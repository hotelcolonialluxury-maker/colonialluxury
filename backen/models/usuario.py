from models import db
from sqlalchemy import Column, Integer, String
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    rol = Column(String(20), default='cliente', nullable=False)
    telefono = Column(String(50), nullable=True)
    identificacion = Column(String(50), nullable=True)

    # ----------------------------------------------------
    # 🔹 Crear usuario
    
    # ----------------------------------------------------
    @staticmethod
    def crear_usuario(nombre, email, password, rol='cliente', telefono=None, identificacion=None):
        try:
            hashed = generate_password_hash(password)
            nuevo_usuario = Usuario(
                nombre=nombre,
                email=email,
                password=hashed,
                rol=rol,
                telefono=telefono,
                identificacion=identificacion
            )
            db.session.add(nuevo_usuario)
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error al crear usuario: {e}")
            db.session.rollback()
            return False

    # ----------------------------------------------------
    # 🔹 Obtener todos los usuarios
    # ----------------------------------------------------
    @staticmethod
    def obtener_todos():
        try:
            usuarios = Usuario.query.all()
            return [u.to_dict() for u in usuarios]
        except Exception as e:
            print(f"Error al obtener usuarios: {e}")
            return []

    # ----------------------------------------------------
    # 🔹 Obtener usuario por ID
    # ----------------------------------------------------
    @staticmethod
    def obtener_por_id(id):
        try:
            return Usuario.query.get(id)
        except Exception as e:
            print(e)
            return None

    # 🔹 Obtener usuario por Email (para login)
    # ----------------------------------------------------
    @staticmethod
    def obtener_por_email(email):
        try:
            return Usuario.query.filter_by(email=email).first()
        except Exception as e:
            print(f"Error al obtener usuario por email: {e}")
            return None

    # ----------------------------------------------------
    # 🔹 Actualizar usuario
    # ----------------------------------------------------
    @staticmethod
    def actualizar_usuario(id, data):
        try:
            usuario = Usuario.query.get(id)
            if not usuario:
                return False
            usuario.nombre = data.get("nombre", usuario.nombre)
            usuario.email = data.get("email", usuario.email)
            if data.get("password"):
                usuario.password = generate_password_hash(data.get("password"))
            usuario.rol = data.get("rol", usuario.rol)
            usuario.telefono = data.get("telefono", usuario.telefono)
            usuario.identificacion = data.get("identificacion", usuario.identificacion)
            db.session.commit()
            return True
        except Exception as e:
            print(e)
            db.session.rollback()
            return False

    # ----------------------------------------------------
    # 🔹 Eliminar usuario
    # ----------------------------------------------------
    @staticmethod
    def eliminar_usuario(id):
        try:
            usuario = Usuario.query.get(id)
            if not usuario:
                return False
            db.session.delete(usuario)
            db.session.commit()
            return True
        except Exception as e:
            print(e)
            db.session.rollback()
            return False

    # ----------------------------------------------------
    # 🔹 Verificar contraseña
    # ----------------------------------------------------
    def check_password(self, pwd):
        try:
            return check_password_hash(self.password, pwd)
        except ValueError:
            return False
    # ----------------------------------------------------
    # 🔹 Convertir a dict
    # ----------------------------------------------------
    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email,
            "rol": self.rol,
            "telefono": self.telefono,
            "identificacion": self.identificacion
        }
    

    def get_id(self):
        return str(self.id)