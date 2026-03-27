import os
import uuid
from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename
from models.configuracion import Configuracion
from models import db
from models.usuario import Usuario
from models.habitacion import Habitacion
from models.reserva import Reserva
from models.pago import Pago
from models.comentario import Comentario
from models.contacto import Contacto
from controllers.pago_controller import PagoController
from middlewares.auth_middleware import solo_admin

admin_routes = Blueprint("admin_routes", __name__, url_prefix="/api/admin")

# =====================================================
# 🔹 CONFIG IMÁGENES
# =====================================================
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

def archivo_permitido(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# =====================================================
# 🔹 USUARIOS
# =====================================================
@admin_routes.route("/usuarios", methods=["GET"])
@solo_admin
def get_usuarios(usuario_actual):
    usuarios = Usuario.query.all()
    return jsonify([{
        "id": u.id,
        "nombre": u.nombre,
        "email": u.email,
        "rol": getattr(u, "rol", "usuario")
    } for u in usuarios]), 200


# =====================================================
# 🔹 HABITACIONES (ADMIN)
# =====================================================
@admin_routes.route("/habitaciones", methods=["GET"])
@solo_admin
def get_habitaciones(usuario_actual):
    habitaciones = Habitacion.query.all()
    return jsonify([h.to_dict() for h in habitaciones]), 200


@admin_routes.route("/habitaciones", methods=["POST"])
@solo_admin
def crear_habitacion_admin(usuario_actual):
    data = request.form.to_dict()
    imagen = request.files.get("imagen")

    if not data.get("nombre") or not data.get("tipo"):
        return jsonify({"error": "Datos incompletos"}), 400

    if imagen and archivo_permitido(imagen.filename):
        nombre_seguro = secure_filename(imagen.filename)
        ext = nombre_seguro.rsplit(".", 1)[1].lower()
        nombre_final = f"{uuid.uuid4().hex}.{ext}"

        carpeta = current_app.config.get(
            "UPLOAD_FOLDER",
            os.path.join(current_app.root_path, "static/uploads/habitaciones")
        )
        os.makedirs(carpeta, exist_ok=True)

        imagen.save(os.path.join(carpeta, nombre_final))
        data["imagen"] = nombre_final

    resultado = Habitacion.crear_habitacion(data)

    if isinstance(resultado, dict) and resultado.get("error"):
        return jsonify(resultado), 400

    return jsonify({"msg": "Habitación creada", "id": resultado}), 201


@admin_routes.route("/habitaciones/<int:id>", methods=["PUT"])
@solo_admin
def actualizar_habitacion(usuario_actual, id):
    habitacion = Habitacion.query.get_or_404(id)
    data = request.form.to_dict()
    imagen = request.files.get("imagen")

    habitacion.nombre = data.get("nombre", habitacion.nombre)
    habitacion.descripcion = data.get("descripcion", habitacion.descripcion)
    habitacion.precio = float(data.get("precio", habitacion.precio))
    habitacion.capacidad = int(data.get("capacidad", habitacion.capacidad))
    habitacion.tipo = data.get("tipo", habitacion.tipo)
    habitacion.estado = data.get("estado", habitacion.estado)

    if imagen and archivo_permitido(imagen.filename):
        if habitacion.imagen:
            carpeta = current_app.config.get(
                "UPLOAD_FOLDER",
                os.path.join(current_app.root_path, "static/uploads/habitaciones")
            )
            ruta_antigua = os.path.join(carpeta, habitacion.imagen)
            if os.path.exists(ruta_antigua):
                os.remove(ruta_antigua)

        nombre_seguro = secure_filename(imagen.filename)
        ext = nombre_seguro.rsplit(".", 1)[1].lower()
        nombre_final = f"{uuid.uuid4().hex}.{ext}"

        carpeta = current_app.config.get(
            "UPLOAD_FOLDER",
            os.path.join(current_app.root_path, "static/uploads/habitaciones")
        )
        os.makedirs(carpeta, exist_ok=True)

        imagen.save(os.path.join(carpeta, nombre_final))
        habitacion.imagen = nombre_final

    db.session.commit()

    return jsonify({
        "msg": "Habitación actualizada",
        "imagen": habitacion.imagen,
        "imagen_url": habitacion.imagen_url
    }), 200


@admin_routes.route("/habitaciones/<int:id>", methods=["DELETE"])
@solo_admin
def eliminar_habitacion(usuario_actual, id):
    h = Habitacion.query.get_or_404(id)
    db.session.delete(h)
    db.session.commit()
    return jsonify({"msg": "Habitación eliminada"}), 200


# =====================================================
# 🔹 RESERVAS
# =====================================================
@admin_routes.route("/reservas", methods=["GET"])
@solo_admin
def get_reservas(usuario_actual):
    reservas = Reserva.query.all()
    return jsonify([{
        "id": r.id,
        "usuario": r.usuario.nombre if r.usuario else "N/A",
        "habitacion": r.habitacion.nombre if r.habitacion else "N/A",
        "fecha_entrada": r.fecha_entrada.strftime("%Y-%m-%d"),
        "fecha_salida": r.fecha_salida.strftime("%Y-%m-%d"),
        "num_personas": r.num_personas,
        "precio_total": r.precio_total,
        "estado": r.estado
    } for r in reservas]), 200


@admin_routes.route("/reservas/<int:id>/estado", methods=["PUT"])
@solo_admin
def cambiar_estado_reserva(usuario_actual, id):
    reserva = Reserva.query.get_or_404(id)
    reserva.estado = request.json.get("estado", reserva.estado)
    db.session.commit()
    return jsonify({"msg": "Estado actualizado"}), 200


@admin_routes.route("/reservas/<int:id>", methods=["DELETE"])
@solo_admin
def eliminar_reserva(usuario_actual, id):
    r = Reserva.query.get_or_404(id)
    db.session.delete(r)
    db.session.commit()
    return jsonify({"msg": "Reserva eliminada"}), 200


# =====================================================
# 🔹 PAGOS
# =====================================================
@admin_routes.route("/pagos", methods=["GET"])
@solo_admin
def get_pagos(usuario_actual):
    estado = request.args.get("estado")
    metodo = request.args.get("metodo")

    query = Pago.query

    if estado:
        query = query.filter_by(estado=estado)
    if metodo:
        query = query.filter_by(metodo=metodo)

    pagos = query.order_by(Pago.fecha.desc()).all()

    return jsonify([p.to_dict() for p in pagos]), 200

@admin_routes.route("/pagos/<int:id>/confirmar", methods=["PUT"])
@solo_admin
def confirmar_pago_transferencia(usuario_actual, id):
    pago = Pago.query.get(id)

    if not pago:
        return jsonify({"message": "Pago no encontrado"}), 404

    if pago.metodo != "transferencia":
        return jsonify({"message": "Solo transferencias pueden confirmarse manualmente"}), 400

    if pago.estado == "pagado":
        return jsonify({"message": "Este pago ya fue confirmado"}), 400

    PagoController.actualizar_estado(id, "pagado")

    return jsonify({"message": "Pago confirmado correctamente"}), 200

@admin_routes.route("/pagos/<int:id>/rechazar", methods=["PUT"])
@solo_admin
def rechazar_pago(usuario_actual, id):
    pago = Pago.query.get(id)

    if not pago:
        return jsonify({"message": "Pago no encontrado"}), 404

    if pago.estado == "pagado":
        return jsonify({"message": "No se puede rechazar un pago ya confirmado"}), 400

    PagoController.actualizar_estado(id, "rechazado")

    return jsonify({"message": "Pago rechazado"}), 200

@admin_routes.route("/pagos/<int:id>", methods=["GET"])
@solo_admin
def get_pago(usuario_actual, id):
    pago = Pago.query.get(id)

    if not pago:
        return jsonify({"message": "Pago no encontrado"}), 404

    return jsonify(pago.to_dict()), 200
# =====================================================
# 🔹 COMENTARIOS
# =====================================================
@admin_routes.route("/comentarios", methods=["GET"])
@solo_admin
def get_comentarios(usuario_actual):
    comentarios = Comentario.query.all()
    return jsonify([{
        "id": c.id,
        "nombre": c.nombre,
        "email": c.email,
        "texto": c.texto,
        "rating": c.rating,
        "estado": c.estado,
        "fecha": c.fecha.strftime("%Y-%m-%d %H:%M:%S") if c.fecha else None
    } for c in comentarios]), 200


@admin_routes.route("/comentarios/<int:id>/<accion>", methods=["PUT"])
@solo_admin
def cambiar_estado_comentario(usuario_actual, id, accion):
    comentario = Comentario.query.get_or_404(id)

    if accion == "aprobar":
        comentario.estado = "aprobado"
    elif accion == "rechazar":
        comentario.estado = "rechazado"
    else:
        return jsonify({"error": "Acción inválida"}), 400

    db.session.commit()
    return jsonify({"msg": "Estado actualizado"}), 200


@admin_routes.route("/comentarios/<int:id>", methods=["DELETE"])
@solo_admin
def eliminar_comentario(usuario_actual, id):
    c = Comentario.query.get_or_404(id)
    db.session.delete(c)
    db.session.commit()
    return jsonify({"msg": "Comentario eliminado"}), 200


# =====================================================
# 🔹 CONTACTOS (ADMIN)
# =====================================================
@admin_routes.route("/contactos", methods=["GET"])
@solo_admin
def get_contactos(usuario_actual):
    return jsonify(Contacto.obtener_todos()), 200


@admin_routes.route("/contactos/<int:id>/estado", methods=["PUT"])
@solo_admin
def cambiar_estado_contacto(usuario_actual, id):
    estado = request.json.get("estado")

    if estado not in ["pendiente", "respondido"]:
        return jsonify({"error": "Estado inválido"}), 400

    if not Contacto.cambiar_estado(id, estado):
        return jsonify({"error": "No se pudo actualizar"}), 500

    return jsonify({"msg": "Estado actualizado"}), 200


@admin_routes.route("/contactos/<int:id>", methods=["DELETE"])
@solo_admin
def eliminar_contacto(usuario_actual, id):
    if not Contacto.eliminar(id):
        return jsonify({"error": "No se pudo eliminar"}), 500

    return jsonify({"msg": "Contacto eliminado"}), 200

# =====================================================
# 🔹 PORTADA INDEX
# =====================================================
@admin_routes.route("/portada", methods=["POST"])
@solo_admin
def actualizar_portada(usuario_actual):
    imagen = request.files.get("imagen")

    if not imagen or not archivo_permitido(imagen.filename):
        return jsonify({"error": "Imagen inválida"}), 400

    # 📌 1. Portada anterior
    portada_anterior = Configuracion.get("portada_index")

    # 📌 2. Guardar nueva portada
    nombre_seguro = secure_filename(imagen.filename)
    ext = nombre_seguro.rsplit(".", 1)[1].lower()
    nombre_final = f"portada_{uuid.uuid4().hex}.{ext}"

    carpeta = os.path.join(current_app.static_folder, "uploads", "portada")
    os.makedirs(carpeta, exist_ok=True)

    ruta_nueva = os.path.join(carpeta, nombre_final)
    imagen.save(ruta_nueva)

    # 📌 3. Eliminar portada anterior
    if portada_anterior:
        ruta_anterior = os.path.join(
            current_app.static_folder,
            "uploads",
            "portada",
            portada_anterior
        )

        if os.path.exists(ruta_anterior):
            os.remove(ruta_anterior)

    # 📌 4. Guardar en DB
    Configuracion.set("portada_index", nombre_final)

    return jsonify({
        "msg": "Portada actualizada",
        "imagen": nombre_final
    }), 200

@admin_routes.route("/portada", methods=["GET"])
def obtener_portada():
    nombre = Configuracion.get("portada_index")

    if not nombre:
        return jsonify({"imagen": None}), 200

    return jsonify({
        "imagen": f"/static/uploads/portada/{nombre}"
    }), 200
