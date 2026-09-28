import uuid
from functools import wraps
from pathlib import Path
from urllib.parse import quote

from flask import (Blueprint, abort, current_app, flash, redirect,
                    render_template, request, send_from_directory, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from .. import ia, models
from ..auth import AdminUser
from ..extensions import socketio
from ..sockets import emitir_nuevo_evento

admin_bp = Blueprint("admin", __name__)

EXTENSIONES_FOTO = {"jpg", "jpeg", "png", "heic", "webp"}
EXTENSIONES_VIDEO = {"mp4", "mov", "m4v", "webm"}


def solo_superadmin(vista):
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if not current_user.es_superadmin:
            abort(403)
        return vista(*args, **kwargs)
    return envoltura


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        usuario = (request.form.get("usuario") or "").strip()
        password = request.form.get("password") or ""
        row = models.obtener_admin_por_usuario(usuario)
        if row and check_password_hash(row["password_hash"], password):
            login_user(AdminUser(row))
            return redirect(url_for("admin.dashboard"))
        error = "Usuario o contraseña incorrectos."
    return render_template("admin/login.html", error=error)


@admin_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("admin.login"))


@admin_bp.route("/")
@login_required
def dashboard():
    citas = models.listar_citas()
    ordenes = models.listar_ordenes()
    citas_pendientes = [c for c in citas if c["estado"] == "pendiente"]
    ordenes_activas = [o for o in ordenes if o["estado_actual"] != "listo"]
    return render_template(
        "admin/dashboard.html",
        citas_pendientes=citas_pendientes, ordenes_activas=ordenes_activas,
        total_clientes=len(models.listar_clientes()), total_vehiculos=len(models.listar_vehiculos()),
        total_informes_pendientes=len(models.listar_informes_pendientes()),
    )


# ---------- Clientes ----------

@admin_bp.route("/clientes", methods=["GET", "POST"])
@login_required
def clientes():
    if request.method == "POST":
        nombre = (request.form.get("nombre") or "").strip()
        telefono = (request.form.get("telefono") or "").strip()
        email = (request.form.get("email") or "").strip()
        if nombre and telefono:
            models.crear_cliente(nombre, telefono, email)
            flash("Cliente creado.", "ok")
        return redirect(url_for("admin.clientes"))
    return render_template("admin/clientes.html", clientes=models.listar_clientes())


@admin_bp.route("/clientes/<int:cliente_id>/editar", methods=["POST"])
@login_required
def editar_cliente(cliente_id):
    nombre = (request.form.get("nombre") or "").strip()
    telefono = (request.form.get("telefono") or "").strip()
    email = (request.form.get("email") or "").strip()
    if nombre and telefono:
        models.actualizar_cliente(cliente_id, nombre, telefono, email)
        flash("Cliente actualizado.", "ok")
    return redirect(url_for("admin.clientes"))


@admin_bp.route("/clientes/<int:cliente_id>/eliminar", methods=["POST"])
@login_required
def eliminar_cliente(cliente_id):
    models.eliminar_cliente(cliente_id)
    flash("Cliente eliminado.", "ok")
    return redirect(url_for("admin.clientes"))


# ---------- Vehículos ----------

@admin_bp.route("/vehiculos", methods=["GET", "POST"])
@login_required
def vehiculos():
    if request.method == "POST":
        cliente_id = request.form.get("cliente_id", type=int)
        placa = (request.form.get("placa") or "").strip()
        marca = (request.form.get("marca") or "").strip()
        modelo = (request.form.get("modelo") or "").strip()
        anio = (request.form.get("anio") or "").strip()
        color = (request.form.get("color") or "").strip()
        if cliente_id and placa:
            models.crear_vehiculo(cliente_id, placa, marca, modelo, anio, color)
            flash("Vehículo creado.", "ok")
        return redirect(url_for("admin.vehiculos"))
    return render_template(
        "admin/vehiculos.html", vehiculos=models.listar_vehiculos(), clientes=models.listar_clientes(),
    )


@admin_bp.route("/vehiculos/<int:vehiculo_id>/eliminar", methods=["POST"])
@login_required
def eliminar_vehiculo(vehiculo_id):
    models.eliminar_vehiculo(vehiculo_id)
    flash("Vehículo eliminado.", "ok")
    return redirect(url_for("admin.vehiculos"))


@admin_bp.route("/vehiculos/<int:vehiculo_id>")
@login_required
def vehiculo_detalle(vehiculo_id):
    vehiculo = models.obtener_vehiculo(vehiculo_id)
    if not vehiculo:
        abort(404)
    cliente = models.obtener_cliente(vehiculo["cliente_id"])
    ordenes = models.listar_ordenes_por_vehiculo(vehiculo_id)
    medios = models.listar_medios_por_vehiculo(vehiculo_id)

    mensaje_whatsapp = (
        f"Hola {cliente['nombre']}, tu código de acceso para ver el estado de tu "
        f"{vehiculo['placa']} en Autoorigen es: {vehiculo['codigo_acceso']}. "
        f"Entra a {url_for('historial.buscar', _external=True)} y pon la placa y este código."
    )
    link_whatsapp = f"https://wa.me/{models.numero_whatsapp(cliente['telefono'])}?text={quote(mensaje_whatsapp)}"

    return render_template(
        "admin/vehiculo_detalle.html", vehiculo=vehiculo, cliente=cliente, ordenes=ordenes, medios=medios,
        link_whatsapp=link_whatsapp,
    )


@admin_bp.route("/vehiculos/<int:vehiculo_id>/ordenes", methods=["POST"])
@login_required
def crear_orden(vehiculo_id):
    titulo = (request.form.get("titulo") or "").strip() or "Orden de trabajo"
    models.crear_orden(vehiculo_id, titulo)
    flash("Orden creada.", "ok")
    return redirect(url_for("admin.vehiculo_detalle", vehiculo_id=vehiculo_id))


@admin_bp.route("/vehiculos/<int:vehiculo_id>/regenerar-codigo", methods=["POST"])
@login_required
def regenerar_codigo_vehiculo(vehiculo_id):
    if not models.obtener_vehiculo(vehiculo_id):
        abort(404)
    models.regenerar_codigo_acceso(vehiculo_id)
    flash("Código de acceso regenerado. El código anterior dejó de funcionar.", "ok")
    return redirect(url_for("admin.vehiculo_detalle", vehiculo_id=vehiculo_id))


# ---------- Órdenes / línea de tiempo ----------

def _extension_valida(nombre_archivo):
    ext = nombre_archivo.rsplit(".", 1)[-1].lower() if "." in nombre_archivo else ""
    if ext in EXTENSIONES_FOTO:
        return "foto", ext
    if ext in EXTENSIONES_VIDEO:
        return "video", ext
    return None, None


@admin_bp.route("/ordenes/<int:orden_id>")
@login_required
def orden_detalle(orden_id):
    orden = models.obtener_orden_detalle(orden_id)
    if not orden:
        abort(404)
    vehiculo = models.obtener_vehiculo(orden["vehiculo_id"])
    eventos = models.listar_eventos_por_orden(orden_id)
    etapas = ["recibido", "diagnosticando", "diagnosticado", "reparando", "verificando", "listo"]
    return render_template(
        "admin/orden_detalle.html", orden=orden, vehiculo=vehiculo, eventos=eventos, etapas=etapas,
    )


@admin_bp.route("/ordenes/<int:orden_id>/estado", methods=["POST"])
@login_required
def cambiar_estado_orden(orden_id):
    orden = models.obtener_orden(orden_id)
    if not orden:
        abort(404)
    estado = request.form.get("estado")
    etapas = ["recibido", "diagnosticando", "diagnosticado", "reparando", "verificando", "listo"]
    if estado in etapas:
        models.actualizar_estado_orden(orden_id, estado)
        evento = models.crear_evento(
            orden_id, "cambio_estado", f"Etapa: {estado.capitalize()}",
            request.form.get("nota") or None, creado_por="admin",
        )
        emitir_nuevo_evento(orden["vehiculo_id"], evento, models.obtener_orden(orden_id))

        if estado in ("reparando", "listo"):
            app_real = current_app._get_current_object()
            socketio.start_background_task(ia.procesar_cambio_de_etapa, app_real, orden_id, estado)
            etiqueta = "informe preliminar" if estado == "reparando" else "informe final"
            flash(f"Estado actualizado. Generando el {etiqueta} con IA en segundo plano…", "ok")
        else:
            flash("Estado actualizado.", "ok")
    return redirect(url_for("admin.orden_detalle", orden_id=orden_id))


@admin_bp.route("/ordenes/<int:orden_id>/eventos", methods=["POST"])
@login_required
def agregar_evento(orden_id):
    orden = models.obtener_orden(orden_id)
    if not orden:
        abort(404)

    tipo = request.form.get("tipo") or "nota"
    titulo = (request.form.get("titulo") or "").strip()
    descripcion = (request.form.get("descripcion") or "").strip()
    if not titulo:
        flash("El evento necesita un título.", "error")
        return redirect(url_for("admin.orden_detalle", orden_id=orden_id))

    medio_path = None
    archivo = request.files.get("archivo")
    if archivo and archivo.filename:
        tipo_medio, ext = _extension_valida(archivo.filename)
        if not tipo_medio:
            flash("Formato de archivo no permitido.", "error")
            return redirect(url_for("admin.orden_detalle", orden_id=orden_id))
        carpeta = Path(current_app.config["UPLOAD_DIR"]) / str(orden["vehiculo_id"])
        carpeta.mkdir(parents=True, exist_ok=True)
        nombre_final = f"{uuid.uuid4().hex}.{ext}"
        archivo.save(carpeta / secure_filename(nombre_final))
        medio_path = f"{orden['vehiculo_id']}/{nombre_final}"
        tipo = tipo_medio

    evento = models.crear_evento(orden_id, tipo, titulo, descripcion or None, medio_path, creado_por="admin")

    if medio_path:
        models.guardar_medio(orden_id, tipo, medio_path, evento_id=evento["id"])

    emitir_nuevo_evento(orden["vehiculo_id"], evento, orden)
    flash("Evento agregado a la línea de tiempo.", "ok")
    return redirect(url_for("admin.orden_detalle", orden_id=orden_id))


@admin_bp.route("/medios/<path:ruta>")
@login_required
def ver_medio(ruta):
    return send_from_directory(current_app.config["UPLOAD_DIR"], ruta)


# ---------- Informes (IA) ----------

@admin_bp.route("/informes")
@login_required
@solo_superadmin
def informes():
    return render_template("admin/informes.html", informes=models.listar_informes_pendientes())


@admin_bp.route("/informes/<int:informe_id>/aprobar", methods=["POST"])
@login_required
@solo_superadmin
def aprobar_informe(informe_id):
    informe = models.obtener_informe(informe_id)
    if not informe:
        abort(404)
    orden = models.obtener_orden(informe["orden_id"])
    models.aprobar_informe(informe_id, int(current_user.id))
    evento = models.crear_evento(
        informe["orden_id"], "informe", "Informe final de la reparación",
        informe["contenido"], creado_por="admin",
    )
    emitir_nuevo_evento(orden["vehiculo_id"], evento, models.obtener_orden(informe["orden_id"]))
    flash("Informe aprobado y publicado para el cliente.", "ok")
    return redirect(url_for("admin.informes"))


@admin_bp.route("/informes/<int:informe_id>/rechazar", methods=["POST"])
@login_required
@solo_superadmin
def rechazar_informe(informe_id):
    if not models.obtener_informe(informe_id):
        abort(404)
    comentario = (request.form.get("comentario") or "").strip()
    models.rechazar_informe(informe_id, int(current_user.id), comentario or None)
    flash("Informe rechazado. Se puede regenerar desde la orden cuando haya más evidencia.", "ok")
    return redirect(url_for("admin.informes"))


@admin_bp.route("/ordenes/<int:orden_id>/regenerar-informe-final", methods=["POST"])
@login_required
@solo_superadmin
def regenerar_informe_final(orden_id):
    if not models.obtener_orden(orden_id):
        abort(404)
    app_real = current_app._get_current_object()
    socketio.start_background_task(ia.procesar_cambio_de_etapa, app_real, orden_id, "listo")
    flash("Regenerando el informe final con IA en segundo plano…", "ok")
    return redirect(url_for("admin.orden_detalle", orden_id=orden_id))


# ---------- Citas ----------

@admin_bp.route("/citas")
@login_required
def citas():
    return render_template("admin/citas.html", citas=models.listar_citas())


@admin_bp.route("/citas/<int:cita_id>/estado", methods=["POST"])
@login_required
def cambiar_estado_cita(cita_id):
    estado = request.form.get("estado")
    if estado in ("pendiente", "confirmada", "cancelada", "completada"):
        models.actualizar_estado_cita(cita_id, estado)
        flash("Cita actualizada.", "ok")
    return redirect(url_for("admin.citas"))


@admin_bp.route("/citas/<int:cita_id>/eliminar", methods=["POST"])
@login_required
def eliminar_cita(cita_id):
    models.eliminar_cita(cita_id)
    flash("Cita eliminada.", "ok")
    return redirect(url_for("admin.citas"))


# ---------- Usuarios admin ----------

@admin_bp.route("/usuarios", methods=["GET", "POST"])
@login_required
@solo_superadmin
def usuarios():
    if request.method == "POST":
        usuario = (request.form.get("usuario") or "").strip()
        password = request.form.get("password") or ""
        rol = request.form.get("rol") or "admin"
        if usuario and len(password) >= 8:
            models.crear_admin(usuario, generate_password_hash(password), rol)
            flash("Usuario admin creado.", "ok")
        else:
            flash("El usuario necesita nombre y una contraseña de al menos 8 caracteres.", "error")
        return redirect(url_for("admin.usuarios"))
    return render_template("admin/usuarios.html", usuarios=models.listar_admins())


@admin_bp.route("/usuarios/<int:admin_id>/eliminar", methods=["POST"])
@login_required
@solo_superadmin
def eliminar_usuario(admin_id):
    if str(admin_id) == current_user.id:
        flash("No puedes eliminar tu propio usuario.", "error")
    else:
        models.eliminar_admin(admin_id)
        flash("Usuario eliminado.", "ok")
    return redirect(url_for("admin.usuarios"))


# ---------- Mecánicos (login de la app Android) ----------

@admin_bp.route("/mecanicos", methods=["GET", "POST"])
@login_required
@solo_superadmin
def mecanicos():
    if request.method == "POST":
        usuario = (request.form.get("usuario") or "").strip()
        nombre = (request.form.get("nombre") or "").strip()
        password = request.form.get("password") or ""
        if usuario and nombre and len(password) >= 8:
            models.crear_mecanico(usuario, generate_password_hash(password), nombre)
            flash("Mecánico creado.", "ok")
        else:
            flash("Usuario, nombre y una contraseña de al menos 8 caracteres son obligatorios.", "error")
        return redirect(url_for("admin.mecanicos"))
    return render_template("admin/mecanicos.html", mecanicos=models.listar_mecanicos())


@admin_bp.route("/mecanicos/<int:mecanico_id>/eliminar", methods=["POST"])
@login_required
@solo_superadmin
def eliminar_mecanico(mecanico_id):
    models.eliminar_mecanico(mecanico_id)
    flash("Mecánico eliminado.", "ok")
    return redirect(url_for("admin.mecanicos"))


# ---------- Tokens de la API móvil ----------

@admin_bp.route("/api-tokens", methods=["GET", "POST"])
@login_required
@solo_superadmin
def api_tokens():
    token_generado = None
    if request.method == "POST":
        import hashlib
        import secrets

        nombre = (request.form.get("nombre_dispositivo") or "").strip()
        if nombre:
            token_generado = secrets.token_urlsafe(32)
            models.crear_api_token(nombre, hashlib.sha256(token_generado.encode()).hexdigest())
    return render_template(
        "admin/api_tokens.html", tokens=models.listar_api_tokens(), token_generado=token_generado,
    )


@admin_bp.route("/api-tokens/<int:token_id>/revocar", methods=["POST"])
@login_required
@solo_superadmin
def revocar_api_token(token_id):
    models.revocar_api_token(token_id)
    flash("Token revocado.", "ok")
    return redirect(url_for("admin.api_tokens"))
