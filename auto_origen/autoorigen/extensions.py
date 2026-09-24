from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_wtf import CSRFProtect

socketio = SocketIO(cors_allowed_origins="*")
login_manager = LoginManager()
csrf = CSRFProtect()
