from flask import Blueprint, request, jsonify
from models import db
from models.comentario import Comentario
from datetime import datetime
from middlewares.auth_middleware import solo_admin

comentario_routes = Blueprint("comentario_routes", __name__)

# ✅ Obtener comentarios aprobados
@comentario_routes.route("/comentarios", methods=["GET"])
def obtener_comentarios():
    try:
        comentarios = Comentario.query.filter_by(estado="aprobado").all()
        resultado = [
            {
                "id": c.id,
                "nombre": c.nombre,
                "email": c.email,
                "rating": c.rating,
                "texto": c.texto,
                "fecha": c.fecha.strftime("%Y-%m-%d %H:%M:%S"),
                "estado": c.estado
            }
            for c in comentarios
        ]
        return jsonify(resultado), 200
    except Exception as e:
        print("❌ ERROR en GET /api/comentarios:", e)
        return jsonify({"error": "Error al obtener comentarios"}), 500


# ✅ Crear nuevo comentario (pendiente por aprobar)
@comentario_routes.route("/comentarios", methods=["POST"])
def crear_comentario():
    try:
        data = request.get_json(silent=True) or {}
        nombre = data.get("nombre")
        email = data.get("email")
        rating = data.get("rating")
        texto = data.get("texto")

        if not nombre or not email or not texto:
            return jsonify({"error": "Faltan datos obligatorios"}), 400

        nuevo = Comentario(
            nombre=nombre,
            email=email,
            rating=int(rating) if rating else 5,
            texto=texto,
            fecha=datetime.now(),
            estado="pendiente"
        )

        db.session.add(nuevo)
        db.session.commit()
        return jsonify({"mensaje": "Comentario enviado correctamente"}), 201

    except Exception as e:
        print("❌ ERROR en POST /api/comentarios:", e)
        db.session.rollback()
        return jsonify({"error": "Error interno al guardar el comentario"}), 500


# ========================
# 🔐 RUTAS DE ADMINISTRACIÓN
# ========================

# ✅ Obtener TODOS los comentarios (para el panel admin)
@comentario_routes.route("/admin/comentarios", methods=["GET"])
@solo_admin
def obtener_todos_comentarios(usuario_actual):
    try:
        comentarios = Comentario.query.order_by(Comentario.fecha.desc()).all()
        resultado = [
            {
                "id": c.id,
                "nombre": c.nombre,
                "email": c.email,
                "rating": c.rating,
                "texto": c.texto,
                "fecha": c.fecha.strftime("%Y-%m-%d %H:%M:%S"),
                "estado": c.estado
            }
            for c in comentarios
        ]
        return jsonify(resultado), 200
    except Exception as e:
        print("❌ ERROR en GET /admin/comentarios:", e)
        return jsonify({"error": "Error al obtener comentarios"}), 500


# ✅ Aprobar comentario
@comentario_routes.route("/admin/comentarios/<int:id>/aprobar", methods=["PUT"])
@solo_admin
def aprobar_comentario(usuario_actual, id):
    try:
        comentario = Comentario.query.get(id)
        if not comentario:
            return jsonify({"error": "Comentario no encontrado"}), 404
        
        comentario.estado = "aprobado"
        db.session.commit()
        return jsonify({"mensaje": "Comentario aprobado"}), 200
    except Exception as e:
        print("❌ ERROR en PUT aprobar:", e)
        db.session.rollback()
        return jsonify({"error": "Error al aprobar comentario"}), 500


# ✅ Rechazar comentario
@comentario_routes.route("/admin/comentarios/<int:id>/rechazar", methods=["PUT"])
@solo_admin
def rechazar_comentario(usuario_actual, id):
    try:
        comentario = Comentario.query.get(id)
        if not comentario:
            return jsonify({"error": "Comentario no encontrado"}), 404
        
        comentario.estado = "rechazado"
        db.session.commit()
        return jsonify({"mensaje": "Comentario rechazado"}), 200
    except Exception as e:
        print("❌ ERROR en PUT rechazar:", e)
        db.session.rollback()
        return jsonify({"error": "Error al rechazar comentario"}), 500


# ✅ Eliminar comentario
@comentario_routes.route("/admin/comentarios/<int:id>", methods=["DELETE"])
@solo_admin
def eliminar_comentario(usuario_actual, id):
    try:
        comentario = Comentario.query.get(id)
        if not comentario:
            return jsonify({"error": "Comentario no encontrado"}), 404
        
        db.session.delete(comentario)
        db.session.commit()
        return jsonify({"mensaje": "Comentario eliminado"}), 200
    except Exception as e:
        print("❌ ERROR en DELETE:", e)
        db.session.rollback()
        return jsonify({"error": "Error al eliminar comentario"}), 500
