from models.usuario import Usuario

class UsuarioController:

    # ✅ Crear usuario
    @staticmethod
    def crear_usuario(data):
        data = data or {}
        nombre = data.get("nombre")
        email = data.get("email")
        password = data.get("password")
        rol = data.get("rol", "cliente")
        telefono = data.get("telefono", "")
        identificacion = data.get("identificacion", "")

        if not nombre or not email or not password:
            return {"ok": False, "message": "Faltan datos obligatorios"}

        resultado = Usuario.crear_usuario(nombre, email, password, rol, telefono, identificacion)
        if resultado:
            return {"ok": True, "message": "Usuario creado correctamente"}
        return {"ok": False, "message": "Error al crear usuario"}

    # ✅ Obtener todos los usuarios
    @staticmethod
    def obtener_usuarios():
        return Usuario.obtener_todos()

    # ✅ Obtener usuario por ID
    @staticmethod
    def obtener_usuario_por_id(id):
        usuario = Usuario.obtener_por_id(id)
        if usuario:
            return {
                "id": usuario.id,
                "nombre": usuario.nombre,
                "email": usuario.email,
                "rol": usuario.rol,
                "telefono": getattr(usuario, "telefono", ""),
                "identificacion": getattr(usuario, "identificacion", "")
            }
        return None

    # ✅ Actualizar usuario
    @staticmethod
    def actualizar_usuario(id, data):
        data = data or {}
        resultado = Usuario.actualizar_usuario(id, data)
        if resultado:
            return {"ok": True, "message": "Usuario actualizado correctamente"}
        return {"ok": False, "message": "Error al actualizar usuario"}

    # ✅ Eliminar usuario
    @staticmethod
    def eliminar_usuario(id):
        resultado = Usuario.eliminar_usuario(id)
        if resultado:
            return {"ok": True, "message": "Usuario eliminado correctamente"}
        return {"ok": False, "message": "Usuario no encontrado"}
