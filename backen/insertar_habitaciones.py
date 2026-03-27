from app import create_app
from models.habitacion import Habitacion
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

# ---------------- Crear instancia de la app ----------------
app = create_app()

# ---------------- Lista de habitaciones a insertar ----------------
habitaciones = [
    # ---------------- Suite ----------------
    {
        "nombre": "Suite Presidencial",
        "descripcion": "Disfruta de nuestra Suite Presidencial con cama king, sala privada, balcón con vista panorámica y todos los lujos que esperas en un hotel de cinco estrellas.",
        "precio": 750000,
        "capacidad": 2,
        "tipo": "suite",
        "imagen_url": "suite.jpg"
    }
]

# 5 Habitaciones Sencillas
for i in range(1, 6):
    habitaciones.append({
        "nombre": f"Habitación Sencilla {i}",
        "descripcion": "Habitación acogedora y elegante con cama individual, ideal para viajes de negocios o estancias cortas.",
        "precio": 250000,
        "capacidad": 1,
        "tipo": "sencilla",
        "imagen_url": "sencilla.jpg"
    })

# 6 Habitaciones Dobles
for i in range(1, 7):
    imagen = "doble1.jpg" if i <= 3 else "doble2.jpg"
    habitaciones.append({
        "nombre": f"Habitación Doble {i}",
        "descripcion": "Habitación amplia con cama doble, elegante decoración y todas las comodidades para una estancia perfecta.",
        "precio": 400000,
        "capacidad": 2,
        "tipo": "doble",
        "imagen_url": imagen
    })

# ---------------- Ejecutar inserción dentro del contexto de la app ----------------
with app.app_context():
    print("🚀 Limpiando códigos vacíos en la base de datos...")
    Habitacion.query.filter((Habitacion.codigo == '') | (Habitacion.codigo == None)).delete()
    from models import db
    db.session.commit()
    print("✅ Códigos vacíos eliminados.")

    print("🚀 Insertando habitaciones nuevas...")
    for data in habitaciones:
        # Verificar si ya existe una habitación con el mismo nombre
        if Habitacion.query.filter_by(nombre=data["nombre"]).first():
            print(f"⚠️ {data['nombre']} ya existe, se omite.")
            continue

        resultado = Habitacion.crear_habitacion(data)
        if isinstance(resultado, int):
            print(f"✅ Habitación creada con ID {resultado} - {data['nombre']}")
        else:
            print(f"❌ Error creando {data['nombre']}: {resultado.get('error')}")
    print("✅ Inserción completada.")