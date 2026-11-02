import bcrypt
from base_datos.conexion import conectar

nombre = input("Escribe tu nombre: ")
usuario = input("Crea tu usuario: ")
clave = input("Crea tu contraseña: ")

clave_protegida = bcrypt.hashpw(
    clave.encode("utf-8"),
    bcrypt.gensalt()
).decode("utf-8")

conexion = conectar()
cursor = conexion.cursor()

try:
    cursor.execute(
        """
        INSERT INTO cuentas_acceso
        (nombre, usuario, clave, rol)
        VALUES (%s, %s, %s, %s)
        """,
        (nombre, usuario, clave_protegida, "administrador")
    )

    conexion.commit()
    print("¡Cuenta creada correctamente!")

except Exception as error:
    conexion.rollback()
    print("Error al crear la cuenta:", error)

finally:
    cursor.close()
    conexion.close()