from base_datos.conexion_orm import engine, Base

# Importar todos los modelos
from modelos.usuario import Usuario
from modelos.libro import Libro
from modelos.prestamo import Prestamo
from modelos.cuenta_acceso import Cuenta
from modelos.incidencia_libros import IncidenciaLibro

from sqlalchemy import text


def probar_orm():
    try:
        with engine.connect() as conexion:
            conexion.execute(text("SELECT 1"))

        print("¡Conexión ORM exitosa!")
        print("\nModelos reconocidos:")

        for tabla in Base.metadata.sorted_tables:
            print(f"- {tabla.name}")

        print("\n¡Prueba ORM completada!")

    except Exception as error:
        print("Error en la prueba ORM:")
        print(error)


if __name__ == "__main__":
    probar_orm()