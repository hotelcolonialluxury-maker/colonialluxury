from models.contacto import Contacto

class ContactoController:

    @staticmethod
    def obtener_contactos():
        try:
            return Contacto.obtener_todos()
        except Exception as e:
            print(f"Error al obtener contactos: {e}")
            return []

    @staticmethod
    def crear_contacto(data):
        try:
            nombre = data.get("nombre")
            mensaje = data.get("mensaje")
            email = data.get("email")
            telefono = data.get("telefono")
            asunto = data.get("asunto")

            if not nombre or not mensaje:
                return False  # Validación obligatoria

            return Contacto.crear(nombre, mensaje, email, telefono, asunto)
        except Exception as e:
            print(f"Error al crear contacto: {e}")
            return False

    @staticmethod
    def cambiar_estado(id, nuevo_estado):
        try:
            return Contacto.cambiar_estado(id, nuevo_estado)
        except Exception as e:
            print(f"Error al cambiar estado del contacto: {e}")
            return False

    @staticmethod
    def eliminar_contacto(id):
        try:
            return Contacto.eliminar(id)
        except Exception as e:
            print(f"Error al eliminar contacto: {e}")
            return False