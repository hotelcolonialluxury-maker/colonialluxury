from models import db
from models.comentario import Comentario
from datetime import datetime

class ComentarioController:
    # 🟢 Obtener comentarios aprobados
    @staticmethod
    def obtener_comentarios():
        try:
            comentarios = Comentario.query.filter_by(estado="aprobado").all()
            return [
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
        except Exception as e:
            print("❌ ERROR en obtener_comentarios:", e)
            return []

    # 🟡 Crear nuevo comentario (queda pendiente hasta aprobación)
    @staticmethod
    def crear_comentario(data):
        try:
            nombre = data.get("nombre")
            email = data.get("email")
            rating = data.get("rating")
            texto = data.get("texto")

            if not nombre or not email or not texto:
                return None  # Datos incompletos

            nuevo_comentario = Comentario(
                nombre=nombre,
                email=email,
                rating=int(rating) if rating else 5,
                texto=texto,
                fecha=datetime.now(),
                estado="pendiente"
            )

            db.session.add(nuevo_comentario)
            db.session.commit()
            return nuevo_comentario
        except Exception as e:
            print("❌ ERROR en crear_comentario:", e)
            db.session.rollback()
            return None

    # 🟠 Cambiar estado (aprobar o rechazar un comentario)
    @staticmethod
    def cambiar_estado(id_comentario, nuevo_estado):
        try:
            comentario = Comentario.query.get(id_comentario)
            if not comentario:
                return None
            comentario.estado = nuevo_estado
            db.session.commit()
            return comentario
        except Exception as e:
            print("❌ ERROR en cambiar_estado:", e)
            db.session.rollback()
            return None