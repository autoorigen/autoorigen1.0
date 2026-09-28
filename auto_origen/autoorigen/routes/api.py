"""API REST para las apps móviles.

Hay dos formas de autenticación, para dos clientes distintos:

1. Token de dispositivo (`Authorization: Bearer <token>` generado desde
   /admin/api-tokens) — pensado para la futura app iOS AutoorigenInspect.
   Ver app-ios/README.md para el contrato completo.
2. Login de mecánico (`POST /api/tecnicos/login` con usuario/contraseña,
   devuelve un token firmado) — usado por la app Android de inspecciones.
"""
import hashlib
import uuid
from functools import wraps
from pathlib import Path

from flask import Blueprint, current_app, g, jsonify, request, send_from_directory
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

from .. import models
from ..routes.admin import EXTENSIONES_FOTO, EXTENSIONES_VIDEO
from ..sockets import emitir_nuevo_evento

api_bp = Blueprint("api", __name__)

TECNICO_TOKEN_SALT = "tecnico-app-android"
TECNICO_TOKEN_TTL_SEGUNDOS = 12 * 60 * 60


def _serializador_tecnico():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt=TECNICO_TOKEN_SALT)


def _guardar_archivo_subido(vehiculo_id, archivo):
    """Guarda una foto/video en data/uploads/<vehiculo_id>/ y devuelve (tipo, medio_path).
    Lanza ValueError si el archivo no tiene una extensión permitida."""
    ext = archivo.filename.rsplit(".", 1)[-1].lower() if "." in archivo.filename else ""
    if ext in EXTENSIONES_FOTO:
        tipo = "foto"
    elif ext in EXTENSIONES_VIDEO:
        tipo = "video"
    else:
        raise ValueError("Formato de archivo no permitido.")

    carpeta = Path(current_app.config["UPLOAD_DIR"]) / str(vehiculo_id)
    carpeta.mkdir(parents=True, exist_ok=True)
    nombre_final = f"{uuid.uuid4().hex}.{ext}"
    archivo.save(carpeta / secure_filename(nombre_final))
    return tipo, f"{vehiculo_id}/{nombre_final}"


# ========================================================================
# Autenticación por token de dispositivo (app iOS futura)
# ========================================================================

def requiere_token(vista):
    @wraps(vista)
    def envoltura(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify(ok=False, error="Falta el token de autorización."), 401
        token_hash = hashlib.sha256(auth[7:].encode()).hexdigest()
        dispositivo = models.obtener_api_token_por_hash(token_hash)
        if not dispositivo:
            return jsonify(ok=False, error="Token inválido o revocado."), 401
        g.dispositivo = dispositivo
        return vista(*args, **kwargs)
    return envoltura


@api_bp.route("/vehiculos", methods=["POST"])
@requiere_token
def upsert_vehiculo():
    data = request.get_json(silent=True) or {}
    placa = (data.get("placa") or "").strip()
    telefono = (data.get("cliente_telefono") or "").strip()
    nombre_cliente = (data.get("cliente_nombre") or "").strip()

    if not placa or not telefono or not nombre_cliente:
        return jsonify(ok=False, error="placa, cliente_nombre y cliente_telefono son obligatorios."), 400

    cliente = models.buscar_cliente_por_telefono(telefono)
    cliente_id = cliente["id"] if cliente else models.crear_cliente(nombre_cliente, telefono)

    vehiculo_id = models.upsert_vehiculo_por_placa(
        placa, cliente_id, data.get("marca"), data.get("modelo"), data.get("anio"), data.get("color"),
    )
    return jsonify(ok=True, vehiculo_id=vehiculo_id)


@api_bp.route("/ordenes", methods=["POST"])
@requiere_token
def crear_orden():
    data = request.get_json(silent=True) or {}
    vehiculo_id = data.get("vehiculo_id")
    titulo = (data.get("titulo") or "Inspección AutoorigenInspect").strip()

    if not vehiculo_id or not models.obtener_vehiculo(vehiculo_id):
        return jsonify(ok=False, error="vehiculo_id no existe."), 404

    orden_id = models.crear_orden(vehiculo_id, titulo)
    return jsonify(ok=True, orden_id=orden_id)


@api_bp.route("/ordenes/<int:orden_id>/eventos", methods=["POST"])
@requiere_token
def agregar_evento(orden_id):
    orden = models.obtener_orden(orden_id)
    if not orden:
        return jsonify(ok=False, error="Orden no encontrada."), 404

    data = request.get_json(silent=True) or {}
    tipo = data.get("tipo") or "nota"
    titulo = (data.get("titulo") or "").strip()
    if not titulo:
        return jsonify(ok=False, error="titulo es obligatorio."), 400

    evento = models.crear_evento(
        orden_id, tipo, titulo, data.get("descripcion"), creado_por="app_movil",
    )
    emitir_nuevo_evento(orden["vehiculo_id"], evento, orden)
    return jsonify(ok=True, evento_id=evento["id"])


@api_bp.route("/ordenes/<int:orden_id>/medios", methods=["POST"])
@requiere_token
def subir_medio(orden_id):
    orden = models.obtener_orden(orden_id)
    if not orden:
        return jsonify(ok=False, error="Orden no encontrada."), 404

    archivo = request.files.get("archivo")
    if not archivo or not archivo.filename:
        return jsonify(ok=False, error="Falta el archivo."), 400

    try:
        tipo, medio_path = _guardar_archivo_subido(orden["vehiculo_id"], archivo)
    except ValueError as exc:
        return jsonify(ok=False, error=str(exc)), 400

    titulo = (request.form.get("titulo") or ("Foto nueva" if tipo == "foto" else "Video nuevo"))
    evento = models.crear_evento(
        orden_id, tipo, titulo, request.form.get("descripcion"), medio_path, creado_por="app_movil",
    )
    models.guardar_medio(orden_id, tipo, medio_path, evento_id=evento["id"])
    emitir_nuevo_evento(orden["vehiculo_id"], evento, orden)
    return jsonify(ok=True, evento_id=evento["id"], medio_path=medio_path)


@api_bp.route("/medios/<path:ruta>")
@requiere_token
def ver_medio_dispositivo(ruta):
    """Sirve un archivo de data/uploads/ para la app iOS futura (token de dispositivo)."""
    return send_from_directory(current_app.config["UPLOAD_DIR"], ruta)


# ========================================================================
# Login de mecánico + endpoints de la app Android
# ========================================================================

def requiere_tecnico(vista):
    @wraps(vista)
    def envoltura(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify(ok=False, error="Falta el token de autorización."), 401
        try:
            datos = _serializador_tecnico().loads(auth[7:], max_age=TECNICO_TOKEN_TTL_SEGUNDOS)
        except SignatureExpired:
            return jsonify(ok=False, error="La sesión expiró. Vuelve a iniciar sesión."), 401
        except BadSignature:
            return jsonify(ok=False, error="Token inválido."), 401

        mecanico = models.obtener_mecanico(datos.get("mecanico_id"))
        if not mecanico or not mecanico["activo"]:
            return jsonify(ok=False, error="Usuario inactivo o eliminado."), 401
        g.tecnico = mecanico
        return vista(*args, **kwargs)
    return envoltura


@api_bp.route("/tecnicos/login", methods=["POST"])
def login_tecnico():
    data = request.get_json(silent=True) or {}
    usuario = (data.get("usuario") or "").strip()
    password = data.get("password") or ""

    mecanico = models.obtener_mecanico_por_usuario(usuario)
    if not mecanico or not mecanico["activo"] or not check_password_hash(mecanico["password_hash"], password):
        return jsonify(ok=False, error="Usuario o contraseña incorrectos."), 401

    token = _serializador_tecnico().dumps({"mecanico_id": mecanico["id"]})
    return jsonify(ok=True, token=token, tecnico={"id": mecanico["id"], "nombre": mecanico["nombre"]})


def _evento_a_dict(evento):
    return {
        "id": evento["id"], "tipo": evento["tipo"], "titulo": evento["titulo"],
        "descripcion": evento["descripcion"], "medio_path": evento["medio_path"],
        "creado_por": evento["creado_por"], "creado_en": evento["creado_en"],
    }


def _orden_resumen_a_dict(orden):
    return {
        "id": orden["id"], "titulo": orden["titulo"], "estado_actual": orden["estado_actual"],
        "vehiculo_placa": orden["vehiculo_placa"], "marca": orden["marca"], "modelo": orden["modelo"],
        "cliente_nombre": orden["cliente_nombre"], "tecnico_nombre": orden["tecnico_nombre"],
        "creado_en": orden["creado_en"],
    }


@api_bp.route("/inspecciones", methods=["POST"])
@requiere_tecnico
def crear_inspeccion():
    data = request.get_json(silent=True) or {}
    placa = (data.get("placa") or "").strip()
    cliente_nombre = (data.get("cliente_nombre") or "").strip()
    cliente_telefono = (data.get("cliente_telefono") or "").strip()
    combustible = data.get("combustible")

    if not placa or not cliente_nombre or not cliente_telefono:
        return jsonify(ok=False, error="placa, cliente_nombre y cliente_telefono son obligatorios."), 400
    if combustible not in (None, "", "gasolina", "hibrido", "electrico"):
        return jsonify(ok=False, error="combustible debe ser gasolina, hibrido o electrico."), 400

    orden_id, vehiculo_id = models.crear_inspeccion_completa(
        placa, cliente_nombre, cliente_telefono,
        data.get("marca"), data.get("modelo"), combustible or None,
        data.get("kilometraje"), data.get("kilometraje_aceite"),
        g.tecnico["id"],
    )
    vehiculo = models.obtener_vehiculo(vehiculo_id)
    return jsonify(
        ok=True, orden_id=orden_id, vehiculo_id=vehiculo_id,
        codigo_acceso=vehiculo["codigo_acceso"],
    )


@api_bp.route("/inspecciones", methods=["GET"])
@requiere_tecnico
def listar_inspecciones():
    ordenes = models.listar_ordenes_resumen()
    return jsonify(ok=True, inspecciones=[_orden_resumen_a_dict(o) for o in ordenes])


@api_bp.route("/inspecciones/<int:orden_id>", methods=["GET"])
@requiere_tecnico
def detalle_inspeccion(orden_id):
    orden = models.obtener_orden_detalle(orden_id)
    if not orden:
        return jsonify(ok=False, error="Inspección no encontrada."), 404

    eventos = models.listar_eventos_por_orden(orden_id)
    return jsonify(ok=True, inspeccion={
        "id": orden["id"], "titulo": orden["titulo"], "estado_actual": orden["estado_actual"],
        "kilometraje": orden["kilometraje"], "kilometraje_aceite": orden["kilometraje_aceite"],
        "vehiculo_placa": orden["vehiculo_placa"], "marca": orden["marca"], "modelo": orden["modelo"],
        "anio": orden["anio"], "color": orden["color"], "combustible": orden["combustible"],
        "cliente_nombre": orden["cliente_nombre"], "cliente_telefono": orden["cliente_telefono"],
        "tecnico_nombre": orden["tecnico_nombre"], "creado_en": orden["creado_en"],
        "eventos": [_evento_a_dict(e) for e in eventos],
    })


@api_bp.route("/inspecciones/<int:orden_id>/eventos", methods=["POST"])
@requiere_tecnico
def agregar_evento_inspeccion(orden_id):
    orden = models.obtener_orden(orden_id)
    if not orden:
        return jsonify(ok=False, error="Inspección no encontrada."), 404

    data = request.get_json(silent=True) or {}
    tipo = data.get("tipo")
    if tipo not in ("observacion_mecanico", "comentario_cliente", "hallazgo", "nota"):
        return jsonify(ok=False, error="tipo inválido."), 400

    titulo = {
        "observacion_mecanico": "Observación del mecánico",
        "comentario_cliente": "Comentario del cliente",
    }.get(tipo, (data.get("titulo") or "Nota").strip())

    descripcion = (data.get("descripcion") or "").strip()
    if not descripcion:
        return jsonify(ok=False, error="descripcion es obligatoria."), 400

    evento = models.crear_evento(orden_id, tipo, titulo, descripcion, creado_por="app_movil")
    emitir_nuevo_evento(orden["vehiculo_id"], evento, orden)
    return jsonify(ok=True, evento_id=evento["id"])


@api_bp.route("/inspecciones/<int:orden_id>/medios", methods=["POST"])
@requiere_tecnico
def subir_medio_inspeccion(orden_id):
    orden = models.obtener_orden(orden_id)
    if not orden:
        return jsonify(ok=False, error="Inspección no encontrada."), 404

    archivo = request.files.get("archivo")
    if not archivo or not archivo.filename:
        return jsonify(ok=False, error="Falta el archivo."), 400

    try:
        tipo, medio_path = _guardar_archivo_subido(orden["vehiculo_id"], archivo)
    except ValueError as exc:
        return jsonify(ok=False, error=str(exc)), 400

    es_video_ingreso = request.form.get("es_video_ingreso") == "1" and tipo == "video"
    tipo_evento = "video_ingreso" if es_video_ingreso else tipo

    titulo = (request.form.get("titulo") or ("Foto nueva" if tipo == "foto" else "Video nuevo"))
    evento = models.crear_evento(
        orden_id, tipo_evento, titulo, request.form.get("descripcion"), medio_path, creado_por="app_movil",
    )
    models.guardar_medio(orden_id, tipo, medio_path, evento_id=evento["id"])
    emitir_nuevo_evento(orden["vehiculo_id"], evento, orden)
    return jsonify(ok=True, evento_id=evento["id"], medio_path=medio_path)


@api_bp.route("/inspecciones/medios/<path:ruta>")
@requiere_tecnico
def ver_medio_inspeccion(ruta):
    """Sirve una foto/video de data/uploads/ para la app Android (login de mecánico)."""
    return send_from_directory(current_app.config["UPLOAD_DIR"], ruta)
