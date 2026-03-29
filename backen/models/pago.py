from models import db
from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, Enum
from datetime import datetime

class Pago(db.Model):
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True)
    reserva_id = Column(Integer, ForeignKey("reservas.id"), nullable=False)
    monto = Column(Float, nullable=False)

    metodo = Column(
        "metodo_pago",
        Enum("tarjeta", "transferencia", name="metodo_pago_enum"),
        nullable=False
    )

    estado = Column(String(50), default="pendiente")

    # 🔑 CLAVE para pagos reales
    referencia = Column(String(200), nullable=True)  # id Wompi
    comprobante = Column(String(255), nullable=True) # transferencia

    fecha = Column("fecha_pago", DateTime, default=datetime.utcnow)

    reserva = db.relationship("Reserva", backref="pagos")

    def to_dict(self):
        return {
            "id": self.id,
            "reserva_id": self.reserva_id,
            "monto": float(self.monto),
            "metodo": self.metodo,
            "estado": self.estado,
            "fecha": self.fecha.strftime("%Y-%m-%d %H:%M:%S") if self.fecha else None,
            "cliente": self.reserva.nombre if self.reserva else "N/A",
            "habitacion": self.reserva.habitacion.nombre if self.reserva and self.reserva.habitacion else "N/A"
        }