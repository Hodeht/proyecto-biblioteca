from sqlalchemy import Column, Integer, String, Text, Date
from modelos.base import Base


class IncidenciaLibro(Base):

    __tablename__ = "incidencias_libros"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo_libro = Column(String(20), nullable=False)
    fecha_reporte = Column(Date, nullable=False)
    descripcion = Column(Text, nullable=False)
    estado_incidencia = Column(
        String(30),
        nullable=False,
        default="Por revisar"
    )
    observaciones = Column(Text, nullable=True)
    fecha_resolucion = Column(Date, nullable=True)