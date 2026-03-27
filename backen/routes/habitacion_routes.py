from flask import Blueprint, request, jsonify, current_app
from controllers.habitacion_controller import HabitacionController
from middlewares.auth_middleware import solo_admin
from werkzeug.utils import secure_filename
import os
import time

habitacion_routes = Blueprint('habitacion_routes', __name__)

# =========================
# CONFIGURACIÓN
# =========================
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# =========================
# LISTAR HABITACIONES
# =========================
@habitacion_routes.route('/habitaciones', methods=['GET'])
def listar_habitaciones():
    habitaciones = HabitacionController.obtener_habitaciones()
    return jsonify(habitaciones), 200
# =========================
# OBTENER HABITACIÓN
# =========================
@habitacion_routes.route('/habitaciones/<int:id>', methods=['GET'])
def obtener_habitacion(id):
    habitacion = HabitacionController.obtener_habitacion_por_id(id)
    if habitacion:
        return jsonify(habitacion), 200
    return jsonify({"error": "Habitación no encontrada"}), 404

# =========================
# CREAR HABITACIÓN (CON IMAGEN)
# =========================
@habitacion_routes.route('/habitaciones', methods=['POST'])
@solo_admin
def crear_habitacion(usuario_actual):
    data = request.form.to_dict()
    imagen = request.files.get('imagen')

    if imagen and allowed_file(imagen.filename):
        filename = secure_filename(imagen.filename)
        nombre_final = f"{data.get('tipo', 'habitacion')}_{int(time.time())}_{filename}"

        ruta = os.path.join(
            current_app.root_path,
            'static',
            'uploads',
            'habitaciones',
            nombre_final
        )

        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        imagen.save(ruta)

        data['imagen'] = nombre_final
    else:
        data['imagen'] = None

    mensaje, exito = HabitacionController.crear_habitacion(data)

    if exito:
        return jsonify({"message": mensaje}), 201
    return jsonify({"error": mensaje}), 400

# =========================
# ACTUALIZAR HABITACIÓN (CON IMAGEN)
# =========================
@habitacion_routes.route('/habitaciones/<int:id>', methods=['PUT'])
@solo_admin
def actualizar_habitacion(usuario_actual, id):
    data = request.form.to_dict()
    imagen = request.files.get('imagen')

    if imagen and allowed_file(imagen.filename):
        filename = secure_filename(imagen.filename)
        nombre_final = f"{data.get('tipo', 'habitacion')}_{int(time.time())}_{filename}"

        ruta = os.path.join(
            current_app.root_path,
            'static',
            'uploads',
            'habitaciones',
            nombre_final
        )

        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        imagen.save(ruta)

        data['imagen'] = nombre_final

    resultado = HabitacionController.actualizar_habitacion(id, data)

    if resultado:
        return jsonify({"message": "Habitación actualizada correctamente"}), 200
    return jsonify({"error": "Error al actualizar habitación"}), 400

# =========================
# ELIMINAR HABITACIÓN
# =========================
@habitacion_routes.route('/habitaciones/<int:id>', methods=['DELETE'])
@solo_admin
def eliminar_habitacion(usuario_actual, id):
    resultado = HabitacionController.eliminar_habitacion(id)
    if resultado:
        return jsonify({"message": "Habitación eliminada correctamente"}), 200
    return jsonify({"error": "Error al eliminar habitación"}), 400