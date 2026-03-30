import os
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

# Directorio base del proyecto
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

db_url = os.getenv("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)


class Config:
    # Subidas
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads", "habitaciones")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    # Seguridad
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    # Base de datos
    SQLALCHEMY_DATABASE_URI = db_url or "sqlite:///" + os.path.join(BASE_DIR, "database.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # Frontend
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:5000")

    # Wompi
    WOMPI_PUBLIC_KEY = os.getenv("WOMPI_PUBLIC_KEY")
    WOMPI_INTEGRITY_KEY = os.getenv("WOMPI_INTEGRITY_KEY")
    WOMPI_CHECKOUT_URL = os.getenv("WOMPI_CHECKOUT_URL", "https://checkout.wompi.co/p/")
    WOMPI_REDIRECT_URL = os.getenv("WOMPI_REDIRECT_URL", FRONTEND_URL)

    # SMTP
    SMTP_HOST = os.getenv("SMTP_HOST")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASS = os.getenv("SMTP_PASS")
    EMAIL_FROM = os.getenv("EMAIL_FROM")

