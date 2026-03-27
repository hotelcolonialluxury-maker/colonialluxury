import os
from dotenv import load_dotenv
load_dotenv()
from flask import redirect, url_for
from flask import Flask, send_from_directory, render_template
from flask_cors import CORS
from flask_migrate import Migrate
from config import Config
from models import db
from werkzeug.security import generate_password_hash

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

# ================== ADMIN POR DEFECTO ==================

def crear_admin_por_defecto():
    admin_email = "admin@hotel.com"
    admin_nombre = "Administrador"
    admin_password = "admin123"

    admin_existente = Usuario.query.filter_by(email=admin_email).first()
    if not admin_existente:
        nuevo_admin = Usuario(
            nombre=admin_nombre,
            email=admin_email,
            password=generate_password_hash(admin_password),
            rol="admin"
        )
        db.session.add(nuevo_admin)
        db.session.commit()
        print("✅ Admin creado")
    else:
        print("⚙️ Admin ya existe")

# ================== FACTORY ==================
def create_app():
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates"
    )

    app.config.from_object(Config)
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

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

    return app

# ================== RUN ==================
if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        crear_admin_por_defecto()
    app.run(host="0.0.0.0", port=5000, debug=True)
