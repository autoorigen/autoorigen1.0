import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-cambia-esta-clave")

    DB_PATH = Path(os.environ.get("DB_PATH", BASE_DIR / "data" / "autoorigen.db"))
    UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", BASE_DIR / "data" / "uploads"))
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25 MB por archivo subido

    # "Historia mecánica del vehículo" se verifica con placa + código de
    # acceso propio del vehículo (autoorigen/models.py: generar_codigo_acceso),
    # no con SMS — no hay credenciales de terceros que configurar aquí.
    HISTORIAL_SESION_MINUTOS = 30
