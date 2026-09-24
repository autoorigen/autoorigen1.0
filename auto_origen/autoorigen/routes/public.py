from flask import Blueprint, current_app, jsonify, render_template, request, send_from_directory

from .. import models

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def index():
    return render_template("index.html")


@public_bp.route("/sw.js")
def service_worker():
    # Servido en la raíz (no bajo /static/) para que su alcance cubra todo
    # el sitio — así puede instalarse como PWA en el iPhone (Safari) y en
    # Android/escritorio (Chrome/Edge).
    respuesta = send_from_directory(current_app.static_folder, "sw.js")
    respuesta.headers["Cache-Control"] = "no-cache"
    return respuesta


@public_bp.route("/api/contacto", methods=["POST"])
def contacto():
    data = request.get_json(silent=True) or request.form

    nombre = (data.get("nombre") or "").strip()
    telefono = (data.get("telefono") or "").strip()
    mensaje = (data.get("mensaje") or "").strip()

    if not nombre or not telefono or not mensaje:
        return jsonify(ok=False, error="Nombre, teléfono y mensaje son obligatorios."), 400

    models.crear_contacto(
        nombre,
        telefono,
        (data.get("tipo") or "").strip(),
        (data.get("marca") or "").strip(),
        (data.get("modelo") or "").strip(),
        (data.get("anio") or "").strip(),
        (data.get("problema") or "").strip(),
        mensaje,
    )

    return jsonify(ok=True, message="¡Gracias! Recibimos tu mensaje, te contactaremos pronto.")


def _cliente_desde_formulario(nombre, telefono, email):
    cliente = models.buscar_cliente_por_telefono(telefono)
    if cliente:
        return cliente["id"]
    return models.crear_cliente(nombre, telefono, email)


@public_bp.route("/citas/vehiculo", methods=["GET", "POST"])
def cita_vehiculo():
    errores = []
    if request.method == "POST":
        nombre = (request.form.get("nombre") or "").strip()
        telefono = (request.form.get("telefono") or "").strip()
        email = (request.form.get("email") or "").strip()
        placa = (request.form.get("placa") or "").strip()
        marca = (request.form.get("marca") or "").strip()
        modelo = (request.form.get("modelo") or "").strip()
        anio = (request.form.get("anio") or "").strip()
        fecha = (request.form.get("fecha") or "").strip()
        hora = (request.form.get("hora") or "").strip()
        servicio = (request.form.get("servicio") or "").strip()
        notas = (request.form.get("notas") or "").strip()

        if not nombre or not telefono or not placa or not fecha or not hora:
            errores.append("Nombre, teléfono, placa, fecha y hora son obligatorios.")

        if not errores:
            cliente_id = _cliente_desde_formulario(nombre, telefono, email)
            vehiculo = models.obtener_vehiculo_por_placa(placa)
            if vehiculo:
                vehiculo_id = vehiculo["id"]
            else:
                vehiculo_id = models.crear_vehiculo(cliente_id, placa, marca, modelo, anio)

            models.crear_cita(
                cliente_id, "vehiculo", fecha, hora,
                servicio=servicio, notas=notas, vehiculo_id=vehiculo_id,
            )
            return render_template("citas/vehiculo.html", enviado=True, errores=[])

    return render_template("citas/vehiculo.html", enviado=False, errores=errores)


@public_bp.route("/citas/visita", methods=["GET", "POST"])
def cita_visita():
    errores = []
    if request.method == "POST":
        nombre = (request.form.get("nombre") or "").strip()
        telefono = (request.form.get("telefono") or "").strip()
        email = (request.form.get("email") or "").strip()
        fecha = (request.form.get("fecha") or "").strip()
        hora = (request.form.get("hora") or "").strip()
        motivo = (request.form.get("motivo") or "").strip()
        notas = (request.form.get("notas") or "").strip()

        if not nombre or not telefono or not fecha or not hora:
            errores.append("Nombre, teléfono, fecha y hora son obligatorios.")

        if not errores:
            cliente_id = _cliente_desde_formulario(nombre, telefono, email)
            models.crear_cita(cliente_id, "visita", fecha, hora, servicio=motivo, notas=notas)
            return render_template("citas/visita.html", enviado=True, errores=[])

    return render_template("citas/visita.html", enviado=False, errores=errores)
