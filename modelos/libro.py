from sqlalchemy import Column, Integer, String
from modelos.base import Base


class Libro(Base):

    __tablename__ = "libros"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(20), nullable=False, unique=True)
    titulo = Column(String(150), nullable=False)
    autor = Column(String(100), nullable=False)
    categoria = Column(String(100), nullable=False)
    estado = Column(String(50), nullable=False)
    anio = Column(Integer, nullable=True)
    edicion = Column(String(50), nullable=True)
    seccion = Column(String(50), nullable=True)
    pasillo = Column(String(20), nullable=True)
    estante = Column(String(20), nullable=True)
    repisa = Column(String(20), nullable=True)