from models import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text,Boolean

class Contacto(db.Model):
    __tablename__ = 'contactos'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(150), nullable=False)
    apellido = Column(String(100))
    email = Column(String(150), nullable=True)
    telefono = Column(String(20), nullable=True)
    asunto = Column(String(200), nullable=True)
    mensaje = Column(Text, nullable=False)
    estado = Column(String(50), default="pendiente")
    leido = Column(Boolean, default=False)   # 👈 NUEVO
    fecha_creacion = Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email,
            "telefono": self.telefono,
            "asunto": self.asunto,
            "mensaje": self.mensaje,
            "estado": self.estado,
            "leido": self.leido,
            "fecha": self.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S")
        }

    @staticmethod
    def crear(nombre, mensaje, email=None, telefono=None, asunto=None):
        try:
            nuevo = Contacto(
                nombre=nombre,
                email=email,
                telefono=telefono,
                asunto=asunto,
                mensaje=mensaje
            )
            db.session.add(nuevo)
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error creando contacto: {e}")
            db.session.rollback()
            return False

    @staticmethod
    def obtener_todos():
        contactos = Contacto.query.order_by(Contacto.id.desc()).all()
        return [c.to_dict() for c in contactos]

    @staticmethod
    def cambiar_estado(id, nuevo_estado):
        try:
            c = Contacto.query.get(id)
            if not c:
                return False
            c.estado = nuevo_estado
            db.session.commit()
            return True
        except Exception as e:
            print(e)
            db.session.rollback()
            return False

    @staticmethod
    def eliminar(id):
        try:
            c = Contacto.query.get(id)
            if not c:
                return False
            db.session.delete(c)
            db.session.commit()
            return True
        except Exception as e:
            print(e)
            db.session.rollback()
            return False
