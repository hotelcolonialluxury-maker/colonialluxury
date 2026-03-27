from flask import Blueprint, request, jsonify
from controllers.usuario_controller import UsuarioController
from middlewares.auth_middleware import solo_admin

usuario_routes = Blueprint('usuario_routes', __name__)

# ✅ Ruta para obtener todos los usuarios (solo admin)
@usuario_routes.route('/usuarios', methods=['GET'])
@solo_admin
def listar_usuarios(usuario_actual):
    usuarios = UsuarioController.obtener_usuarios()
    return jsonify(usuarios), 200


# ✅ Ruta para crear usuario (solo admin)
@usuario_routes.route('/usuarios', methods=['POST'])
@solo_admin
def crear_usuario(usuario_actual):
    data = request.get_json(silent=True) or {}
    resultado = UsuarioController.crear_usuario(data)
    if resultado["ok"]:
        return jsonify({"message": resultado["message"]}), 201
    return jsonify({"error": resultado["message"]}), 400


# ✅ Ruta para actualizar usuario (solo admin)
@usuario_routes.route('/usuarios/<int:id>', methods=['PUT'])
@solo_admin
def actualizar_usuario(usuario_actual, id):
    data = request.get_json(silent=True) or {}
    resultado = UsuarioController.actualizar_usuario(id, data)
    if resultado["ok"]:
        return jsonify({"message": resultado["message"]}), 200
    return jsonify({"error": resultado["message"]}), 400


# ✅ Ruta para eliminar usuario (solo admin)
@usuario_routes.route('/usuarios/<int:id>', methods=['DELETE'])
@solo_admin
def eliminar_usuario(usuario_actual, id):
    resultado = UsuarioController.eliminar_usuario(id)
    if resultado["ok"]:
        return jsonify({"message": resultado["message"]}), 200
    return jsonify({"error": resultado["message"]}), 404
