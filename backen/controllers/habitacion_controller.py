from models.habitacion import Habitacion


class HabitacionController:

    # =========================
    # CREAR HABITACION
    # =========================
    @staticmethod
    def crear_habitacion(data):
        campos_obligatorios = ["nombre", "precio", "capacidad", "tipo"]

        for campo in campos_obligatorios:
            if not data.get(campo):
                return f"Falta el campo obligatorio: {campo}", False

        resultado = Habitacion.crear_habitacion(data)

        if isinstance(resultado, int):
            return "Habitacion creada correctamente", True

        if isinstance(resultado, dict):
            return resultado.get("error", "Error al crear habitacion"), False

        return "Error al crear habitacion", False

    # =========================
    # OBTENER TODAS
    # =========================
    @staticmethod
    def obtener_habitaciones():
        habitaciones = Habitacion.obtener_todas()
        lista = []

        for h in habitaciones:
            lista.append({
                "id": h.id,
                "nombre": h.nombre,
                "descripcion": h.descripcion,
                "precio": h.precio,
                "capacidad": h.capacidad,
                "tipo": h.tipo,
                "estado": h.estado,
                "imagen": h.imagen,
                "imagen_url": h.imagen_url
            })

        return lista

    # =========================
    # OBTENER POR ID
    # =========================
    @staticmethod
    def obtener_habitacion_por_id(id):
        habitacion = Habitacion.obtener_por_id(id)

        if not habitacion:
            return None

        return {
            "id": habitacion.id,
            "nombre": habitacion.nombre,
            "descripcion": habitacion.descripcion,
            "precio": habitacion.precio,
            "capacidad": habitacion.capacidad,
            "tipo": habitacion.tipo,
            "estado": habitacion.estado,
            "imagen": habitacion.imagen,
            "imagen_url": habitacion.imagen_url
        }

    # =========================
    # ACTUALIZAR
    # =========================
    @staticmethod
    def actualizar_habitacion(id, data):
        return Habitacion.actualizar_habitacion(id, data)

    # =========================
    # ELIMINAR
    # =========================
    @staticmethod
    def eliminar_habitacion(id):
        return Habitacion.eliminar_habitacion(id)
