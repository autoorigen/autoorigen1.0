"""Transcribe los videos del mecánico con Whisper local (faster-whisper),
reutilizando Autoorigen_IA_Content_Studio/app/core/transcriber.py sin
duplicar esa lógica.

Se carga por ruta de archivo (importlib), no como un import normal del
paquete "app" de Content Studio — este proyecto ya tiene su propio
app.py en la raíz, y los nombres chocarían.
"""
import importlib.util
import os
import shutil
from pathlib import Path

from flask import current_app

from . import models

BASE_DIR = Path(__file__).resolve().parent.parent
TRANSCRIBER_PATH = BASE_DIR / "Autoorigen_IA_Content_Studio" / "app" / "core" / "transcriber.py"

_modulo_transcriber = None
_motor = None


def _asegurar_ffmpeg_en_path():
    """faster-whisper necesita ffmpeg en el PATH. Si se instaló con winget en
    esta misma sesión, la terminal donde arrancó el servidor puede no haber
    recogido el PATH actualizado todavía — se busca la carpeta conocida como
    respaldo en vez de fallar."""
    if shutil.which("ffmpeg"):
        return
    base_winget = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages"
    if not base_winget.exists():
        return
    for carpeta in base_winget.glob("Gyan.FFmpeg_*/ffmpeg-*/bin"):
        if (carpeta / "ffmpeg.exe").exists():
            os.environ["PATH"] = str(carpeta) + os.pathsep + os.environ.get("PATH", "")
            return


def _cargar_transcriber():
    global _modulo_transcriber
    if _modulo_transcriber is not None:
        return _modulo_transcriber
    if not TRANSCRIBER_PATH.exists():
        raise RuntimeError(
            f"No se encontró {TRANSCRIBER_PATH}. Autoorigen_IA_Content_Studio debe estar "
            "en la raíz del repositorio para poder transcribir videos."
        )
    spec = importlib.util.spec_from_file_location("autoorigen_content_studio_transcriber", TRANSCRIBER_PATH)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    _modulo_transcriber = modulo
    return modulo


def _obtener_motor():
    global _motor
    if _motor is None:
        _asegurar_ffmpeg_en_path()
        modulo = _cargar_transcriber()
        _motor = modulo.AutoorigenTranscriber(current_app.config["WHISPER_MODELO"], "cpu", "int8")
    return _motor


def transcribir_videos_de_orden(orden_id):
    """Transcribe todos los videos ya subidos para esa orden. Devuelve una
    lista de (nombre_archivo, texto). Puede tardar bastante sin GPU —
    llamar siempre desde una tarea de fondo, nunca dentro de una petición
    HTTP normal."""
    videos = models.listar_medios_por_orden(orden_id, tipo="video")
    if not videos:
        return []

    motor = _obtener_motor()
    upload_dir = current_app.config["UPLOAD_DIR"]
    resultados = []
    for video in videos:
        ruta = Path(upload_dir) / video["archivo_path"]
        if not ruta.exists():
            resultados.append((video["archivo_path"], ""))
            continue
        datos = motor.transcribe(ruta, language="es")
        texto = " ".join(segmento["text"] for segmento in datos["segments"])
        resultados.append((video["archivo_path"], texto))
    return resultados
