from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QFrame,
    QPushButton,
    QProgressBar,
    QScrollArea,
    QMessageBox,
    QSizePolicy
)
from PySide6.QtCore import Qt, QUrl
from datetime import date
from sqlalchemy import func, extract
from base_datos.conexion_orm import obtener_sesion
from modelos.prestamo import Prestamo

import os
from PySide6.QtGui import QDesktopServices
from reportes.pdf_service import generar_pdf_estadisticas


class EstadisticasPrestamos(QWidget):

    def __init__(self, volver):
        super().__init__()

        self.volver = volver
        self.setObjectName("paginaEstadisticas")

        self.tarjetas_indicadores = {}
        self.barras_meses = []
        self.barras_libros = []

        principal = QVBoxLayout(self)
        principal.setContentsMargins(30, 20, 30, 20)
        principal.setSpacing(18)

        # ENCABEZADO
        encabezado = QHBoxLayout()

        textos = QVBoxLayout()

        titulo = QLabel("Estadísticas de préstamos")
        titulo.setObjectName("tituloPagina")

        descripcion = QLabel(
            "Consulta el movimiento de los préstamos "
            "y los libros más solicitados."
        )
        descripcion.setObjectName("descripcion")

        textos.addWidget(titulo)
        textos.addWidget(descripcion)

        encabezado.addLayout(textos)
        encabezado.addStretch()

        boton_pdf = QPushButton("Generar PDF")
        boton_pdf.setObjectName("btnPrincipal")
        boton_pdf.clicked.connect(self.generar_reporte_pdf)

        encabezado.addWidget(boton_pdf)

        boton_volver = QPushButton("Volver")
        boton_volver.setObjectName("btnSecundario")
        boton_volver.clicked.connect(self.volver)

        encabezado.addWidget(boton_volver)
        principal.addLayout(encabezado)

        # CONTENIDO CON DESPLAZAMIENTO
        desplazamiento = QScrollArea()
        desplazamiento.setWidgetResizable(True)
        desplazamiento.setFrameShape(QFrame.Shape.NoFrame)

        contenido = QWidget()
        contenido_layout = QVBoxLayout(contenido)
        contenido_layout.setContentsMargins(2, 2, 8, 2)
        contenido_layout.setSpacing(18)

        # TARJETAS DE INDICADORES
        rejilla = QGridLayout()
        rejilla.setSpacing(14)

        indicadores = [
            ("total", "Total de préstamos", "#234B4A"),
            ("activos", "Préstamos activos", "#8B5E3C"),
            ("vencidos", "Préstamos vencidos", "#B76E32"),
            ("devueltos", "Libros devueltos", "#47785A")
        ]

        for posicion, (clave, nombre, color) in enumerate(indicadores):
            tarjeta = QFrame()
            tarjeta.setObjectName("tarjeta")

            tarjeta_layout = QVBoxLayout(tarjeta)
            tarjeta_layout.setContentsMargins(18, 16, 18, 16)
            tarjeta_layout.setSpacing(8)

            etiqueta_nombre = QLabel(nombre)
            etiqueta_nombre.setWordWrap(True)
            etiqueta_nombre.setObjectName("descripcion")

            numero = QLabel("0")
            numero.setAlignment(Qt.AlignmentFlag.AlignLeft)
            numero.setStyleSheet(
                f"color: {color};"
                "font-size: 29px;"
                "font-weight: bold;"
            )

            tarjeta_layout.addWidget(etiqueta_nombre)
            tarjeta_layout.addWidget(numero)
            tarjeta_layout.addStretch()

            rejilla.addWidget(
                tarjeta,
                posicion // 2,
                posicion % 2
            )

            self.tarjetas_indicadores[clave] = numero

        contenido_layout.addLayout(rejilla)

        # PRÉSTAMOS POR MES
        self.tarjeta_meses = QFrame()
        self.tarjeta_meses.setObjectName("tarjeta")

        meses_layout = QVBoxLayout(self.tarjeta_meses)
        meses_layout.setContentsMargins(20, 18, 20, 18)
        meses_layout.setSpacing(12)

        titulo_meses = QLabel("Préstamos por mes")
        titulo_meses.setObjectName("tituloPagina")
        meses_layout.addWidget(titulo_meses)

        self.contenedor_meses = QVBoxLayout()
        self.contenedor_meses.setSpacing(10)
        meses_layout.addLayout(self.contenedor_meses)

        contenido_layout.addWidget(self.tarjeta_meses)

        # LIBROS MÁS SOLICITADOS
        self.tarjeta_libros = QFrame()
        self.tarjeta_libros.setObjectName("tarjeta")

        libros_layout = QVBoxLayout(self.tarjeta_libros)
        libros_layout.setContentsMargins(20, 18, 20, 18)
        libros_layout.setSpacing(12)

        titulo_libros = QLabel("Libros más solicitados")
        titulo_libros.setObjectName("tituloPagina")
        libros_layout.addWidget(titulo_libros)

        self.contenedor_libros = QVBoxLayout()
        self.contenedor_libros.setSpacing(12)
        libros_layout.addLayout(self.contenedor_libros)

        contenido_layout.addWidget(self.tarjeta_libros)
        contenido_layout.addStretch()

        desplazamiento.setWidget(contenido)
        principal.addWidget(desplazamiento)

        # BOTÓN PARA ACTUALIZAR LOS DATOS
        boton_actualizar = QPushButton("Actualizar estadísticas")
        boton_actualizar.setObjectName("btnPrincipal")
        boton_actualizar.clicked.connect(self.cargar_estadisticas)

        principal.addWidget(
            boton_actualizar,
            alignment=Qt.AlignmentFlag.AlignRight
        )

    def limpiar_layout(self, layout):
        while layout.count():
            elemento = layout.takeAt(0)

            widget = elemento.widget()

            if widget is not None:
                widget.deleteLater()

            sublayout = elemento.layout()

            if sublayout is not None:
                self.limpiar_layout(sublayout)

    def cargar_estadisticas(self):
        sesion = obtener_sesion()

        try:
            hoy = date.today()

            # TOTAL DE PRÉSTAMOS REGISTRADOS
            total = (
                sesion.query(func.count(Prestamo.id))
                .scalar() or 0
            )

            # PRÉSTAMOS ACTIVOS QUE AÚN NO VENCEN
            activos = (
                sesion.query(func.count(Prestamo.id))
                .filter(
                    Prestamo.estado == "Prestado",
                    Prestamo.fecha_devolucion >= hoy
                )
                .scalar() or 0
            )

            # PRÉSTAMOS VENCIDOS QUE NO SE HAN DEVUELTO
            vencidos = (
                sesion.query(func.count(Prestamo.id))
                .filter(
                    Prestamo.estado.in_(["Prestado", "Vencido"]),
                    Prestamo.fecha_devolucion < hoy
                )
                .scalar() or 0
            )

            # PRÉSTAMOS DEVUELTOS
            devueltos = (
                sesion.query(func.count(Prestamo.id))
                .filter(
                    Prestamo.estado == "Devuelto"
                )
                .scalar() or 0
            )

            self.tarjetas_indicadores["total"].setText(str(total))
            self.tarjetas_indicadores["activos"].setText(str(activos))
            self.tarjetas_indicadores["vencidos"].setText(str(vencidos))
            self.tarjetas_indicadores["devueltos"].setText(str(devueltos))

            # PRÉSTAMOS DE LOS ÚLTIMOS SEIS MESES
            hace_cinco_meses = hoy.replace(day=1)

            for _ in range(5):
                if hace_cinco_meses.month == 1:
                    hace_cinco_meses = hace_cinco_meses.replace(
                        year=hace_cinco_meses.year - 1,
                        month=12
                    )
                else:
                    hace_cinco_meses = hace_cinco_meses.replace(
                        month=hace_cinco_meses.month - 1
                    )

            datos_meses = (
                sesion.query(
                    extract("year", Prestamo.fecha_prestamo),
                    extract("month", Prestamo.fecha_prestamo),
                    func.count(Prestamo.id)
                )
                .filter(
                    Prestamo.fecha_prestamo >= hace_cinco_meses
                )
                .group_by(
                    extract("year", Prestamo.fecha_prestamo),
                    extract("month", Prestamo.fecha_prestamo)
                )
                .order_by(
                    extract("year", Prestamo.fecha_prestamo),
                    extract("month", Prestamo.fecha_prestamo)
                )
                .all()
            )

            datos_meses = [
                (int(anio), int(mes), cantidad)
                for anio, mes, cantidad in datos_meses
            ]

            self.mostrar_meses(datos_meses)

            # CINCO LIBROS MÁS SOLICITADOS
            datos_libros = (
                sesion.query(
                    Prestamo.libro,
                    func.count(Prestamo.id).label("cantidad")
                )
                .group_by(Prestamo.libro)
                .order_by(
                    func.count(Prestamo.id).desc(),
                    Prestamo.libro.asc()
                )
                .limit(5)
                .all()
            )

            self.mostrar_libros(datos_libros)

        except Exception as error:
            QMessageBox.critical(
                self,
                "Error al cargar estadísticas",
                "No se pudieron cargar los datos.\n\n"
                f"Detalle: {error}"
            )

        finally:
            sesion.close()

    def generar_reporte_pdf(self):
        sesion = obtener_sesion()

        try:
            hoy = date.today()

            # INDICADORES
            total = sesion.query(func.count(Prestamo.id)).scalar() or 0

            activos = (
                sesion.query(func.count(Prestamo.id))
                .filter(
                    Prestamo.estado == "Prestado",
                    Prestamo.fecha_devolucion >= hoy
                )
                .scalar() or 0
            )

            vencidos = (
                sesion.query(func.count(Prestamo.id))
                .filter(
                    Prestamo.estado.in_(["Prestado", "Vencido"]),
                    Prestamo.fecha_devolucion < hoy
                )
                .scalar() or 0
            )

            devueltos = (
                sesion.query(func.count(Prestamo.id))
                .filter(Prestamo.estado == "Devuelto")
                .scalar() or 0
            )

            # PRÉSTAMOS DE LOS ÚLTIMOS SEIS MESES
            hace_cinco_meses = hoy.replace(day=1)

            for _ in range(5):
                if hace_cinco_meses.month == 1:
                    hace_cinco_meses = hace_cinco_meses.replace(
                        year=hace_cinco_meses.year - 1,
                        month=12
                    )
                else:
                    hace_cinco_meses = hace_cinco_meses.replace(
                        month=hace_cinco_meses.month - 1
                    )

            resultados_meses = (
                sesion.query(
                    extract("year", Prestamo.fecha_prestamo),
                    extract("month", Prestamo.fecha_prestamo),
                    func.count(Prestamo.id)
                )
                .filter(Prestamo.fecha_prestamo >= hace_cinco_meses)
                .group_by(
                    extract("year", Prestamo.fecha_prestamo),
                    extract("month", Prestamo.fecha_prestamo)
                )
                .order_by(
                    extract("year", Prestamo.fecha_prestamo),
                    extract("month", Prestamo.fecha_prestamo)
                )
                .all()
            )

            nombres_meses = [
                "Enero", "Febrero", "Marzo", "Abril",
                "Mayo", "Junio", "Julio", "Agosto",
                "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ]

            meses = [
                [f"{nombres_meses[int(mes) - 1]} {int(anio)}", int(cantidad)]
                for anio, mes, cantidad in resultados_meses
            ]

            # CINCO LIBROS MÁS SOLICITADOS
            resultados_libros = (
                sesion.query(
                    Prestamo.libro,
                    func.count(Prestamo.id)
                )
                .group_by(Prestamo.libro)
                .order_by(
                    func.count(Prestamo.id).desc(),
                    Prestamo.libro.asc()
                )
                .limit(5)
                .all()
            )

            libros = [
                [str(libro or "Sin título"), int(cantidad)]
                for libro, cantidad in resultados_libros
            ]

            datos = {
                "total": total,
                "activos": activos,
                "vencidos": vencidos,
                "devueltos": devueltos,
                "meses": meses,
                "libros": libros
            }

            # GENERAR Y ABRIR PDF
            ruta = os.path.join(
                os.path.dirname(__file__),
                "reporte_estadisticas.pdf"
            )

            generar_pdf_estadisticas(datos, ruta)

            abierto = QDesktopServices.openUrl(
                QUrl.fromLocalFile(os.path.abspath(ruta))
            )

            if abierto:
                QMessageBox.information(
                    self,
                    "Reporte generado",
                    "El reporte PDF se generó y se abrió correctamente."
                )
            else:
                QMessageBox.warning(
                    self,
                    "Reporte generado",
                    f"El PDF se creó, pero no se pudo abrir automáticamente.\n\n{ruta}"
                )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Error al generar PDF",
                f"No se pudo generar el reporte.\n\nDetalle: {error}"
            )

        finally:
            sesion.close()

                

    def mostrar_meses(self, datos):
        self.limpiar_layout(self.contenedor_meses)

        nombres_meses = [
            "Enero", "Febrero", "Marzo", "Abril",
            "Mayo", "Junio", "Julio", "Agosto",
            "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]

        cantidades = [fila[2] for fila in datos]
        maximo = max(cantidades, default=0)

        if not datos:
            mensaje = QLabel("Todavía no hay préstamos registrados.")
            mensaje.setObjectName("descripcion")
            self.contenedor_meses.addWidget(mensaje)
            return

        for anio, mes, cantidad in datos:
            fila = QHBoxLayout()

            nombre = QLabel(f"{nombres_meses[mes - 1]} {anio}")
            nombre.setMinimumWidth(125)

            barra = QProgressBar()
            barra.setRange(0, maximo if maximo > 0 else 1)
            barra.setValue(cantidad)
            barra.setFormat(f"{cantidad} préstamo(s)")
            barra.setMinimumHeight(22)
            barra.setTextVisible(True)
            barra.setStyleSheet("""
                QProgressBar {
                    border: none;
                    border-radius: 5px;
                    background-color: #E6E0D5;
                    color: #234B4A;
                    text-align: center;
                }

                QProgressBar::chunk {
                    background-color: #234B4A;
                    border-radius: 5px;
                }
            """)

            fila.addWidget(nombre)
            fila.addWidget(barra, 1)

            self.contenedor_meses.addLayout(fila)

    def mostrar_libros(self, datos):
        self.limpiar_layout(self.contenedor_libros)

        if not datos:
            mensaje = QLabel("Todavía no hay libros prestados.")
            mensaje.setObjectName("descripcion")
            self.contenedor_libros.addWidget(mensaje)
            return

        maximo = max(fila[1] for fila in datos)

        for posicion, (libro, cantidad) in enumerate(datos, start=1):
            fila = QVBoxLayout()
            encabezado = QHBoxLayout()

            nombre = QLabel(f"{posicion}. {libro or 'Libro sin título'}")
            nombre.setWordWrap(True)

            numero = QLabel(str(cantidad))
            numero.setStyleSheet(
                "color: #8B5E3C; font-weight: bold;"
            )

            encabezado.addWidget(nombre, 1)
            encabezado.addWidget(numero)

            barra = QProgressBar()
            barra.setRange(0, maximo if maximo > 0 else 1)
            barra.setValue(cantidad)
            barra.setTextVisible(False)
            barra.setFixedHeight(9)
            barra.setStyleSheet("""
                QProgressBar {
                    border: none;
                    border-radius: 4px;
                    background-color: #E6E0D5;
                }

                QProgressBar::chunk {
                    background-color: #8B5E3C;
                    border-radius: 4px;
                }
            """)

            fila.addLayout(encabezado)
            fila.addWidget(barra)

            self.contenedor_libros.addLayout(fila)