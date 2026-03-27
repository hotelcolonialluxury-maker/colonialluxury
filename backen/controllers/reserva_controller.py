# controllers/reserva_controller.py
from models import db
from models.reserva import Reserva
from models.usuario import Usuario
from models.habitacion import Habitacion
from datetime import datetime
from config import Config
import smtplib
from email.message import EmailMessage

class ReservaController:

    @staticmethod
    def enviar_email_pago(email_destino, reserva_id, monto, enlace_pago):
        try:
            msg = EmailMessage()
            msg["Subject"] = f"Reserva #{reserva_id} - Pago pendiente"
            msg["From"] = Config.EMAIL_FROM
            msg["To"] = email_destino

            cuerpo = f"""
Hola,

Tu reserva (ID: {reserva_id}) fue creada y está pendiente de pago.
Monto: {monto}
Para completar la reserva, realiza el pago aquí: {enlace_pago}

Después de recibir el pago confirmaremos tu reserva.

Gracias,
Hotel Colonial Luxury
            """
            msg.set_content(cuerpo)

            with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT) as server:
                server.starttls()
                server.login(Config.SMTP_USER, Config.SMTP_PASS)
                server.send_message(msg)

            return True
        except Exception as e:
            print("Error enviando correo:", e)
            return False

    # ----------------------------------------------------------
    # 🔹 Crear reserva
    # ----------------------------------------------------------
    @staticmethod
    def crear_reserva(data, usuario_id=None):
        try:
            if usuario_id is None:
                return {"error": "No autenticado. Inicia sesión para reservar."}, 401

            nombre = data.get("nombre")
            email = data.get("email")
            telefono = data.get("telefono")
            identificacion = data.get("identificacion")

            habitacion_id = data.get("habitacion_id")
            fecha_entrada = data.get("fecha_entrada")
            fecha_salida = data.get("fecha_salida")
            num_personas = int(data.get("num_personas", 1))
            notas = data.get("notas", "")

            if not habitacion_id or not fecha_entrada or not fecha_salida:
                return {"error": "Faltan datos obligatorios."}, 400

            resultado = Reserva.crear_reserva(
                usuario_id,
                habitacion_id,
                fecha_entrada,
                fecha_salida,
                num_personas,
                nombre,
                email,
                telefono,
                identificacion,
                notas
            )

            if isinstance(resultado, int):
                reserva_id = resultado
                reserva_obj = Reserva.query.get(reserva_id)
                monto = reserva_obj.precio_total if reserva_obj else 0
                enlace_pago = f"{Config.FRONTEND_URL}/pago?reserva_id={reserva_id}"

                # Enviar email sin self
                ReservaController.enviar_email_pago(email, reserva_id, monto, enlace_pago)

                return {"message": "Reserva creada correctamente.", "reserva_id": reserva_id}, 201

            elif isinstance(resultado, str):
                return {"error": resultado}, 400

            return {"error": "Error al crear la reserva."}, 500

        except Exception as e:
            print("Error controlador crear_reserva:", e)
            return {"error": "Error interno del servidor."}, 500

    # ----------------------------------------------------------
    # 🔹 Listar todas las reservas (ADMIN)
    # ----------------------------------------------------------
    @staticmethod
    def listar_reservas():
        try:
            reservas = Reserva.query.order_by(Reserva.fecha_entrada.desc()).all()
            lista = []

            for r in reservas:
                lista.append({
                    "id": r.id,
                    "usuario": {
                        "id": r.usuario.id if r.usuario else None,
                        "nombre": r.usuario.nombre if r.usuario else None,
                        "email": r.usuario.email if r.usuario else None
                    },
                    "habitacion": {
                        "id": r.habitacion.id if r.habitacion else None,
                        "nombre": r.habitacion.nombre if r.habitacion else None
                    },
                    "fecha_entrada": r.fecha_entrada.isoformat(),
                    "fecha_salida": r.fecha_salida.isoformat(),
                    "num_personas": r.num_personas,
                    "estado": r.estado,
                    "precio_total": r.precio_total,
                    "nombre": r.nombre,
                    "email": r.email,
                    "telefono": r.telefono,
                    "identificacion": r.identificacion,
                    "notas": r.notas
                })

            return lista

        except Exception as e:
            print("Error controlador listar_reservas:", e)
            return []
        # ----------------------------------------------------------
        # 🔹 Cambiar estado de reserva
        # ----------------------------------------------------------
    @staticmethod
    def cambiar_estado(id, nuevo_estado):
        try:
            return Reserva.actualizar_estado(id, nuevo_estado)
        except Exception as e:
            print(f"Error controlador cambiar_estado: {e}")
            return False