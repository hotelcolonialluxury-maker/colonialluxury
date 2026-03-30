from app import create_app, inicializar_base_de_datos

app = create_app(auto_init_db=False)

if __name__ == "__main__":
    inicializar_base_de_datos(app)
    print("Tablas creadas y admin listo")
