from datetime import datetime, timedelta, timezone

from flask import (Blueprint, abort, current_app, redirect, render_template,
                    request, send_from_directory, session, url_for)

from .. import models

historial_bp = Blueprint("historial", __name__)


@historial_bp.route("/")
def buscar():
    return render_template("historial/buscar.html", error=None)


@historial_bp.route("/verificar", methods=["POST"])
def verificar():
    placa = models.normalizar_placa(request.form.get("placa"))
    codigo_acceso = (request.form.get("codigo_acceso") or "").strip()

    if not placa or not codigo_acceso:
        return render_template("historial/buscar.html", error="Ingresa la placa y el código de acceso.")

    vehiculo = models.obtener_vehiculo_por_placa_y_codigo(placa, codigo_acceso)
    if not vehiculo:
        return render_template(
            "historial/buscar.html",
            error="Placa o código de acceso incorrectos. El código te lo entrega el taller.",
        )

    session["historial_vehiculo_id"] = vehiculo["id"]
    session["historial_expira"] = (
        datetime.now(timezone.utc) + timedelta(minutes=current_app.config["HISTORIAL_SESION_MINUTOS"])
    ).isoformat()

    return redirect(url_for("historial.hoja_de_vida", placa=placa))


def _tiene_acceso(vehiculo_id):
    if session.get("historial_vehiculo_id") != vehiculo_id:
        return False
    expira = session.get("historial_expira")
    if not expira or datetime.fromisoformat(expira) < datetime.now(timezone.utc):
        return False
    return True


@historial_bp.route("/vehiculo/<placa>")
def hoja_de_vida(placa):
    placa = models.normalizar_placa(placa)
    vehiculo = models.obtener_vehiculo_por_placa(placa)
    if not vehiculo or not _tiene_acceso(vehiculo["id"]):
        return render_template(
            "historial/buscar.html",
            error="Tu sesión expiró o no verificaste esta placa. Vuelve a intentarlo.",
        )

    cliente = models.obtener_cliente(vehiculo["cliente_id"])
    ordenes = models.listar_ordenes_por_vehiculo(vehiculo["id"])
    orden_activa = ordenes[0] if ordenes else None
    eventos = models.listar_eventos_por_orden(orden_activa["id"]) if orden_activa else []
    medios = models.listar_medios_por_vehiculo(vehiculo["id"])

    etapas = ["recibido", "diagnosticando", "diagnosticado", "reparando", "verificando", "listo"]

    return render_template(
        "historial/hoja_de_vida.html",
        vehiculo=vehiculo, cliente=cliente, ordenes=ordenes,
        orden_activa=orden_activa, eventos=eventos, medios=medios, etapas=etapas,
    )


@historial_bp.route("/medios/<int:medio_id>")
def ver_medio(medio_id):
    medio = models.obtener_medio_con_vehiculo(medio_id)
    if not medio or not _tiene_acceso(medio["vehiculo_id"]):
        abort(403)
    return send_from_directory(current_app.config["UPLOAD_DIR"], medio["archivo_path"])
