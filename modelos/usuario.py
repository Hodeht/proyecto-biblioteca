from sqlalchemy import Column, Integer, String
from modelos.base import Base


class Usuario(Base):

    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(150), nullable=False)
    cedula = Column(String(20), nullable=False, unique=True)
    telefono = Column(String(20), nullable=True)
    direccion = Column(String(200), nullable=True)