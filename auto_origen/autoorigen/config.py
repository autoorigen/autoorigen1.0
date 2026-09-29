import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-cambia-esta-clave")

    DB_PATH = Path(os.environ.get("DB_PATH", BASE_DIR / "data" / "autoorigen.db"))
    DATABASE_URL = os.environ.get("DATABASE_URL")
    UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", BASE_DIR / "data" / "uploads"))
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25 MB por archivo subido

    # "Historia mecánica del vehículo" se verifica con placa + código de
    # acceso propio del vehículo (autoorigen/models.py: generar_codigo_acceso),
    # no con SMS — no hay credenciales de terceros que configurar aquí.
    HISTORIAL_SESION_MINUTOS = 30

    # Informes con IA (autoorigen/ia.py): Ollama corre local, sin API de pago.
    # Mismos valores por defecto que Autoorigen_IA_Content_Studio/config/settings.example.json.
    OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
    OLLAMA_MODELO = os.environ.get("OLLAMA_MODELO", "qwen2.5:7b")

    # Transcripción (autoorigen/transcripcion.py): tamaño del modelo de Whisper.
    # "small" es un buen punto de partida en CPU sin GPU dedicada.
    WHISPER_MODELO = os.environ.get("WHISPER_MODELO", "small")
