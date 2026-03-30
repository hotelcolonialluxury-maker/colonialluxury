import os
from dotenv import load_dotenv
import pymysql
from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.exceptions import HTTPException
from config import Config
from models import db
from werkzeug.security import generate_password_hash

load_dotenv()
pymysql.install_as_MySQLdb()

# ================== MODELOS ==================
from models.usuario import Usuario
from models.habitacion import Habitacion
from models.reserva import Reserva
from models.pago import Pago
from models.contacto import Contacto
from models.comentario import Comentario
from models.configuracion import Configuracion

# ================== RUTAS ==================
from routes.usuario_routes import usuario_routes
from routes.habitacion_routes import habitacion_routes
from routes.auth_routes import auth_routes
from routes.reserva_routes import reserva_routes
from routes.pago_routes import pago_routes
from routes.contacto_routes import contacto_routes
from routes.comentario_routes import comentario_routes
from routes.admin_routes import admin_routes
from routes.public_routes import public_routes

migrate = Migrate()


def _env_true(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


# ================== ADMIN POR DEFECTO ==================
def crear_admin_por_defecto():
    admin_email = "admin@hotel.com"
    admin_nombre = "Administrador"
    admin_password = "admin123"

    try:
        admin_existente = Usuario.query.filter_by(email=admin_email).first()
        if admin_existente:
            print("Admin ya existe")
            return

        nuevo_admin = Usuario(
            nombre=admin_nombre,
            email=admin_email,
            password=generate_password_hash(admin_password),
            rol="admin"
        )
        db.session.add(nuevo_admin)
        db.session.commit()
        print("Admin creado")
    except IntegrityError:
        db.session.rollback()
        print("Admin ya existe")
    except Exception as exc:
        db.session.rollback()
        print(f"No se pudo crear el admin por defecto: {exc}")


def inicializar_base_de_datos(app):
    with app.app_context():
        db.create_all()
        crear_admin_por_defecto()


def registrar_manejadores_error(app):
    @app.errorhandler(SQLAlchemyError)
    def manejar_error_sqlalchemy(exc):
        db.session.rollback()
        app.logger.exception("Error de base de datos en %s %s", request.method, request.path)
        if request.path.startswith("/api/"):
            return jsonify({"error": "Error de base de datos"}), 500
        return "Error de base de datos", 500

    @app.errorhandler(Exception)
    def manejar_error_general(exc):
        if isinstance(exc, HTTPException):
            return exc

        app.logger.exception("Error inesperado en %s %s", request.method, request.path)
        if request.path.startswith("/api/"):
            return jsonify({"error": "Error interno del servidor"}), 500
        return "Error interno del servidor", 500


# ================== FACTORY ==================
def create_app(auto_init_db=None):
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates"
    )

    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(app)
    migrate.init_app(app, db)

    # -------- Blueprints API --------
    app.register_blueprint(public_routes)
    app.register_blueprint(usuario_routes, url_prefix="/api")
    app.register_blueprint(habitacion_routes, url_prefix="/api")
    app.register_blueprint(auth_routes, url_prefix="/api/auth")
    app.register_blueprint(reserva_routes, url_prefix="/api")
    app.register_blueprint(pago_routes, url_prefix="/api")
    app.register_blueprint(admin_routes)
    app.register_blueprint(comentario_routes, url_prefix="/api")
    app.register_blueprint(contacto_routes, url_prefix="/api")

    registrar_manejadores_error(app)

    # -------- INDEX REAL --------
    @app.route("/")
    def index():
        return render_template("index.html")

    # -------- LOGIN / ADMIN (si existen) --------
    @app.route("/login")
    def login():
        return render_template("login.html")

    @app.route("/login.html")
    def login_html():
        return redirect(url_for("login"))

    @app.route("/admin")
    def admin():
        return render_template("admin.html")

    if auto_init_db is None:
        # En Render se activa automaticamente; localmente se puede forzar con AUTO_INIT_DB=true
        auto_init_db = _env_true(
            os.getenv("AUTO_INIT_DB"),
            default=_env_true(os.getenv("RENDER"), default=False) or __name__ == "__main__"
        )

    if auto_init_db:
        inicializar_base_de_datos(app)

    return app


# Objeto WSGI para gunicorn/render
app = create_app()

# ================== RUN ==================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
