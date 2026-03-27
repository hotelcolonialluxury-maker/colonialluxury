from flask import Blueprint, request, jsonify
from controllers.pago_controller import PagoController
from middlewares.auth_middleware import solo_admin

pago_routes = Blueprint('pago_routes', __name__)


# Obtener todos los pagos (solo admin)
@pago_routes.route("/pagos", methods=["GET"])
@solo_admin
def listar_pagos(usuario_actual):
    pagos = PagoController.obtener_pagos()
    return jsonify(pagos), 200


# Crear nuevo pago
@pago_routes.route("/pagos", methods=["POST"])
def crear_pago():
    data = request.get_json(silent=True) or {}

    resultado = PagoController.crear_pago(data)
    if not resultado["ok"]:
        return jsonify({"message": resultado["error"]}), 400

    pago = resultado["pago"]

    # Si es tarjeta, generamos URL real de checkout de Wompi.
    if pago.metodo == "tarjeta":
        checkout = PagoController.generar_checkout_wompi(pago)
        if not checkout["ok"]:
            return jsonify({"message": checkout["error"]}), 500

        return jsonify({
            "tipo": "tarjeta",
            "url_pago": checkout["url"],
            "pago_id": pago.id,
            "referencia": checkout["referencia"],
            "amount_in_cents": checkout["amount_in_cents"]
        }), 201

    # Transferencia
    return jsonify({
        "tipo": "transferencia",
        "pago_id": pago.id,
        "message": "Pago creado, pendiente de confirmacion"
    }), 201


# Actualizar pago (solo admin)
@pago_routes.route('/pagos/<int:id>', methods=['PUT'])
@solo_admin
def actualizar_pago(usuario_actual, id):
    data = request.get_json(silent=True) or {}
    resultado = PagoController.actualizar_pago(id, data)
    if resultado:
        return jsonify({"message": "Pago actualizado correctamente"}), 200
    return jsonify({"message": "Error al actualizar pago"}), 400


# Eliminar pago (solo admin)
@pago_routes.route('/pagos/<int:id>', methods=['DELETE'])
@solo_admin
def eliminar_pago(usuario_actual, id):
    resultado = PagoController.eliminar_pago(id)
    if resultado:
        return jsonify({"message": "Pago eliminado correctamente"}), 200
    return jsonify({"message": "Error al eliminar pago"}), 400


@pago_routes.route("/pagos/tarjeta", methods=["POST"])
def pagar_tarjeta():
    data = request.get_json(silent=True) or {}
    data["metodo"] = "tarjeta"

    resultado = PagoController.crear_pago(data)
    if not resultado["ok"]:
        return jsonify({"message": resultado["error"]}), 400

    pago = resultado["pago"]
    checkout = PagoController.generar_checkout_wompi(pago)
    if not checkout["ok"]:
        return jsonify({"message": checkout["error"]}), 500

    return jsonify({
        "url_pago": checkout["url"],
        "pago_id": pago.id,
        "referencia": checkout["referencia"]
    }), 201


@pago_routes.route("/pagos/webhook", methods=["POST"])
def webhook_wompi():
    data = request.get_json(silent=True) or {}

    transaction = data.get("transaction") or (data.get("data") or {}).get("transaction")
    if not transaction:
        return jsonify({"error": "Payload invalido"}), 400

    referencia = str(transaction.get("reference") or "").strip()
    estado_wompi = (transaction.get("status") or "").upper()
    wompi_id = transaction.get("id")

    estados = {
        "APPROVED": "pagado",
        "DECLINED": "rechazado",
        "VOIDED": "rechazado",
        "ERROR": "rechazado",
        "PENDING": "pendiente",
    }

    estado_local = estados.get(estado_wompi)
    if not referencia or not estado_local:
        return jsonify({"ok": True}), 200

    PagoController.actualizar_estado_por_referencia(
        referencia=referencia,
        estado=estado_local,
        referencia_externa=wompi_id
    )

    return jsonify({"ok": True}), 200
