"""Páginas web para mecánicos (misma API que la app Android: /api/tecnicos/...
y /api/inspecciones/...). Son pantallas casi vacías del lado del servidor —
toda la lógica vive en static/js/mecanico/*.js, que llama a la API con el
token guardado en localStorage. Así, la misma experiencia de AutoorigenInspect
se puede "instalar" en cualquier teléfono (incluido iPhone, sin Mac) como PWA.
"""
from flask import Blueprint, render_template

mecanico_bp = Blueprint("mecanico", __name__)


@mecanico_bp.route("/login")
def login():
    return render_template("mecanico/login.html")


@mecanico_bp.route("/")
def home():
    return render_template("mecanico/home.html")


@mecanico_bp.route("/nueva")
def nueva_inspeccion():
    return render_template("mecanico/nueva.html")


@mecanico_bp.route("/captura/<int:orden_id>")
def captura(orden_id):
    return render_template("mecanico/captura.html", orden_id=orden_id)


@mecanico_bp.route("/observaciones/<int:orden_id>")
def observaciones(orden_id):
    return render_template("mecanico/observaciones.html", orden_id=orden_id)


@mecanico_bp.route("/historial")
def historial():
    return render_template("mecanico/historial.html")


@mecanico_bp.route("/detalle/<int:orden_id>")
def detalle(orden_id):
    return render_template("mecanico/detalle.html", orden_id=orden_id)
