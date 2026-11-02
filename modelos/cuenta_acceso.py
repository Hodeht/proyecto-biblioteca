from sqlalchemy import Column, Integer, String, Enum, Boolean
from modelos.base import Base


class Cuenta(Base):

    __tablename__ = "cuentas_acceso"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    usuario = Column(String(50), nullable=False, unique=True)
    clave = Column(String(255), nullable=False)

    rol = Column(
        Enum("administrador", "bibliotecario"),
        nullable=False
    )

    activo = Column(Boolean, nullable=False, default=True)