from sqlalchemy.orm import Session
from modelos.usuario import Usuario


class UsuarioServicio:

    # CREATE: registrar usuario
    @staticmethod
    def crear_usuario(
        sesion: Session,
        nombre,
        cedula,
        telefono=None,
        direccion=None
    ):
        nuevo_usuario = Usuario(
            nombre=nombre,
            cedula=cedula,
            telefono=telefono,
            direccion=direccion
        )

        sesion.add(nuevo_usuario)
        sesion.commit()
        sesion.refresh(nuevo_usuario)

        return nuevo_usuario

    # READ: consultar todos los usuarios
    @staticmethod
    def obtener_usuarios(sesion: Session):
        return sesion.query(Usuario).all()

    # READ: consultar usuario por ID
    @staticmethod
    def obtener_usuario(sesion: Session, usuario_id):
        return sesion.get(Usuario, usuario_id)

    # UPDATE: actualizar usuario
    @staticmethod
    def actualizar_usuario(
        sesion: Session,
        usuario_id,
        **datos
    ):
        usuario = sesion.get(Usuario, usuario_id)

        if usuario is None:
            return None

        for campo, valor in datos.items():
            if hasattr(usuario, campo):
                setattr(usuario, campo, valor)

        sesion.commit()
        sesion.refresh(usuario)

        return usuario

    # DELETE: eliminar usuario
    @staticmethod
    def eliminar_usuario(sesion: Session, usuario_id):
        usuario = sesion.get(Usuario, usuario_id)

        if usuario is None:
            return False

        sesion.delete(usuario)
        sesion.commit()

        return True