from app import create_app
from models import db
from app import crear_admin_por_defecto

app = create_app()

with app.app_context():
    db.create_all()
    crear_admin_por_defecto()
    print("✅ Tablas creadas y admin listo")