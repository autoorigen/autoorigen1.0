"""Eventos de Socket.IO para la línea de tiempo en vivo de 'Historia mecánica del vehículo'.

Un visitante solo puede unirse al room de un vehículo si su sesión de Flask
(creada al verificar placa + código de acceso en /historial) ya tiene acceso
a ese vehiculo_id. Así evitamos exponer las líneas de tiempo de otros clientes.
"""
from flask import session
from flask_socketio import join_room

from .extensions import socketio


def room_vehiculo(vehiculo_id):
    return f"vehiculo:{vehiculo_id}"


@socketio.on("historial:unirse")
def historial_unirse(data):
    vehiculo_id = session.get("historial_vehiculo_id")
    if not vehiculo_id:
        return
    solicitado = (data or {}).get("vehiculo_id")
    if str(vehiculo_id) != str(solicitado):
        return
    join_room(room_vehiculo(vehiculo_id))


def emitir_nuevo_evento(vehiculo_id, evento_row, orden_row):
    socketio.emit(
        "timeline:nuevo_evento",
        {
            "id": evento_row["id"],
            "tipo": evento_row["tipo"],
            "titulo": evento_row["titulo"],
            "descripcion": evento_row["descripcion"],
            "medio_path": evento_row["medio_path"],
            "creado_en": evento_row["creado_en"],
            "orden_estado_actual": orden_row["estado_actual"],
        },
        room=room_vehiculo(vehiculo_id),
    )
