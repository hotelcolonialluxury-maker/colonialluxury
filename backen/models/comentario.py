from models import db
from datetime import datetime
from sqlalchemy import Enum

class Comentario(db.Model):
    __tablename__ = 'comentarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150))
    rating = db.Column(db.Integer)
    texto = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(
        Enum('pendiente', 'aprobado', 'rechazado', name='estado_enum'),
        default='pendiente'
    )

    @staticmethod
    def crear(nombre, email, rating, texto):
        try:
            nuevo = Comentario(
                nombre=nombre,
                email=email,
                rating=rating,
                texto=texto
            )
            db.session.add(nuevo)
            db.session.commit()
            return True
        except Exception as e:
            print("❌ ERROR al crear comentario:", e)
            db.session.rollback()
            return False

    @staticmethod
    def obtener_todos():
        comentarios = Comentario.query.all()
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

    @staticmethod
    def eliminar(id):
        try:
            comentario = Comentario.query.get(id)
            if not comentario:
                return False
            db.session.delete(comentario)
            db.session.commit()
            return True
        except Exception as e:
            print("❌ ERROR al eliminar comentario:", e)
            db.session.rollback()
            return False