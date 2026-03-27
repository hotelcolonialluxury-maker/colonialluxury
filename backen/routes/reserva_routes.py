# routes/reserva_routes.py
from flask import Blueprint, request, jsonify
from controllers.reserva_controller import ReservaController
from models.reserva import Reserva
from models import db
from middlewares.auth_middleware import token_requerido, solo_admin

reserva_routes = Blueprint("reserva_routes", __name__)

# -----------------------------
# 🔹 Crear Reserva (REQUERIDO LOGIN)
# -----------------------------
@reserva_routes.route("/reservas", methods=["POST"])
@token_requerido
def crear_reserva(usuario_actual):
    """
    Crea una reserva para el usuario logueado
    """
    data = request.get_json(silent=True) or {}
    usuario_id = usuario_actual["id"]

    resp, status = ReservaController.crear_reserva(data, usuario_id)
    return jsonify(resp), status

## -----------------------------
# 🔹 Crear Reserva PÚBLICA (SIN LOGIN)
# -----------------------------
@reserva_routes.route("/reservas/publica", methods=["POST"])
def crear_reserva_publica():
    data = request.get_json(silent=True) or {}

    reserva_id = Reserva.crear_reserva(
        usuario_id=None,
        habitacion_id=data.get("habitacion_id"),
        fecha_entrada=data.get("fecha_entrada"),
        fecha_salida=data.get("fecha_salida"),
        num_personas=data.get("num_personas"),
        nombre=data.get("nombre"),
        email=data.get("email"),
        telefono=data.get("telefono"),
        identificacion=data.get("identificacion"),
        notas=data.get("notas", "")
    )

    if isinstance(reserva_id, int):
        return jsonify({
            "message": "Reserva creada correctamente",
            "reserva_id": reserva_id
        }), 201

    if isinstance(reserva_id, str):
        return jsonify({"error": reserva_id}), 400

    return jsonify({"error": "No se pudo crear la reserva"}), 400
# -----------------------------
# 🔹 Listar todas las reservas (ADMIN)
# -----------------------------
@reserva_routes.route("/reservas", methods=["GET"])
@solo_admin
def listar_reservas(usuario_actual):
    """
    Devuelve todas las reservas (solo admins)
    """
    reservas = ReservaController.listar_reservas()
    return jsonify(reservas), 200


# -----------------------------
# 🔹 Cambiar estado de reserva (ADMIN)
# -----------------------------
@reserva_routes.route("/reservas/<int:id>/estado", methods=["PUT"])
@solo_admin
def actualizar_estado(usuario_actual, id):
    """
    Actualiza el estado de una reserva por ID
    """
    data = request.get_json(silent=True) or {}
    nuevo_estado = data.get("estado")

    if not nuevo_estado:
        return jsonify({"error": "Falta el nuevo estado"}), 400

    ok = ReservaController.cambiar_estado(id, nuevo_estado)

    if ok:
        return jsonify({"message": "Estado actualizado"}), 200

    return jsonify({"error": "No se pudo actualizar"}), 400

# -----------------------------
# 🔹 Obtener reserva por ID (ADMIN)
# -----------------------------
@reserva_routes.route("/reservas/<int:id>", methods=["GET"])
@solo_admin
def obtener_reserva(usuario_actual, id):
    """
    Devuelve el detalle completo de una reserva
    """
    reserva = Reserva.query.get(id)

    if not reserva:
        return jsonify({"error": "Reserva no encontrada"}), 404

    return jsonify({
        "id": reserva.id,
        "nombre": reserva.nombre,
        "email": reserva.email,
        "telefono": reserva.telefono,
        "notas": reserva.notas,
        "fecha_entrada": reserva.fecha_entrada.strftime("%Y-%m-%d"),
        "fecha_salida": reserva.fecha_salida.strftime("%Y-%m-%d"),
        "num_personas": reserva.num_personas,
        "precio_total": reserva.precio_total,
        "estado": reserva.estado,
        "habitacion": {
            "id": reserva.habitacion.id,
            "nombre": reserva.habitacion.nombre
        } if reserva.habitacion else None
    }), 200

# -----------------------------
# 🔹 Eliminar reserva (ADMIN)
# -----------------------------
@reserva_routes.route("/reservas/<int:id>", methods=["DELETE"])
@solo_admin
def eliminar_reserva(usuario_actual, id):
    """
    Elimina una reserva por ID (solo admin)
    """
    reserva = Reserva.query.get(id)
    if not reserva:
        return jsonify({"error": "Reserva no encontrada"}), 404

    try:
        db.session.delete(reserva)
        db.session.commit()
        return jsonify({"message": "Reserva eliminada"}), 200

    except Exception as e:
        db.session.rollback()
        print("Error eliminando reserva:", e)
        return jsonify({"error": "Error eliminando la reserva"}), 500
