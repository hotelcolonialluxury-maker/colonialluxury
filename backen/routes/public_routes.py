from flask import Blueprint, jsonify, render_template
from models.configuracion import Configuracion

public_routes = Blueprint("public_routes", __name__)

# =========================
# 🏠 INDEX (HTML)
# =========================
@public_routes.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# =========================
# 🖼️ PORTADA INDEX (API)
# =========================
@public_routes.route("/api/portada", methods=["GET"])
def obtener_portada():
    imagen = Configuracion.get("portada_index")

    if not imagen:
        return jsonify({"imagen": ""})

    return jsonify({
        "imagen": f"/static/uploads/portada/{imagen}"
    })