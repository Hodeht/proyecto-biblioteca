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
        echo=depuracion,
        pool_pre_ping=True
    
    )

    return engine


engine = obtener_engine_mysql()


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)



Base = declarative_base()



def obtener_sesion():
    return SessionLocal()


if __name__ == "__main__":
    try:
        with engine.connect() as conexion:
            print("¡Conexión ORM exitosa!")

    except Exception as e:
        print("Error de conexión:", e)