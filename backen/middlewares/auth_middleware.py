# middlewares/auth_middleware.py
import jwt
from functools import wraps
from flask import request, jsonify
from config import Config

# -----------------------------------------------------
# 🔐 Función central para decodificar token
# -----------------------------------------------------
def _decode_token(token):
    if not Config.SECRET_KEY:
        raise jwt.InvalidTokenError("SECRET_KEY no configurada")

    return jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])


# -----------------------------------------------------
# ✅ Middleware general: requiere token
# -----------------------------------------------------
def token_requerido(f):
    @wraps(f)
    def decorador(*args, **kwargs):

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"mensaje": "Token requerido"}), 401

        if not auth_header.startswith("Bearer "):
            return jsonify({"mensaje": "Formato de token inválido"}), 401

        token = auth_header.split(" ")[1]

        try:
            usuario_actual = _decode_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"mensaje": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"mensaje": "Token inválido"}), 401

        return f(usuario_actual, *args, **kwargs)

    return decorador


# -----------------------------------------------------
# 🔥 SOLO ADMIN
# -----------------------------------------------------
def solo_admin(f):
    @wraps(f)
    def decorador(*args, **kwargs):

        # Permitir preflight CORS
        if request.method == "OPTIONS":
            return "", 200

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"error": "Token requerido"}), 401

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Formato de token inválido"}), 401

        token = auth_header.split(" ")[1]

        try:
            payload = _decode_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 401

        if payload.get("rol") != "admin":
            return jsonify({"error": "No autorizado"}), 403

        return f(payload, *args, **kwargs)

    return decorador