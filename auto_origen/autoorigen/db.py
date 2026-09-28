import sqlite3

import click
from flask import current_app, g

EVENTOS_TIMELINE_COLUMNAS = """
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    orden_id INTEGER NOT NULL REFERENCES ordenes(id) ON DELETE CASCADE,
    tipo TEXT NOT NULL CHECK (tipo IN (
        'nota', 'cambio_estado', 'hallazgo', 'foto', 'video', 'informe',
        'observacion_mecanico', 'comentario_cliente', 'video_ingreso'
    )),
    titulo TEXT NOT NULL,
    descripcion TEXT,
    medio_path TEXT,
    creado_por TEXT NOT NULL DEFAULT 'admin' CHECK (creado_por IN ('admin', 'app_movil')),
    creado_en TEXT NOT NULL
"""

SCHEMA = f"""
CREATE TABLE IF NOT EXISTS contactos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    telefono TEXT NOT NULL,
    tipo TEXT,
    marca TEXT,
    modelo TEXT,
    anio TEXT,
    problema TEXT,
    mensaje TEXT NOT NULL,
    creado_en TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    telefono TEXT NOT NULL,
    email TEXT,
    creado_en TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_clientes_telefono ON clientes(telefono);

CREATE TABLE IF NOT EXISTS vehiculos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
    placa TEXT NOT NULL UNIQUE,
    marca TEXT,
    modelo TEXT,
    anio TEXT,
    color TEXT,
    combustible TEXT CHECK (combustible IN ('gasolina', 'hibrido', 'electrico')),
    codigo_acceso TEXT,
    creado_en TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS mecanicos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    nombre TEXT NOT NULL,
    activo INTEGER NOT NULL DEFAULT 1,
    creado_en TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS citas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
    vehiculo_id INTEGER REFERENCES vehiculos(id) ON DELETE SET NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('vehiculo', 'visita')),
    fecha TEXT NOT NULL,
    hora TEXT NOT NULL,
    servicio TEXT,
    notas TEXT,
    estado TEXT NOT NULL DEFAULT 'pendiente'
        CHECK (estado IN ('pendiente', 'confirmada', 'cancelada', 'completada')),
    creado_en TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ordenes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehiculo_id INTEGER NOT NULL REFERENCES vehiculos(id) ON DELETE CASCADE,
    tecnico_id INTEGER REFERENCES mecanicos(id) ON DELETE SET NULL,
    titulo TEXT NOT NULL,
    estado_actual TEXT NOT NULL DEFAULT 'recibido'
        CHECK (estado_actual IN (
            'recibido', 'diagnosticando', 'diagnosticado',
            'reparando', 'verificando', 'listo'
        )),
    kilometraje TEXT,
    kilometraje_aceite TEXT,
    creado_en TEXT NOT NULL,
    actualizado_en TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS eventos_timeline ({EVENTOS_TIMELINE_COLUMNAS});

CREATE TABLE IF NOT EXISTS medios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    orden_id INTEGER NOT NULL REFERENCES ordenes(id) ON DELETE CASCADE,
    evento_id INTEGER REFERENCES eventos_timeline(id) ON DELETE SET NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('foto', 'video')),
    archivo_path TEXT NOT NULL,
    creado_en TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    rol TEXT NOT NULL DEFAULT 'admin' CHECK (rol IN ('admin', 'superadmin')),
    creado_en TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS api_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_dispositivo TEXT NOT NULL,
    token_hash TEXT NOT NULL UNIQUE,
    activo INTEGER NOT NULL DEFAULT 1,
    creado_en TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS informes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    orden_id INTEGER NOT NULL REFERENCES ordenes(id) ON DELETE CASCADE,
    tipo TEXT NOT NULL CHECK (tipo IN ('preliminar', 'final')),
    contenido TEXT NOT NULL,
    estado TEXT NOT NULL DEFAULT 'generado' CHECK (estado IN ('generado', 'aprobado', 'rechazado')),
    aprobado_por INTEGER REFERENCES admins(id) ON DELETE SET NULL,
    comentario_supervisor TEXT,
    creado_en TEXT NOT NULL,
    revisado_en TEXT
);
"""


def get_db():
    if "db" not in g:
        db_path = current_app.config["DB_PATH"]
        db_path.parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def _columnas(db, tabla):
    return {fila["name"] for fila in db.execute(f"PRAGMA table_info({tabla})")}


def _agregar_columna_si_falta(db, tabla, columna, definicion):
    if columna not in _columnas(db, tabla):
        db.execute(f"ALTER TABLE {tabla} ADD COLUMN {columna} {definicion}")


def migrate_schema(db):
    """Ajusta una base de datos que ya existía antes de estos campos nuevos,
    sin borrar nada. Se ejecuta en cada arranque; es segura de repetir."""
    _agregar_columna_si_falta(
        db, "vehiculos", "combustible",
        "TEXT CHECK (combustible IN ('gasolina', 'hibrido', 'electrico'))",
    )
    _agregar_columna_si_falta(db, "vehiculos", "codigo_acceso", "TEXT")
    _agregar_columna_si_falta(
        db, "ordenes", "tecnico_id", "INTEGER REFERENCES mecanicos(id) ON DELETE SET NULL",
    )
    _agregar_columna_si_falta(db, "ordenes", "kilometraje", "TEXT")
    _agregar_columna_si_falta(db, "ordenes", "kilometraje_aceite", "TEXT")

    # Vehículos que ya existían antes del código de acceso (o que quedaron
    # sin uno por alguna razón): se les genera uno para que "Historia
    # mecánica del vehículo" siga funcionando para ellos.
    sin_codigo = db.execute(
        "SELECT id FROM vehiculos WHERE codigo_acceso IS NULL OR codigo_acceso = ''"
    ).fetchall()
    if sin_codigo:
        from . import models  # import diferido: models importa db, evita ciclo

        for fila in sin_codigo:
            db.execute(
                "UPDATE vehiculos SET codigo_acceso = ? WHERE id = ?",
                (models.generar_codigo_acceso(), fila["id"]),
            )
        db.commit()

    # otp_codigos (verificación por SMS) se reemplazó por el código de
    # acceso por vehículo: la tabla ya no se usa en ningún lado.
    db.execute("DROP TABLE IF EXISTS otp_codigos")

    # eventos_timeline.tipo tiene un CHECK que ALTER TABLE no puede ampliar
    # directamente: si la tabla en disco todavía no acepta los tipos nuevos,
    # se reconstruye conservando todas las filas.
    definicion_actual = db.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'eventos_timeline'"
    ).fetchone()
    if definicion_actual and "video_ingreso" not in definicion_actual["sql"]:
        # RENAME TABLE reescribe automáticamente la FK de medios.evento_id
        # hacia el nombre temporal "eventos_timeline_viejo". Probado a mano:
        # ninguna de las dos pragmas la evita por separado, pero juntas sí
        # (foreign_keys=OFF solo no alcanza, y legacy_alter_table=ON solo
        # tampoco si foreign_keys sigue en ON).
        db.execute("PRAGMA foreign_keys = OFF")
        db.execute("PRAGMA legacy_alter_table = ON")
        db.executescript(
            f"""
            ALTER TABLE eventos_timeline RENAME TO eventos_timeline_viejo;
            CREATE TABLE eventos_timeline ({EVENTOS_TIMELINE_COLUMNAS});
            INSERT INTO eventos_timeline
                (id, orden_id, tipo, titulo, descripcion, medio_path, creado_por, creado_en)
                SELECT id, orden_id, tipo, titulo, descripcion, medio_path, creado_por, creado_en
                FROM eventos_timeline_viejo;
            DROP TABLE eventos_timeline_viejo;
            """
        )
        db.commit()
        db.execute("PRAGMA legacy_alter_table = OFF")
        db.execute("PRAGMA foreign_keys = ON")


def init_db():
    db = get_db()
    db.executescript(SCHEMA)
    db.commit()
    migrate_schema(db)


def init_app(app):
    app.teardown_appcontext(close_db)

    with app.app_context():
        init_db()

    @app.cli.command("crear-admin")
    @click.argument("usuario")
    @click.argument("password")
    @click.option(
        "--superadmin", "es_superadmin", is_flag=True, default=False,
        help="Crea el usuario con rol superadmin (puede gestionar otros admins y tokens de la app móvil).",
    )
    def crear_admin_cmd(usuario, password, es_superadmin):
        """Crea (o actualiza la contraseña de) un usuario admin del panel.

        El primer admin del sistema siempre se crea como superadmin, sin
        importar la bandera --superadmin, para que exista alguien capaz de
        gestionar el resto desde /admin/usuarios.
        """
        from werkzeug.security import generate_password_hash

        from . import models

        existente = models.obtener_admin_por_usuario(usuario)
        if existente:
            models.actualizar_password_admin(existente["id"], generate_password_hash(password))
            click.echo(f"Contraseña actualizada para el admin '{usuario}'.")
            return

        es_primero = models.contar_admins() == 0
        rol = "superadmin" if (es_primero or es_superadmin) else "admin"
        models.crear_admin(usuario, generate_password_hash(password), rol)
        etiqueta = " (superadmin)" if rol == "superadmin" else ""
        click.echo(f"Admin '{usuario}' creado{etiqueta}.")

    @app.cli.command("crear-tecnico")
    @click.argument("usuario")
    @click.argument("password")
    @click.argument("nombre")
    def crear_tecnico_cmd(usuario, password, nombre):
        """Crea (o actualiza la contraseña de) un mecánico con acceso a la app móvil."""
        from werkzeug.security import generate_password_hash

        from . import models

        existente = models.obtener_mecanico_por_usuario(usuario)
        if existente:
            models.actualizar_password_mecanico(existente["id"], generate_password_hash(password))
            click.echo(f"Contraseña actualizada para el técnico '{usuario}'.")
        else:
            models.crear_mecanico(usuario, generate_password_hash(password), nombre)
            click.echo(f"Técnico '{usuario}' ({nombre}) creado.")
