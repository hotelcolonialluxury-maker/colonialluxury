from app import app
from models import db   # asegúrate que aquí está tu db

with app.app_context():
    db.create_all()
    print("✅ Tablas creadas correctamente")