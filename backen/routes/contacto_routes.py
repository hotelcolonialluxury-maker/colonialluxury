from flask import Blueprint, request, jsonify
from models import db
from models.contacto import Contacto
from middlewares.auth_middleware import solo_admin

contacto_routes = Blueprint('contacto_routes', __name__)

# ➤ Crear un nuevo contacto
@contacto_routes.route('/contactos', methods=['POST'])
def crear_contacto():
    data = request.get_json(silent=True) or {}

    if not data or not data.get('nombre') or not data.get('mensaje'):
        return jsonify({'error': 'Nombre y mensaje son obligatorios'}), 400

    ok = Contacto.crear(
        nombre=data.get('nombre'),
        mensaje=data.get('mensaje'),
        email=data.get('email'),
        telefono=data.get('telefono'),
        asunto=data.get('asunto')
    )

    if not ok:
        return jsonify({'error': 'No se pudo guardar el contacto'}), 500

    return jsonify({'msg': 'Contacto enviado correctamente'}), 201

# ➤ Listar todos los contactos (ADMIN)
@contacto_routes.route('/contactos', methods=['GET'])
@solo_admin
def listar_contactos(usuario_actual):
    contactos = Contacto.obtener_todos()
    return jsonify(contactos), 200

# ➤ Eliminar contacto
@contacto_routes.route('/contactos/<int:id>', methods=['DELETE'])
@solo_admin
def eliminar_contacto(usuario_actual, id):
    contacto = Contacto.query.get(id)

    if not contacto:
        return jsonify({'error': 'Contacto no encontrado'}), 404

    db.session.delete(contacto)
    db.session.commit()

    return jsonify({'msg': 'Contacto eliminado correctamente'}), 200

# ➤ Marcar contacto como leído / no leído
@contacto_routes.route('/contactos/<int:id>/leido', methods=['PUT'])
@solo_admin
def marcar_leido(usuario_actual, id):
    data = request.get_json(silent=True) or {}
    leido = data.get('leido')

    if leido is None:
        return jsonify({'error': 'Estado leido requerido'}), 400

    contacto = Contacto.query.get(id)

    if not contacto:
        return jsonify({'error': 'Contacto no encontrado'}), 404

    contacto.leido = leido
    contacto.estado = "leido" if leido else "pendiente"

    db.session.commit()

    return jsonify({'msg': 'Estado actualizado'}), 200
