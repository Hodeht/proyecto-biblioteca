from base_datos.conexion_orm import obtener_sesion
from servicios.usuario_servicio import UsuarioServicio


sesion = obtener_sesion()

try:
    print("=== PRUEBA DE CONSULTA DE USUARIOS ===")

    usuarios = UsuarioServicio.obtener_usuarios(sesion)

    print(f"Usuarios encontrados: {len(usuarios)}")

    for usuario in usuarios:
        print(
            usuario.id,
            usuario.nombre,
            usuario.cedula
        )

except Exception as error:
    print("Error:", error)

finally:
    sesion.close()