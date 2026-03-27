# routes/auth_routes.py
from flask import Blueprint, request, jsonify
from models.usuario import Usuario
from models import db
import jwt
from datetime import datetime, timedelta
from config import Config
from werkzeug.security import generate_password_hash
from middlewares.auth_middleware import token_requerido, solo_admin

auth_routes = Blueprint("auth", __name__)

@auth_routes.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}

    nombre = data.get("nombre")
    email = data.get("email")
    password = data.get("password")

    if not all([nombre, email, password]):
        return jsonify({"mensaje": "Faltan datos"}), 400

    if len(password) < 6:
        return jsonify({"mensaje": "La contraseña debe tener al menos 6 caracteres"}), 400

    if Usuario.obtener_por_email(email):
        return jsonify({"mensaje": "El usuario ya existe"}), 400

    hashed = generate_password_hash(password)

    nuevo = Usuario(
        nombre=nombre,
        email=email,
        password=hashed,
        rol="cliente"
    )

    try:
        db.session.add(nuevo)
        db.session.commit()
        return jsonify({"mensaje": "Usuario creado exitosamente"}), 201
    except Exception as e:
        db.session.rollback()
        print("Error al registrar usuario:", e)
        return jsonify({"mensaje": "Error interno"}), 500


@auth_routes.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email y contraseña requeridos"}), 400

    usuario = Usuario.obtener_por_email(email)

    if not usuario or not usuario.check_password(password):
        return jsonify({"error": "Correo o contraseña incorrectos"}), 401

    if not Config.SECRET_KEY:
        return jsonify({"error": "Error de configuración del servidor"}), 500

    payload = {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "email": usuario.email,
        "rol": usuario.rol,
        "exp": datetime.utcnow() + timedelta(hours=6)
    }

    token = jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")

    # 🔧 Compatibilidad PyJWT
    if isinstance(token, bytes):
        token = token.decode("utf-8")

    return jsonify({
        "mensaje": "Login exitoso",
        "usuario": usuario.to_dict(),
        "token": token
    }), 200


@auth_routes.route("/perfil", methods=["GET"])
@token_requerido
def perfil(usuario_actual):
    return jsonify({"usuario": usuario_actual}), 200


@auth_routes.route("/admin", methods=["GET"])
@solo_admin
def admin(usuario_actual):
    return jsonify({
        "mensaje": f"Bienvenido administrador {usuario_actual.get('email')}"
    }), 200