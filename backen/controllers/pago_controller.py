from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode
import hashlib
import uuid

from models import db
from models.pago import Pago
from models.reserva import Reserva
from config import Config


class PagoController:

    @staticmethod
    def obtener_pagos():
        pagos = Pago.query.order_by(Pago.fecha.desc()).all()
        return [p.to_dict() for p in pagos]

    @staticmethod
    def _normalizar_monto(monto):
        try:
            valor = Decimal(str(monto))
        except (InvalidOperation, TypeError, ValueError):
            return None

        if valor <= 0:
            return None

        return float(valor)

    @staticmethod
    def crear_pago(data):
        data = data or {}

        reserva_id = data.get("reserva_id")
        metodo = (data.get("metodo") or "").strip().lower()

        if not reserva_id:
            return {"ok": False, "error": "reserva_id es obligatorio"}

        try:
            reserva_id = int(reserva_id)
        except (TypeError, ValueError):
            return {"ok": False, "error": "reserva_id invalido"}

        if metodo not in {"tarjeta", "transferencia"}:
            return {"ok": False, "error": "Metodo de pago invalido"}

        reserva = Reserva.query.get(reserva_id)
        if not reserva:
            return {"ok": False, "error": "Reserva no encontrada"}

        # El monto siempre se toma de la reserva para evitar manipulaciones desde frontend.
        monto = PagoController._normalizar_monto(reserva.precio_total)
        if monto is None:
            return {"ok": False, "error": "Monto de reserva invalido"}

        try:
            pago = Pago(
                reserva_id=reserva_id,
                monto=monto,
                metodo=metodo,
                estado="pendiente"
            )
            db.session.add(pago)
            db.session.commit()

            if metodo == "tarjeta" and not pago.referencia:
                pago.referencia = f"PAGO-{pago.id}-{uuid.uuid4().hex[:8]}".upper()
                db.session.commit()

            return {"ok": True, "pago": pago}
        except Exception as e:
            db.session.rollback()
            return {"ok": False, "error": f"No se pudo crear el pago: {e}"}

    @staticmethod
    def generar_checkout_wompi(pago):
        public_key = Config.WOMPI_PUBLIC_KEY
        integrity_key = Config.WOMPI_INTEGRITY_KEY

        if not public_key or not integrity_key:
            return {
                "ok": False,
                "error": "Wompi no esta configurado. Falta WOMPI_PUBLIC_KEY o WOMPI_INTEGRITY_KEY"
            }

        reference = pago.referencia or f"PAGO-{pago.id}"
        if not pago.referencia:
            pago.referencia = reference
            db.session.commit()

        amount_in_cents = int(round(float(pago.monto) * 100))
        currency = "COP"

        cadena = f"{reference}{amount_in_cents}{currency}{integrity_key}"
        firma = hashlib.sha256(cadena.encode("utf-8")).hexdigest()

        params = {
            "public-key": public_key,
            "currency": currency,
            "amount-in-cents": amount_in_cents,
            "reference": reference,
            "signature:integrity": firma,
            "redirect-url": Config.WOMPI_REDIRECT_URL,
        }

        checkout_url = f"{Config.WOMPI_CHECKOUT_URL}?{urlencode(params)}"

        return {
            "ok": True,
            "url": checkout_url,
            "referencia": reference,
            "amount_in_cents": amount_in_cents,
        }

    @staticmethod
    def actualizar_estado(pago_id, estado, referencia_externa=None):
        pago = Pago.query.get(pago_id)
        if not pago:
            return False

        pago.estado = estado
        if referencia_externa:
            pago.comprobante = referencia_externa

        if estado == "pagado" and pago.reserva:
            pago.reserva.estado = "confirmada"
            pago.reserva.metodo_pago = pago.metodo

        db.session.commit()
        return True

    @staticmethod
    def actualizar_estado_por_referencia(referencia, estado, referencia_externa=None):
        pago = Pago.query.filter_by(referencia=referencia).first()

        if not pago and str(referencia).isdigit():
            pago = Pago.query.get(int(referencia))

        if not pago:
            return False

        pago.estado = estado
        if referencia_externa:
            pago.comprobante = referencia_externa

        if estado == "pagado" and pago.reserva:
            pago.reserva.estado = "confirmada"
            pago.reserva.metodo_pago = pago.metodo

        db.session.commit()
        return True

    @staticmethod
    def actualizar_pago(pago_id, data):
        data = data or {}
        pago = Pago.query.get(pago_id)
        if not pago:
            return False

        nuevo_estado = data.get("estado")
        if nuevo_estado:
            pago.estado = nuevo_estado

        nuevo_metodo = data.get("metodo")
        if nuevo_metodo in {"tarjeta", "transferencia"}:
            pago.metodo = nuevo_metodo

        nuevo_monto = data.get("monto")
        if nuevo_monto is not None:
            monto = PagoController._normalizar_monto(nuevo_monto)
            if monto is None:
                return False
            pago.monto = monto

        db.session.commit()
        return True

    @staticmethod
    def eliminar_pago(pago_id):
        pago = Pago.query.get(pago_id)
        if not pago:
            return False

        db.session.delete(pago)
        db.session.commit()
        return True
