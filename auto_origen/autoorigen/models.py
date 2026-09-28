"""Acceso a datos: una función por operación, sobre las tablas definidas en db.py."""
import re
import secrets
from datetime import datetime, timezone

from .db import get_db

# Sin 0/O/1/I/L ni vocales que puedan formar palabras raras al leerlas en
# voz alta — es un código que el taller dicta o escribe en un recibo.
ALFABETO_CODIGO_ACCESO = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"


def _ahora():
    return datetime.now(timezone.utc).isoformat()


def normalizar_placa(placa):
    return re.sub(r"[^A-Z0-9]", "", (placa or "").upper())


def generar_codigo_acceso(longitud=8):
    return "".join(secrets.choice(ALFABETO_CODIGO_ACCESO) for _ in range(longitud))


def numero_whatsapp(telefono):
    """Convierte un teléfono guardado (con o sin +57, espacios, guiones...)
    al formato que necesita wa.me: solo dígitos, con código de país. Si el
    número ya viene completo se deja igual; si parece un celular colombiano
    de 10 dígitos sin indicativo, se le antepone 57 (mercado del taller)."""
    digitos = re.sub(r"\D", "", telefono or "")
    if len(digitos) == 10 and digitos.startswith("3"):
        return "57" + digitos
    return digitos


# ---------- Clientes ----------

def crear_cliente(nombre, telefono, email=None):
    db = get_db()
    cur = db.execute(
        "INSERT INTO clientes (nombre, telefono, email, creado_en) VALUES (?, ?, ?, ?)",
        (nombre.strip(), telefono.strip(), (email or "").strip() or None, _ahora()),
    )
    db.commit()
    return cur.lastrowid


def obtener_cliente(cliente_id):
    return get_db().execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,)).fetchone()


def buscar_cliente_por_telefono(telefono):
    return get_db().execute(
        "SELECT * FROM clientes WHERE telefono = ?", (telefono.strip(),)
    ).fetchone()


def listar_clientes():
    return get_db().execute("SELECT * FROM clientes ORDER BY nombre").fetchall()


def actualizar_cliente(cliente_id, nombre, telefono, email=None):
    db = get_db()
    db.execute(
        "UPDATE clientes SET nombre = ?, telefono = ?, email = ? WHERE id = ?",
        (nombre.strip(), telefono.strip(), (email or "").strip() or None, cliente_id),
    )
    db.commit()


def eliminar_cliente(cliente_id):
    db = get_db()
    db.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
    db.commit()


# ---------- Vehículos ----------

def crear_vehiculo(cliente_id, placa, marca=None, modelo=None, anio=None, color=None, combustible=None):
    db = get_db()
    cur = db.execute(
        """INSERT INTO vehiculos (cliente_id, placa, marca, modelo, anio, color, combustible, codigo_acceso, creado_en)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (cliente_id, normalizar_placa(placa), marca, modelo, anio, color, combustible, generar_codigo_acceso(), _ahora()),
    )
    db.commit()
    return cur.lastrowid


def obtener_vehiculo(vehiculo_id):
    return get_db().execute("SELECT * FROM vehiculos WHERE id = ?", (vehiculo_id,)).fetchone()


def obtener_vehiculo_por_placa(placa):
    return get_db().execute(
        "SELECT * FROM vehiculos WHERE placa = ?", (normalizar_placa(placa),)
    ).fetchone()


def obtener_vehiculo_por_placa_y_codigo(placa, codigo_acceso):
    return get_db().execute(
        "SELECT * FROM vehiculos WHERE placa = ? AND codigo_acceso = ?",
        (normalizar_placa(placa), (codigo_acceso or "").strip().upper()),
    ).fetchone()


def regenerar_codigo_acceso(vehiculo_id):
    db = get_db()
    nuevo_codigo = generar_codigo_acceso()
    db.execute("UPDATE vehiculos SET codigo_acceso = ? WHERE id = ?", (nuevo_codigo, vehiculo_id))
    db.commit()
    return nuevo_codigo


def listar_vehiculos():
    return get_db().execute(
        """SELECT vehiculos.*, clientes.nombre AS cliente_nombre, clientes.telefono AS cliente_telefono
           FROM vehiculos JOIN clientes ON clientes.id = vehiculos.cliente_id
           ORDER BY vehiculos.creado_en DESC"""
    ).fetchall()


def listar_vehiculos_por_cliente(cliente_id):
    return get_db().execute(
        "SELECT * FROM vehiculos WHERE cliente_id = ? ORDER BY creado_en DESC", (cliente_id,)
    ).fetchall()


def actualizar_vehiculo(vehiculo_id, placa, marca=None, modelo=None, anio=None, color=None, combustible=None):
    db = get_db()
    db.execute(
        """UPDATE vehiculos SET placa = ?, marca = ?, modelo = ?, anio = ?, color = ?, combustible = ?
           WHERE id = ?""",
        (normalizar_placa(placa), marca, modelo, anio, color, combustible, vehiculo_id),
    )
    db.commit()


def eliminar_vehiculo(vehiculo_id):
    db = get_db()
    db.execute("DELETE FROM vehiculos WHERE id = ?", (vehiculo_id,))
    db.commit()


def upsert_vehiculo_por_placa(placa, cliente_id, marca=None, modelo=None, anio=None, color=None, combustible=None):
    """Usado por la API de la app móvil: crea el vehículo o actualiza sus datos si la placa ya existe."""
    existente = obtener_vehiculo_por_placa(placa)
    if existente:
        actualizar_vehiculo(existente["id"], placa, marca, modelo, anio, color, combustible)
        return existente["id"]
    return crear_vehiculo(cliente_id, placa, marca, modelo, anio, color, combustible)


# ---------- Citas ----------

def crear_cita(cliente_id, tipo, fecha, hora, servicio=None, notas=None, vehiculo_id=None):
    db = get_db()
    cur = db.execute(
        """INSERT INTO citas (cliente_id, vehiculo_id, tipo, fecha, hora, servicio, notas, estado, creado_en)
           VALUES (?, ?, ?, ?, ?, ?, ?, 'pendiente', ?)""",
        (cliente_id, vehiculo_id, tipo, fecha, hora, servicio, notas, _ahora()),
    )
    db.commit()
    return cur.lastrowid


def listar_citas():
    return get_db().execute(
        """SELECT citas.*, clientes.nombre AS cliente_nombre, clientes.telefono AS cliente_telefono,
                  vehiculos.placa AS vehiculo_placa
           FROM citas
           JOIN clientes ON clientes.id = citas.cliente_id
           LEFT JOIN vehiculos ON vehiculos.id = citas.vehiculo_id
           ORDER BY citas.fecha DESC, citas.hora DESC"""
    ).fetchall()


def obtener_cita(cita_id):
    return get_db().execute("SELECT * FROM citas WHERE id = ?", (cita_id,)).fetchone()


def actualizar_estado_cita(cita_id, estado):
    db = get_db()
    db.execute("UPDATE citas SET estado = ? WHERE id = ?", (estado, cita_id))
    db.commit()


def eliminar_cita(cita_id):
    db = get_db()
    db.execute("DELETE FROM citas WHERE id = ?", (cita_id,))
    db.commit()


# ---------- Órdenes (hoja de vida / proceso del vehículo) ----------

def crear_orden(vehiculo_id, titulo, kilometraje=None, kilometraje_aceite=None, tecnico_id=None):
    db = get_db()
    ahora = _ahora()
    cur = db.execute(
        """INSERT INTO ordenes
           (vehiculo_id, titulo, estado_actual, kilometraje, kilometraje_aceite, tecnico_id, creado_en, actualizado_en)
           VALUES (?, ?, 'recibido', ?, ?, ?, ?, ?)""",
        (vehiculo_id, titulo, kilometraje, kilometraje_aceite, tecnico_id, ahora, ahora),
    )
    db.commit()
    orden_id = cur.lastrowid
    crear_evento(orden_id, "cambio_estado", "Vehículo recibido", "El proceso Entender → Diagnosticar → Explicar → Reparar → Verificar → Documentar comienza aquí.")
    return orden_id


def obtener_orden(orden_id):
    return get_db().execute("SELECT * FROM ordenes WHERE id = ?", (orden_id,)).fetchone()


def listar_ordenes_por_vehiculo(vehiculo_id):
    return get_db().execute(
        "SELECT * FROM ordenes WHERE vehiculo_id = ? ORDER BY creado_en DESC", (vehiculo_id,)
    ).fetchall()


def orden_activa_por_vehiculo(vehiculo_id):
    return get_db().execute(
        """SELECT * FROM ordenes WHERE vehiculo_id = ? AND estado_actual != 'listo'
           ORDER BY creado_en DESC LIMIT 1""",
        (vehiculo_id,),
    ).fetchone()


def listar_ordenes():
    return get_db().execute(
        """SELECT ordenes.*, vehiculos.placa AS vehiculo_placa, vehiculos.id AS vehiculo_id
           FROM ordenes JOIN vehiculos ON vehiculos.id = ordenes.vehiculo_id
           ORDER BY ordenes.actualizado_en DESC"""
    ).fetchall()


def actualizar_estado_orden(orden_id, estado):
    db = get_db()
    db.execute(
        "UPDATE ordenes SET estado_actual = ?, actualizado_en = ? WHERE id = ?",
        (estado, _ahora(), orden_id),
    )
    db.commit()


# ---------- Eventos de la línea de tiempo ----------

def crear_evento(orden_id, tipo, titulo, descripcion=None, medio_path=None, creado_por="admin"):
    db = get_db()
    cur = db.execute(
        """INSERT INTO eventos_timeline (orden_id, tipo, titulo, descripcion, medio_path, creado_por, creado_en)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (orden_id, tipo, titulo, descripcion, medio_path, creado_por, _ahora()),
    )
    db.commit()
    return get_db().execute(
        "SELECT * FROM eventos_timeline WHERE id = ?", (cur.lastrowid,)
    ).fetchone()


def listar_eventos_por_orden(orden_id):
    return get_db().execute(
        "SELECT * FROM eventos_timeline WHERE orden_id = ? ORDER BY creado_en ASC", (orden_id,)
    ).fetchall()


TIPOS_EVENTO_TEXTO = (
    "nota", "hallazgo", "observacion_mecanico", "comentario_cliente", "cambio_estado",
)


def listar_eventos_texto_por_orden(orden_id):
    """Eventos con contenido de texto (sin fotos/video) — es el contexto que se le
    pasa a la IA para redactar los informes; nunca incluye nada que no haya escrito
    alguien del taller o el cliente."""
    marcadores = ",".join("?" * len(TIPOS_EVENTO_TEXTO))
    return get_db().execute(
        f"""SELECT * FROM eventos_timeline
            WHERE orden_id = ? AND tipo IN ({marcadores})
            ORDER BY creado_en ASC""",
        (orden_id, *TIPOS_EVENTO_TEXTO),
    ).fetchall()


# ---------- Medios (fotos / video) ----------

def guardar_medio(orden_id, tipo, archivo_path, evento_id=None):
    db = get_db()
    cur = db.execute(
        """INSERT INTO medios (orden_id, evento_id, tipo, archivo_path, creado_en)
           VALUES (?, ?, ?, ?, ?)""",
        (orden_id, evento_id, tipo, archivo_path, _ahora()),
    )
    db.commit()
    return cur.lastrowid


def listar_medios_por_vehiculo(vehiculo_id):
    return get_db().execute(
        """SELECT medios.* FROM medios
           JOIN ordenes ON ordenes.id = medios.orden_id
           WHERE ordenes.vehiculo_id = ?
           ORDER BY medios.creado_en DESC""",
        (vehiculo_id,),
    ).fetchall()


def listar_medios_por_orden(orden_id, tipo=None):
    if tipo:
        return get_db().execute(
            "SELECT * FROM medios WHERE orden_id = ? AND tipo = ? ORDER BY creado_en ASC",
            (orden_id, tipo),
        ).fetchall()
    return get_db().execute(
        "SELECT * FROM medios WHERE orden_id = ? ORDER BY creado_en ASC", (orden_id,)
    ).fetchall()


# ---------- Admins ----------

def crear_admin(usuario, password_hash, rol="admin"):
    db = get_db()
    cur = db.execute(
        "INSERT INTO admins (usuario, password_hash, rol, creado_en) VALUES (?, ?, ?, ?)",
        (usuario.strip(), password_hash, rol, _ahora()),
    )
    db.commit()
    return cur.lastrowid


def obtener_admin(admin_id):
    return get_db().execute("SELECT * FROM admins WHERE id = ?", (admin_id,)).fetchone()


def obtener_admin_por_usuario(usuario):
    return get_db().execute(
        "SELECT * FROM admins WHERE usuario = ?", (usuario.strip(),)
    ).fetchone()


def listar_admins():
    return get_db().execute("SELECT * FROM admins ORDER BY usuario").fetchall()


def actualizar_password_admin(admin_id, password_hash):
    db = get_db()
    db.execute("UPDATE admins SET password_hash = ? WHERE id = ?", (password_hash, admin_id))
    db.commit()


def eliminar_admin(admin_id):
    db = get_db()
    db.execute("DELETE FROM admins WHERE id = ?", (admin_id,))
    db.commit()


def contar_admins():
    return get_db().execute("SELECT COUNT(*) AS n FROM admins").fetchone()["n"]


# ---------- Mecánicos (login de la app Android) ----------

def crear_mecanico(usuario, password_hash, nombre):
    db = get_db()
    cur = db.execute(
        "INSERT INTO mecanicos (usuario, password_hash, nombre, creado_en) VALUES (?, ?, ?, ?)",
        (usuario.strip(), password_hash, nombre.strip(), _ahora()),
    )
    db.commit()
    return cur.lastrowid


def obtener_mecanico(mecanico_id):
    return get_db().execute("SELECT * FROM mecanicos WHERE id = ?", (mecanico_id,)).fetchone()


def obtener_mecanico_por_usuario(usuario):
    return get_db().execute(
        "SELECT * FROM mecanicos WHERE usuario = ?", (usuario.strip(),)
    ).fetchone()


def listar_mecanicos():
    return get_db().execute("SELECT * FROM mecanicos ORDER BY nombre").fetchall()


def actualizar_password_mecanico(mecanico_id, password_hash):
    db = get_db()
    db.execute("UPDATE mecanicos SET password_hash = ? WHERE id = ?", (password_hash, mecanico_id))
    db.commit()


def eliminar_mecanico(mecanico_id):
    db = get_db()
    db.execute("DELETE FROM mecanicos WHERE id = ?", (mecanico_id,))
    db.commit()


def contar_mecanicos():
    return get_db().execute("SELECT COUNT(*) AS n FROM mecanicos").fetchone()["n"]


# ---------- Inspecciones (app Android) ----------

def crear_inspeccion_completa(
    placa, cliente_nombre, cliente_telefono, marca, modelo, combustible,
    kilometraje, kilometraje_aceite, tecnico_id,
):
    """Primera acción de 'Nueva inspección' en la app: registra el carro
    (por placa) y abre la orden con los kilometrajes de esta visita."""
    cliente = buscar_cliente_por_telefono(cliente_telefono)
    cliente_id = cliente["id"] if cliente else crear_cliente(cliente_nombre, cliente_telefono)

    vehiculo_id = upsert_vehiculo_por_placa(placa, cliente_id, marca, modelo, combustible=combustible)

    titulo = f"Inspección {placa} — {_ahora()[:10]}"
    orden_id = crear_orden(
        vehiculo_id, titulo,
        kilometraje=kilometraje, kilometraje_aceite=kilometraje_aceite, tecnico_id=tecnico_id,
    )
    return orden_id, vehiculo_id


def listar_ordenes_resumen():
    """Para 'Revisión de inspecciones anteriores' en la app: todas las
    inspecciones, de más reciente a más antigua, en solo lectura."""
    return get_db().execute(
        """SELECT ordenes.*, vehiculos.placa AS vehiculo_placa, vehiculos.marca, vehiculos.modelo,
                  clientes.nombre AS cliente_nombre, mecanicos.nombre AS tecnico_nombre
           FROM ordenes
           JOIN vehiculos ON vehiculos.id = ordenes.vehiculo_id
           JOIN clientes ON clientes.id = vehiculos.cliente_id
           LEFT JOIN mecanicos ON mecanicos.id = ordenes.tecnico_id
           ORDER BY ordenes.creado_en DESC"""
    ).fetchall()


def obtener_orden_detalle(orden_id):
    """Ficha completa de una inspección (vehículo + cliente + técnico) para el
    detalle de solo lectura en la app y en la web."""
    return get_db().execute(
        """SELECT ordenes.*, vehiculos.placa AS vehiculo_placa, vehiculos.marca, vehiculos.modelo,
                  vehiculos.anio, vehiculos.color, vehiculos.combustible,
                  clientes.nombre AS cliente_nombre, clientes.telefono AS cliente_telefono,
                  mecanicos.nombre AS tecnico_nombre
           FROM ordenes
           JOIN vehiculos ON vehiculos.id = ordenes.vehiculo_id
           JOIN clientes ON clientes.id = vehiculos.cliente_id
           LEFT JOIN mecanicos ON mecanicos.id = ordenes.tecnico_id
           WHERE ordenes.id = ?""",
        (orden_id,),
    ).fetchone()


# ---------- Tokens de la API móvil ----------

def crear_api_token(nombre_dispositivo, token_hash):
    db = get_db()
    cur = db.execute(
        "INSERT INTO api_tokens (nombre_dispositivo, token_hash, creado_en) VALUES (?, ?, ?)",
        (nombre_dispositivo.strip(), token_hash, _ahora()),
    )
    db.commit()
    return cur.lastrowid


def obtener_api_token_por_hash(token_hash):
    return get_db().execute(
        "SELECT * FROM api_tokens WHERE token_hash = ? AND activo = 1", (token_hash,)
    ).fetchone()


def listar_api_tokens():
    return get_db().execute("SELECT * FROM api_tokens ORDER BY creado_en DESC").fetchall()


def revocar_api_token(token_id):
    db = get_db()
    db.execute("UPDATE api_tokens SET activo = 0 WHERE id = ?", (token_id,))
    db.commit()


# ---------- Informes (IA: preliminar y final) ----------

def crear_informe(orden_id, tipo, contenido):
    db = get_db()
    cur = db.execute(
        """INSERT INTO informes (orden_id, tipo, contenido, estado, creado_en)
           VALUES (?, ?, ?, 'generado', ?)""",
        (orden_id, tipo, contenido, _ahora()),
    )
    db.commit()
    return obtener_informe(cur.lastrowid)


def obtener_informe(informe_id):
    return get_db().execute("SELECT * FROM informes WHERE id = ?", (informe_id,)).fetchone()


def ultimo_informe_por_orden(orden_id, tipo):
    return get_db().execute(
        """SELECT * FROM informes WHERE orden_id = ? AND tipo = ?
           ORDER BY creado_en DESC LIMIT 1""",
        (orden_id, tipo),
    ).fetchone()


def listar_informes_pendientes():
    """Informes finales esperando revisión del jefe de taller (superadmin)."""
    return get_db().execute(
        """SELECT informes.*, ordenes.titulo AS orden_titulo, vehiculos.placa AS vehiculo_placa,
                  vehiculos.id AS vehiculo_id, clientes.nombre AS cliente_nombre
           FROM informes
           JOIN ordenes ON ordenes.id = informes.orden_id
           JOIN vehiculos ON vehiculos.id = ordenes.vehiculo_id
           JOIN clientes ON clientes.id = vehiculos.cliente_id
           WHERE informes.tipo = 'final' AND informes.estado = 'generado'
           ORDER BY informes.creado_en ASC"""
    ).fetchall()


def aprobar_informe(informe_id, admin_id):
    db = get_db()
    db.execute(
        """UPDATE informes SET estado = 'aprobado', aprobado_por = ?, revisado_en = ?
           WHERE id = ?""",
        (admin_id, _ahora(), informe_id),
    )
    db.commit()


def rechazar_informe(informe_id, admin_id, comentario):
    db = get_db()
    db.execute(
        """UPDATE informes SET estado = 'rechazado', aprobado_por = ?, comentario_supervisor = ?, revisado_en = ?
           WHERE id = ?""",
        (admin_id, comentario, _ahora(), informe_id),
    )
    db.commit()


# ---------- Contacto (formulario original) ----------

def crear_contacto(nombre, telefono, tipo, marca, modelo, anio, problema, mensaje):
    db = get_db()
    db.execute(
        """INSERT INTO contactos (nombre, telefono, tipo, marca, modelo, anio, problema, mensaje, creado_en)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (nombre, telefono, tipo, marca, modelo, anio, problema, mensaje, _ahora()),
    )
    db.commit()
