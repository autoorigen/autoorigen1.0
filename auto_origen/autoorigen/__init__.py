from pathlib import Path

from flask import Flask

from . import auth, db
from .config import Config
from .extensions import csrf, login_manager, socketio

BASE_DIR = Path(__file__).resolve().parent.parent


def create_app():
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )
    app.config.from_object(Config)

    db.init_app(app)

    socketio.init_app(app)
    csrf.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "admin.login"
    login_manager.login_message = "Inicia sesión para entrar al panel admin."

    @login_manager.user_loader
    def cargar_usuario(admin_id):
        return auth.cargar_admin(admin_id)

    from .routes.admin import admin_bp
    from .routes.api import api_bp
    from .routes.historial import historial_bp
    from .routes.mecanico import mecanico_bp
    from .routes.public import public_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(historial_bp, url_prefix="/historial")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(mecanico_bp, url_prefix="/mecanico")

    # La API para la app móvil se autentica con token Bearer, no con cookies de
    # sesión: el CSRF de formularios no aplica ahí.
    csrf.exempt(api_bp)

    from . import sockets  # noqa: F401  (registra los handlers de socketio)

    return app
