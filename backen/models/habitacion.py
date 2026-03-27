from models import db
from sqlalchemy import Column, Integer, String, Text, Float, func, cast
from sqlalchemy.exc import IntegrityError

class Habitacion(db.Model):
    __tablename__ = "habitaciones"

    id = Column(Integer, primary_key=True)
    codigo = Column(String(10), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    precio = Column(Float, nullable=False)
    capacidad = Column(Integer, nullable=False)
    tipo = Column(String(50), nullable=False)
    estado = Column(String(50), default="disponible")
    imagen = Column(String(255), nullable=True)

    # =========================
    # CREAR
    # =========================
    @staticmethod
    def crear_habitacion(data):
        try:
            if not data:
                return {"error": "No se proporcionaron datos"}

            tipo_abrev = data["tipo"][:3].upper()

            codigo = data.get("codigo")
            if not codigo:
                ultimo = (
                    db.session.query(
                        func.coalesce(
                            func.max(
                                cast(func.substr(Habitacion.codigo, 5), Integer)
                            ), 0
                        )
                    )
                    .filter(Habitacion.codigo.like(f"{tipo_abrev}-%"))
                    .scalar()
                )
                codigo = f"{tipo_abrev}-{ultimo + 1:03d}"

            if Habitacion.query.filter_by(codigo=codigo).first():
                return {"error": "El código ya existe"}

            nueva = Habitacion(
                codigo=codigo,
                nombre=data["nombre"],
                descripcion=data.get("descripcion"),
                precio=float(data["precio"]),
                capacidad=int(data["capacidad"]),
                tipo=data["tipo"],
                estado=data.get("estado", "disponible"),
                imagen=data.get("imagen")  # 👈 Guardamos solo el nombre del archivo
            )

            db.session.add(nueva)
            db.session.commit()
            return nueva.id

        except IntegrityError as e:
            db.session.rollback()
            return {"error": f"Error de integridad: {str(e)}"}
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al crear habitación: {str(e)}"}

    # =========================
    # OBTENER
    # =========================
    @staticmethod
    def obtener_todas():
        return Habitacion.query.all()

    @staticmethod
    def obtener_por_id(id):
        return Habitacion.query.get(id)

    # =========================
    # ACTUALIZAR
    # =========================
    @staticmethod
    def actualizar_habitacion(id, data):
        habitacion = Habitacion.query.get(id)
        if not habitacion:
            return False

        habitacion.nombre = data.get("nombre", habitacion.nombre)
        habitacion.descripcion = data.get("descripcion", habitacion.descripcion)
        habitacion.precio = float(data.get("precio", habitacion.precio))
        habitacion.capacidad = int(data.get("capacidad", habitacion.capacidad))
        habitacion.tipo = data.get("tipo", habitacion.tipo)
        habitacion.estado = data.get("estado", habitacion.estado)

        if data.get("imagen"):
            habitacion.imagen = data["imagen"]

        db.session.commit()
        return True

    # =========================
    # ELIMINAR
    # =========================
    @staticmethod
    def eliminar_habitacion(id):
        habitacion = Habitacion.query.get(id)
        if not habitacion:
            return False

        db.session.delete(habitacion)
        db.session.commit()
        return True

    # =========================
    # URL DINÁMICA
    # =========================
    @property
    def imagen_url(self):
        """Retorna la URL completa de la imagen o None"""
        if not self.imagen:
            return None
        
        # Si ya es una URL completa, retornarla tal cual
        if self.imagen.startswith("http"):
            return self.imagen
        
        # Si es un nombre de archivo, construir la ruta
        return f"/static/uploads/habitaciones/{self.imagen}"

    # =========================
    # JSON
    # =========================
    def to_dict(self):
        return {
            "id": self.id,
            "codigo": self.codigo,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "precio": self.precio,
            "capacidad": self.capacidad,
            "tipo": self.tipo,
            "estado": self.estado,
            "imagen": self.imagen,  # Nombre del archivo
            "imagen_url": self.imagen_url  # URL completa para el frontend
        }