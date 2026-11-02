from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


def obtener_engine_mysql(
    host='localhost',
    usuario='root',
    clave='',
    base_datos='biblioteca_leon',
    puerto=3307,
    depuracion=False
):

    url = (
        f"mysql+mysqlconnector://{usuario}:{clave}"
        f"@{host}:{puerto}/{base_datos}"
    )

    engine = create_engine(
        url,
        echo=depuracion
    )

    return engine


# Crear el motor de conexión
engine = obtener_engine_mysql()


# Configuración de sesiones
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


# Base para todos los modelos ORM
Base = declarative_base()


# Función para obtener una sesión
def obtener_sesion():
    return SessionLocal()


if __name__ == "__main__":
    try:
        with engine.connect() as conexion:
            print("¡Conexión ORM exitosa!")

    except Exception as e:
        print("Error de conexión:", e)