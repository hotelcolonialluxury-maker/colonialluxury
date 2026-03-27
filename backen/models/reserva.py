from models import db
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.habitacion import Habitacion

class Reserva(db.Model):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)  # ahora puede ser None
    habitacion_id = Column(Integer, ForeignKey("habitaciones.id"), nullable=False)

    fecha_entrada = Column(Date, nullable=False)
    fecha_salida = Column(Date, nullable=False)
    num_personas = Column(Integer, nullable=False)
    precio_total = Column(Float, nullable=False)
    estado = Column(String(50), default="pendiente")
    metodo_pago = Column(String(50), default="no asignado")
    notas = Column(String(255), nullable=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    telefono = Column(String(50), nullable=False)
    identificacion = Column(String(50), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now)

    # Relaciones
    usuario = relationship("Usuario", backref="reservas")
    habitacion = relationship("Habitacion", backref="reservas")

    # ------------------------------------------------------------
    # 🔹 Crear reserva
    # ------------------------------------------------------------
    @staticmethod
    def crear_reserva(usuario_id, habitacion_id, fecha_entrada, fecha_salida, num_personas, nombre, email, telefono, identificacion, notas=""):
        try:
            # Convertir strings a date si es necesario
            if isinstance(fecha_entrada, str):
                fecha_entrada = datetime.strptime(fecha_entrada, "%Y-%m-%d").date()
            if isinstance(fecha_salida, str):
                fecha_salida = datetime.strptime(fecha_salida, "%Y-%m-%d").date()

            # Validación de fechas
            if fecha_entrada >= fecha_salida:
                return "La fecha de salida debe ser mayor que la de entrada."

            # Validar disponibilidad
            conflicto = Reserva.query.filter(
                Reserva.habitacion_id == habitacion_id,
                Reserva.fecha_salida > fecha_entrada,
                Reserva.fecha_entrada < fecha_salida
            ).first()

            if conflicto:
                return "La habitación no está disponible en esas fechas."

            # Cargar habitación
            habitacion = Habitacion.query.get(habitacion_id)
            if not habitacion:
                return "Habitación no encontrada."

            dias = (fecha_salida - fecha_entrada).days
            precio_total = dias * habitacion.precio

            # Crear reserva
            reserva = Reserva(
                usuario_id=usuario_id,
                habitacion_id=habitacion_id,
                fecha_entrada=fecha_entrada,
                fecha_salida=fecha_salida,
                num_personas=num_personas,
                notas=notas,
                nombre=nombre,
                email=email,
                telefono=telefono,
                identificacion=identificacion,
                precio_total=precio_total
            )

            db.session.add(reserva)
            db.session.commit()
            return reserva.id  # devolvemos el id para el redirect

        except Exception as e:
            print(f"Error al crear la reserva: {e}")
            db.session.rollback()
            return False

    # ------------------------------------------------------------
    # 🔹 Obtener todas las reservas
    # ------------------------------------------------------------
    @staticmethod
    def obtener_todas():
        return Reserva.query.order_by(Reserva.fecha_creacion.desc()).all()

    # ------------------------------------------------------------
    # 🔹 Actualizar estado
    # ------------------------------------------------------------
    @staticmethod
    def actualizar_estado(id, nuevo_estado):
        try:
            reserva = Reserva.query.get(id)
            if not reserva:
                return False

            reserva.estado = nuevo_estado
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False