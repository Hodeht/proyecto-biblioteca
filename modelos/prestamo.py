from sqlalchemy import Column, Integer, String, Date
from modelos.base import Base


class Prestamo(Base):

    __tablename__ = "prestamos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo_prestamo = Column(String(20), nullable=False)
    codigo_libro = Column(String(20), nullable=False)
    libro = Column(String(200), nullable=False)
    usuario = Column(String(150), nullable=False)
    fecha_prestamo = Column(Date, nullable=False)
    fecha_devolucion = Column(Date, nullable=False)
    estado = Column(String(50), nullable=False)
    cedula_usuario = Column(String(30), nullable=True)