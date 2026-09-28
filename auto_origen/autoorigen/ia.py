"""Generación de informes de inspección con IA local (Ollama).

No usa ninguna API de pago ni en la nube: llama a Ollama corriendo en la
misma máquina, con el mismo patrón que
Autoorigen_IA_Content_Studio/app/core/ollama.py (POST /api/generate). Si
Ollama no está disponible, falla con un mensaje claro — nunca genera un
informe vacío ni inventa contenido.

La IA solo redacta a partir de lo que el taller ya escribió (hallazgos,
observaciones, cambios de etapa) y, para el informe final, de la
transcripción de los videos del mecánico. No "ve" fotos ni video — no hay
IA de visión instalada — solo cuenta cuántos hay y los menciona.
"""
import requests
from flask import current_app

from . import models

ETIQUETAS_TIPO_EVENTO = {
    "nota": "Nota",
    "hallazgo": "Hallazgo",
    "observacion_mecanico": "Observación del mecánico",
    "comentario_cliente": "Comentario del cliente",
    "cambio_estado": "Cambio de etapa",
}

PROMPT_PRELIMINAR = """Eres el asistente de Autoorigen, un taller mecánico. Con la información de
abajo, redacta un INFORME PRELIMINAR breve y claro para el cliente, explicando en qué va la
inspección/reparación de su vehículo hasta ahora. Tono profesional y cercano, en español, sin
tecnicismos innecesarios. No inventes hallazgos, piezas, diagnósticos ni reparaciones que no
estén en la información dada — si falta información, dilo en vez de inventar.

INFORMACIÓN DEL TALLER:
{contexto}

Escribe el informe preliminar ahora:"""

PROMPT_FINAL = """Eres el asistente de Autoorigen, un taller mecánico. Con la información de abajo
(incluida la transcripción de lo que dijo el mecánico en sus videos), redacta el INFORME FINAL de
esta reparación para que lo revise el jefe del taller antes de mandárselo al cliente. Debe cubrir:
qué se encontró, qué se hizo, y el estado final del vehículo. Tono profesional, en español, sin
tecnicismos innecesarios. No inventes nada que no esté en la información dada.

INFORMACIÓN DEL TALLER:
{contexto}

Escribe el informe final ahora:"""


class OllamaNoDisponible(RuntimeError):
    pass


def _ollama_disponible():
    try:
        r = requests.get(f"{current_app.config['OLLAMA_URL']}/api/tags", timeout=3)
        return r.ok
    except requests.RequestException:
        return False


def _generar_texto(prompt):
    if not _ollama_disponible():
        raise OllamaNoDisponible(
            f"Ollama no está disponible en {current_app.config['OLLAMA_URL']}. "
            "Instálalo y déjalo corriendo antes de generar informes."
        )
    respuesta = requests.post(
        f"{current_app.config['OLLAMA_URL']}/api/generate",
        json={"model": current_app.config["OLLAMA_MODELO"], "prompt": prompt, "stream": False},
        timeout=900,
    )
    respuesta.raise_for_status()
    texto = (respuesta.json().get("response") or "").strip()
    if not texto:
        raise OllamaNoDisponible("Ollama respondió, pero sin contenido.")
    return texto


def _contexto_orden(orden_id, transcripciones=None):
    orden = models.obtener_orden_detalle(orden_id)
    if not orden:
        raise ValueError(f"La orden {orden_id} no existe.")

    eventos = models.listar_eventos_texto_por_orden(orden_id)
    fotos = models.listar_medios_por_orden(orden_id, tipo="foto")
    videos = models.listar_medios_por_orden(orden_id, tipo="video")

    lineas = [
        f"Vehículo: {orden['vehiculo_placa']} — {(orden['marca'] or '')} {(orden['modelo'] or '')}".strip(),
    ]
    if orden["combustible"]:
        lineas.append(f"Combustible: {orden['combustible']}")
    if orden["kilometraje"]:
        lineas.append(f"Kilometraje: {orden['kilometraje']}")
    if orden["kilometraje_aceite"]:
        lineas.append(f"Kilometraje del aceite: {orden['kilometraje_aceite']}")
    lineas.append(f"Cliente: {orden['cliente_nombre']}")
    if orden["tecnico_nombre"]:
        lineas.append(f"Técnico a cargo: {orden['tecnico_nombre']}")

    lineas.append("")
    lineas.append("Cronología registrada por el taller:")
    if eventos:
        for evento in eventos:
            etiqueta = ETIQUETAS_TIPO_EVENTO.get(evento["tipo"], evento["tipo"])
            texto = evento["descripcion"] or evento["titulo"]
            fecha = (evento["creado_en"] or "")[:16].replace("T", " ")
            lineas.append(f"- [{fecha}] {etiqueta}: {texto}")
    else:
        lineas.append("- (todavía no hay notas escritas)")

    lineas.append("")
    lineas.append(f"Evidencia adjunta: {len(fotos)} foto(s) y {len(videos)} video(s) (no se describe el contenido visual).")

    if transcripciones:
        lineas.append("")
        lineas.append("Transcripción de lo que dijo el mecánico en sus videos:")
        for nombre, texto in transcripciones:
            lineas.append(f"--- {nombre} ---")
            lineas.append(texto.strip() if texto and texto.strip() else "(sin voz reconocible en este video)")

    return orden, "\n".join(lineas)


def generar_informe(orden_id, tipo, transcripciones=None):
    """tipo: 'preliminar' o 'final'. `transcripciones` es una lista de
    (nombre_archivo, texto) — se usa para el informe final."""
    if tipo not in ("preliminar", "final"):
        raise ValueError("tipo debe ser 'preliminar' o 'final'.")

    orden, contexto = _contexto_orden(orden_id, transcripciones)
    plantilla = PROMPT_PRELIMINAR if tipo == "preliminar" else PROMPT_FINAL
    contenido = _generar_texto(plantilla.format(contexto=contexto))
    informe = models.crear_informe(orden_id, tipo, contenido)
    return informe, orden


def generar_preliminar_y_publicar(orden_id):
    """Genera el informe preliminar y lo publica de inmediato en la línea de
    tiempo del cliente (se ve en vivo, sin esperar aprobación)."""
    from .sockets import emitir_nuevo_evento

    informe, orden = generar_informe(orden_id, "preliminar")
    evento = models.crear_evento(
        orden_id, "informe", "Informe preliminar de la inspección",
        informe["contenido"], creado_por="admin",
    )
    emitir_nuevo_evento(orden["vehiculo_id"], evento, models.obtener_orden(orden_id))
    return informe


def generar_final_pendiente(orden_id):
    """Transcribe los videos y genera el informe final. Queda con
    estado='generado', esperando que el jefe de taller lo apruebe o
    rechace desde /admin/informes — no se publica todavía."""
    from . import transcripcion

    transcripciones = transcripcion.transcribir_videos_de_orden(orden_id)
    informe, _orden = generar_informe(orden_id, "final", transcripciones=transcripciones)
    return informe


def procesar_cambio_de_etapa(app, orden_id, estado_nuevo):
    """Pensada para correr en una tarea de fondo (socketio.start_background_task),
    nunca dentro de la petición HTTP que cambió la etapa — transcribir video
    puede tardar bastante sin GPU."""
    with app.app_context():
        try:
            if estado_nuevo == "reparando":
                generar_preliminar_y_publicar(orden_id)
            elif estado_nuevo == "listo":
                generar_final_pendiente(orden_id)
        except Exception as exc:  # noqa: BLE001 — se registra, no hay petición HTTP esperando
            app.logger.error("No se pudo generar el informe de la orden %s: %s", orden_id, exc)
