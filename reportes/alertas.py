from datetime import date
from urllib.parse import quote

import qtawesome as qta

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QCompleter

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFrame,
    QMessageBox,
    QAbstractItemView,
    QScrollArea,
    QComboBox,
    QLineEdit,
    QInputDialog

)

from base_datos.conexion_orm import obtener_sesion
from modelos.prestamo import Prestamo
from modelos.usuario import Usuario
from modelos.libro import Libro
from modelos.incidencia_libros import IncidenciaLibro
from sqlalchemy import func


class MenuAlertas(QWidget):

    def __init__(
        self,
        abrir_devoluciones,
        abrir_estado_fisico,
        abrir_estadisticas,
        volver
    ):
        super().__init__()

        principal = QVBoxLayout(self)
        principal.setContentsMargins(30, 25, 30, 25)
        principal.setSpacing(20)

        encabezado = QHBoxLayout()
        textos = QVBoxLayout()

        titulo = QLabel("Alertas y seguimiento")
        titulo.setObjectName("tituloPagina")

        descripcion = QLabel(
            "Consulte el estado de los libros y los préstamos de la biblioteca."
        )
        descripcion.setObjectName("descripcion")

        textos.addWidget(titulo)
        textos.addWidget(descripcion)
        encabezado.addLayout(textos)
        encabezado.addStretch()

        boton_volver = QPushButton("← Volver")
        boton_volver.setObjectName("btnSecundario")
        boton_volver.clicked.connect(volver)
        encabezado.addWidget(boton_volver)

        principal.addLayout(encabezado)

        tarjetas = QGridLayout()
        tarjetas.setSpacing(18)

        self.crear_tarjeta(
            tarjetas, 0, "fa5s.book",
            "Alertas de devolución",
            "Consultar los préstamos vencidos y sus días de retraso.",
            abrir_devoluciones
        )

        self.crear_tarjeta(
            tarjetas, 1, "fa5s.book",
            "Estado físico de los libros",
            "Revisar el estado de conservación de los libros.",
            abrir_estado_fisico
        )

        self.crear_tarjeta(
            tarjetas, 2, "fa5s.chart-bar",
            "Estadísticas de préstamos",
            "Consultar información y estadísticas de los préstamos.",
            abrir_estadisticas
        )

        principal.addLayout(tarjetas)
        principal.addStretch()

    def crear_tarjeta(
        self, distribucion, columna, icono, titulo, descripcion, accion
    ):
        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta")
        tarjeta.setMinimumHeight(230)

        contenido = QVBoxLayout(tarjeta)
        contenido.setContentsMargins(20, 22, 20, 22)
        contenido.setSpacing(12)

        imagen = QLabel()
        imagen.setPixmap(
            qta.icon(icono, color="#8B5E3C").pixmap(42, 42)
        )
        imagen.setAlignment(Qt.AlignCenter)

        nombre = QLabel(titulo)
        nombre.setAlignment(Qt.AlignCenter)
        nombre.setWordWrap(True)
        nombre.setStyleSheet(
            "font-size: 17px; font-weight: bold; color: #234B4A;"
        )

        texto = QLabel(descripcion)
        texto.setAlignment(Qt.AlignCenter)
        texto.setWordWrap(True)
        texto.setStyleSheet("font-size: 13px; color: #66594D;")

        boton = QPushButton("Abrir sección")
        boton.setObjectName("btnPrincipal")
        boton.clicked.connect(accion)

        contenido.addWidget(imagen)
        contenido.addWidget(nombre)
        contenido.addWidget(texto)
        contenido.addStretch()
        contenido.addWidget(boton)

        distribucion.addWidget(tarjeta, 0, columna)


class AlertasDevolucion(QWidget):

    def __init__(self, volver):
        super().__init__()

        self.volver = volver

        principal = QVBoxLayout(self)
        principal.setContentsMargins(30, 25, 30, 25)
        principal.setSpacing(20)

        encabezado = QHBoxLayout()
        textos = QVBoxLayout()

        titulo = QLabel("Alertas de devolución")
        titulo.setObjectName("tituloPagina")

        descripcion = QLabel(
            "Préstamos que requieren seguimiento"
        )
        descripcion.setObjectName("descripcion")

        textos.addWidget(titulo)
        textos.addWidget(descripcion)
        encabezado.addLayout(textos)
        encabezado.addStretch()

        boton_volver = QPushButton("← Volver")
        boton_volver.setObjectName("btnSecundario")
        boton_volver.clicked.connect(self.volver)
        encabezado.addWidget(boton_volver)

        principal.addLayout(encabezado)

        resumen = QFrame()
        resumen.setObjectName("tarjeta")

        resumen_layout = QHBoxLayout(resumen)
        resumen_layout.setContentsMargins(20, 15, 20, 15)

        icono_campana = QLabel()
        icono_campana.setPixmap(
            qta.icon("fa5s.bell", color="#7B3038").pixmap(35, 35)
        )

        self.total_alertas = QLabel("0 préstamos vencidos")
        self.total_alertas.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #234B4A;
        """)

        resumen_layout.addWidget(icono_campana)
        resumen_layout.addWidget(self.total_alertas)
        resumen_layout.addStretch()

        principal.addWidget(resumen)

        self.contenedor_scroll = QScrollArea()
        self.contenedor_scroll.setWidgetResizable(True)
        self.contenedor_scroll.setFrameShape(QFrame.NoFrame)

        self.contenedor = QWidget()
        self.tarjetas_layout = QVBoxLayout(self.contenedor)
        self.tarjetas_layout.setContentsMargins(0, 0, 0, 0)
        self.tarjetas_layout.setSpacing(15)

        self.contenedor_scroll.setWidget(self.contenedor)
        principal.addWidget(self.contenedor_scroll)

        boton_actualizar = QPushButton("Actualizar alertas")
        boton_actualizar.setObjectName("btnPrincipal")
        boton_actualizar.clicked.connect(self.cargar_alertas)

        principal.addWidget(
            boton_actualizar,
            alignment=Qt.AlignRight
        )

        self.cargar_alertas()

    def crear_tarjeta(
        self, codigo, libro, usuario, telefono, fecha_texto, dias
    ):
        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta")
        tarjeta.setMinimumHeight(190)

        tarjeta.setStyleSheet("""
            QFrame#tarjeta {
                background-color: #FFFFFF;
                border: 1px solid #E5D9CC;
                border-radius: 12px;
            }
        """)

        contenido = QVBoxLayout(tarjeta)
        contenido.setContentsMargins(20, 18, 20, 18)
        contenido.setSpacing(12)

        encabezado = QHBoxLayout()

        icono = QLabel()
        icono.setPixmap(
            qta.icon("fa5s.bell", color="#C46F65").pixmap(25, 25)
        )

        titulo = QLabel("Devolución pendiente")
        titulo.setStyleSheet("""
            font-size: 17px;
            font-weight: bold;
            color: #234B4A;
        """)

        encabezado.addWidget(icono)
        encabezado.addWidget(titulo)
        encabezado.addStretch()

        retraso = QLabel(f"{dias} días de retraso")
        retraso.setStyleSheet("""
            background-color: #FCE8E6;
            color: #B3261E;
            padding: 6px 10px;
            border-radius: 8px;
            font-weight: bold;
        """)

        encabezado.addWidget(retraso)
        contenido.addLayout(encabezado)

        nombre_usuario = QLabel(f"Usuario: {usuario}")
        nombre_usuario.setStyleSheet(
            "font-size: 14px; color: #332C27;"
        )

        telefono_usuario = QLabel(
            f"Teléfono: {telefono or 'No registrado'}"
        )
        telefono_usuario.setStyleSheet(
            "font-size: 13px; color: #66594D;"
        )

        contenido.addWidget(nombre_usuario)
        contenido.addWidget(telefono_usuario)

        libro_texto = QLabel(
            f"Libro: {libro}  |  Código: {codigo}"
        )
        libro_texto.setWordWrap(True)
        libro_texto.setStyleSheet(
            "font-size: 13px; color: #66594D;"
        )

        fecha = QLabel(f"Fecha límite: {fecha_texto}")
        fecha.setStyleSheet(
            "font-size: 13px; color: #66594D;"
        )

        contenido.addWidget(libro_texto)
        contenido.addWidget(fecha)

        botones = QHBoxLayout()
        botones.addStretch()

        boton_contactar = QPushButton(
            qta.icon("fa5s.phone", color="white"),
            " Contactar"
        )

        boton_contactar.setStyleSheet("""
            QPushButton {
                background-color: #8B5E3C;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #70482D;
            }
        """)

        if telefono:
            boton_contactar.clicked.connect(
                lambda checked=False, numero=telefono,
                nombre=usuario, nombre_libro=libro:
                self.contactar_whatsapp(
                    numero, nombre, nombre_libro
                )
            )
        else:
            boton_contactar.setEnabled(False)
            boton_contactar.setText("Sin teléfono")

        boton_devolver = QPushButton(
            qta.icon("fa5s.check", color="white"),
            " Registrar devolución"
        )

        boton_devolver.setStyleSheet("""
            QPushButton {
                background-color: #3F7D5A;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #326448;
            }
        """)

        boton_devolver.clicked.connect(
            lambda checked=False, prestamo=codigo:
            self.registrar_devolucion(prestamo)
        )

        botones.addWidget(boton_contactar)
        botones.addWidget(boton_devolver)
        contenido.addLayout(botones)

        return tarjeta

    def contactar_whatsapp(self, telefono, usuario, libro):
        numero = "".join(
            caracter for caracter in str(telefono)
            if caracter.isdigit()
        )

        if len(numero) == 8:
            numero = "505" + numero

        if not numero:
            QMessageBox.warning(
                self,
                "Teléfono no disponible",
                "Este usuario no tiene un número de teléfono válido."
            )
            return

        mensaje = (
            f"Hola, {usuario}. Le contactamos de la "
            f"Biblioteca  para recordarle que "
            f"tiene pendiente la devolución del libro "
            f"'{libro}'. ¿Podría indicarnos cuándo "
            f"realizará la devolución? Muchas gracias."
        )

        enlace = f"https://wa.me/{numero}?text={quote(mensaje)}"

        if not QDesktopServices.openUrl(QUrl(enlace)):
            QMessageBox.warning(
                self,
                "No se pudo abrir WhatsApp",
                "No se pudo abrir el enlace. "
                "Verificá que tengas un navegador disponible."
            )

    def cargar_alertas(self):

        sesion = obtener_sesion()

        try:
            filas = (
                sesion.query(
                    Prestamo.codigo_prestamo,
                    Prestamo.libro,
                    Prestamo.usuario,
                    Usuario.telefono,
                    Prestamo.fecha_devolucion,
                    Prestamo.estado
                )
                .outerjoin(
                    Usuario,
                    Usuario.cedula == Prestamo.cedula_usuario
                )
                .filter(
                    Prestamo.estado.in_(["Prestado", "Vencido"]),
                    Prestamo.fecha_devolucion < date.today()
                )
                .order_by(Prestamo.fecha_devolucion.asc())
                .all()
            )

            while self.tarjetas_layout.count():
                elemento = self.tarjetas_layout.takeAt(0)
                widget = elemento.widget()

                if widget:
                    widget.deleteLater()

            for datos in filas:
                (
                    codigo, libro, usuario, telefono,
                    fecha_limite, estado
                ) = datos

                if isinstance(fecha_limite, date):
                    fecha_texto = fecha_limite.strftime("%d/%m/%Y")
                    dias = (date.today() - fecha_limite).days
                else:
                    fecha_texto = str(fecha_limite or "")
                    dias = 0

                tarjeta = self.crear_tarjeta(
                    codigo,
                    libro,
                    usuario,
                    telefono,
                    fecha_texto,
                    dias
                )

                self.tarjetas_layout.addWidget(tarjeta)

            self.total_alertas.setText(
                f"{len(filas)} préstamos vencidos"
            )

            if not filas:
                mensaje = QLabel(
                    "¡Excelente! No hay préstamos vencidos."
                )
                mensaje.setAlignment(Qt.AlignCenter)
                mensaje.setStyleSheet("""
                    font-size: 16px;
                    color: #234B4A;
                    padding: 30px;
                """)
                self.tarjetas_layout.addWidget(mensaje)

            self.tarjetas_layout.addStretch()

        except Exception as error:
            QMessageBox.warning(
                self,
                "Error al cargar alertas",
                "No se pudieron consultar las alertas.\n\n"
                + str(error)
            )

        finally:
            sesion.close()  

    def registrar_devolucion(self, codigo):
        sesion = obtener_sesion()

        try:
            prestamo = sesion.query(Prestamo).filter_by(
                codigo_prestamo=codigo
            ).first()

            if not prestamo:
                QMessageBox.warning(
                    self, "Aviso", "No se encontró el préstamo."
                )
                return

            if prestamo.estado == "Devuelto":
                QMessageBox.information(
                    self, "Información", "Este préstamo ya fue devuelto."
                )
                return

            libro = sesion.query(Libro).filter_by(
                codigo=prestamo.codigo_libro
            ).first()

            prestamo.estado = "Devuelto"

            if libro and str(libro.estado).lower() == "prestado":
                libro.estado = "Disponible"

            sesion.commit()

            QMessageBox.information(
                self, "Éxito",
                "La devolución se registró correctamente."
            )

            self.cargar_alertas()

        except Exception as e:
            sesion.rollback()
            QMessageBox.critical(
                self, "Error",
                f"No se pudo registrar la devolución: {e}"
            )

        finally:
            sesion.close()

     


   
                  

    

class EstadoFisicoLibros(QWidget):

    def __init__(self, volver):
        super().__init__()

        self.volver = volver
        self.estado_filtro = "Por revisar"
        self.tarjetas = {}

        # Área desplazable para toda la página.
        exterior = QVBoxLayout(self)
        exterior.setContentsMargins(0, 0, 0, 0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.contenido = QWidget()
        principal = QVBoxLayout(self.contenido)
        principal.setContentsMargins(25, 22, 25, 25)
        principal.setSpacing(20)

        self.scroll.setWidget(self.contenido)
        exterior.addWidget(self.scroll)

        # Encabezado.
        encabezado = QHBoxLayout()
        encabezado.setSpacing(15)

        textos = QVBoxLayout()
        textos.setSpacing(6)

        titulo = QLabel("Estado físico de los libros")
        titulo.setObjectName("tituloPagina")

        descripcion = QLabel(
            "Registro y seguimiento del estado de conservación."
        )
        descripcion.setObjectName("descripcion")
        descripcion.setWordWrap(True)

        textos.addWidget(titulo)
        textos.addWidget(descripcion)

        encabezado.addLayout(textos, 1)

        boton_volver = QPushButton("← Volver")
        boton_volver.setObjectName("btnSecundario")
        boton_volver.setMinimumHeight(38)
        boton_volver.clicked.connect(self.volver)
        encabezado.addWidget(
            boton_volver, 0, Qt.AlignmentFlag.AlignTop
        )

        principal.addLayout(encabezado)

        # Tarjetas de resumen.
        distribucion = QGridLayout()
        distribucion.setHorizontalSpacing(18)
        distribucion.setVerticalSpacing(18)

        configuracion = [
            ("Por revisar", "Pendientes de revisión"),
            ("Necesita reparación", "Daños registrados"),
            ("En reparación", "Reparaciones pendientes"),
            ("Reparado", "Reparaciones terminadas")
        ]

        for indice, (estado, ayuda) in enumerate(configuracion):
            tarjeta = QFrame()
            tarjeta.setObjectName("tarjeta")
            tarjeta.setMinimumHeight(165)

            contenido_tarjeta = QVBoxLayout(tarjeta)
            contenido_tarjeta.setContentsMargins(18, 16, 18, 16)
            contenido_tarjeta.setSpacing(8)

            titulo_tarjeta = QLabel(estado)
            titulo_tarjeta.setObjectName("tarjetaTitulo")
            titulo_tarjeta.setWordWrap(True)

            numero = QLabel("0")
            numero.setObjectName("tarjetaNumero")

            descripcion_tarjeta = QLabel(ayuda)
            descripcion_tarjeta.setObjectName("descripcion")
            descripcion_tarjeta.setWordWrap(True)

            boton_ver = QPushButton("Ver registros")
            boton_ver.setObjectName("btnSecundario")
            boton_ver.setMinimumHeight(34)
            boton_ver.setMinimumWidth(125)
            boton_ver.clicked.connect(
                lambda checked=False, valor=estado:
                self.filtrar_estado(valor)
            )

            contenido_tarjeta.addWidget(titulo_tarjeta)
            contenido_tarjeta.addWidget(numero)
            contenido_tarjeta.addWidget(descripcion_tarjeta)
            contenido_tarjeta.addStretch()
            contenido_tarjeta.addWidget(
                boton_ver, 0, Qt.AlignmentFlag.AlignLeft
            )

            fila = indice // 2
            columna = indice % 2
            distribucion.addWidget(tarjeta, fila, columna)

            self.tarjetas[estado] = {
                "tarjeta": tarjeta,
                "numero": numero
            }

        principal.addLayout(distribucion)

        # Botón independiente, separado de las tarjetas.
        fila_todos = QHBoxLayout()
        fila_todos.setContentsMargins(0, 2, 0, 4)
        fila_todos.addStretch()

        self.boton_todos = QPushButton("Ver todos los registros")
        self.boton_todos.setObjectName("btnSecundario")
        self.boton_todos.setMinimumHeight(40)
        self.boton_todos.setMinimumWidth(210)
        self.boton_todos.clicked.connect(
            lambda: self.filtrar_estado("Todos")
        )

        fila_todos.addWidget(self.boton_todos)
        principal.addLayout(fila_todos)

        # Formulario de revisión.
        self.formulario = QFrame()
        self.formulario.setObjectName("tarjeta")

        formulario_layout = QVBoxLayout(self.formulario)
        formulario_layout.setContentsMargins(20, 18, 20, 18)
        formulario_layout.setSpacing(12)

        subtitulo = QLabel("Registrar revisión física")
        subtitulo.setObjectName("tituloPagina")
        formulario_layout.addWidget(subtitulo)

        formulario_layout.addWidget(QLabel("Buscar libro:"))

        self.libro_combo = QComboBox()
        self.libro_combo.setEditable(True)
        self.libro_combo.setInsertPolicy(QComboBox.NoInsert)
        self.libro_combo.setMinimumHeight(40)
        self.libro_combo.setMaxVisibleItems(12)
        self.libro_combo.setPlaceholderText(
            "Escribí el código o título del libro..."
        )
        formulario_layout.addWidget(self.libro_combo)

        formulario_layout.addWidget(
            QLabel("Descripción del daño:")
        )

        self.descripcion_input = QLineEdit()
        self.descripcion_input.setMinimumHeight(40)
        self.descripcion_input.setPlaceholderText(
            "Ej.: portada dañada, hojas sueltas o páginas rotas..."
        )
        formulario_layout.addWidget(self.descripcion_input)

        fila_registrar = QHBoxLayout()
        fila_registrar.addStretch()

        self.boton_registrar = QPushButton("Registrar revisión")
        self.boton_registrar.setObjectName("btnPrincipal")
        self.boton_registrar.setMinimumHeight(42)
        self.boton_registrar.clicked.connect(self.registrar_revision)

        fila_registrar.addWidget(self.boton_registrar)
        formulario_layout.addLayout(fila_registrar)

        principal.addWidget(self.formulario)

        # Tabla de incidencias.
        self.titulo_tabla = QLabel("Libros por revisar")
        self.titulo_tabla.setObjectName("tituloPagina")
        principal.addWidget(self.titulo_tabla)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels([
            "ID",
            "Código",
            "Libro",
            "Fecha de reporte",
            "Descripción",
            "Estado",
            "Fecha de resolución"
        ])

        self.tabla.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.tabla.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.tabla.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setMinimumHeight(280)

        encabezado_tabla = self.tabla.horizontalHeader()
        encabezado_tabla.setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        encabezado_tabla.setSectionResizeMode(
            4, QHeaderView.ResizeMode.Stretch
        )

        principal.addWidget(self.tabla)

        # Acciones inferiores.
        botones = QHBoxLayout()
        botones.setSpacing(12)

        boton_actualizar = QPushButton("↻ Actualizar")
        boton_actualizar.setObjectName("btnSecundario")
        boton_actualizar.setMinimumHeight(40)
        boton_actualizar.clicked.connect(self.actualizar)

        self.boton_cambiar = QPushButton("Cambiar estado")
        self.boton_cambiar.setObjectName("btnPrincipal")
        self.boton_cambiar.setMinimumHeight(40)
        self.boton_cambiar.clicked.connect(self.cambiar_estado)

        botones.addWidget(boton_actualizar)
        botones.addStretch()
        botones.addWidget(self.boton_cambiar)

        principal.addLayout(botones)

        # Espacio al final para facilitar el desplazamiento.
        principal.addSpacing(10)

        self.cargar_libros()
        self.actualizar()

    def cargar_libros(self):

        sesion = obtener_sesion()

        try:
            libros = (
                sesion.query(Libro)
                .filter(Libro.estado == "Disponible")
                .order_by(Libro.titulo)
                .all()
            )

            self.libro_combo.clear()

            for libro in libros:
                self.libro_combo.addItem(
                    f"{libro.codigo} - {libro.titulo}",
                    libro.codigo
                )

            completador = QCompleter(
                self.libro_combo.model(), self
            )
            completador.setCompletionColumn(0)
            completador.setCaseSensitivity(
                Qt.CaseSensitivity.CaseInsensitive
            )
            completador.setFilterMode(
                Qt.MatchFlag.MatchContains
            )
            completador.setCompletionMode(
                QCompleter.CompletionMode.PopupCompletion
            )
            self.libro_combo.setCompleter(completador)

        except Exception as error:
            QMessageBox.warning(
                self, "Error",
                f"No se pudieron cargar los libros.\n\n{error}"
            )

        finally:
            sesion.close()




    def registrar_revision(self):
        codigo_libro = self.libro_combo.currentData()
        descripcion = self.descripcion_input.text().strip()

        if not codigo_libro:
            QMessageBox.warning(
                self,
                "Aviso",
                "Seleccione un libro para registrar la revisión."
            )
            return

        if not descripcion:
            QMessageBox.warning(
                self,
                "Aviso",
                "Ingrese una descripción de la revisión."
            )
            return

        sesion = obtener_sesion()

        try:
            nueva_incidencia = IncidenciaLibro(
                codigo_libro=codigo_libro,
                fecha_reporte=date.today(),
                descripcion=descripcion,
                estado_incidencia="Por revisar"
            )

            sesion.add(nueva_incidencia)
            sesion.commit()

            QMessageBox.information(
                self,
                "Éxito",
                "La revisión se registró correctamente."
            )

            self.descripcion_input.clear()
            self.actualizar()

        except Exception as error:
            sesion.rollback()

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo registrar la revisión.\n\n{error}"
            )

        finally:
            sesion.close()






    def actualizar_tarjetas(self):   
        cantidades = {
            "Por revisar": 0,
            "Necesita reparación": 0,
            "En reparación": 0,
            "Reparado": 0
        }

        sesion = obtener_sesion()

        try:
            resultados = (
                sesion.query(
                    IncidenciaLibro.estado_incidencia,
                    func.count(IncidenciaLibro.id)
                )
                .group_by(IncidenciaLibro.estado_incidencia)
                .all()
            )

            for estado, cantidad in resultados:
                if estado in cantidades:
                    cantidades[estado] = cantidad

        except Exception as error:
            QMessageBox.warning(
                self,
                "Error",
                f"No se pudieron actualizar las cantidades.\n\n{error}"
            )

        finally:
            sesion.close()

        for estado, datos in self.tarjetas.items():
            datos["numero"].setText(str(cantidades[estado]))
            


         

    def filtrar_estado(self, estado):
        self.estado_filtro = estado
        self.formulario.setVisible(estado == "Por revisar")

        titulos = {
            "Todos": "Todos los registros",
            "Por revisar": "Libros por revisar",
            "Necesita reparación": "Libros que necesitan reparación",
            "En reparación": "Libros en reparación",
            "Reparado": "Libros reparados"
        }

        self.titulo_tabla.setText(titulos.get(estado, estado))
        self.actualizar()

    

       
    def cargar_datos(self):
        sesion = obtener_sesion()

        try:
            consulta = (
                sesion.query(
                    IncidenciaLibro.id,
                    IncidenciaLibro.codigo_libro,
                    Libro.titulo,
                    IncidenciaLibro.fecha_reporte,
                    IncidenciaLibro.descripcion,
                    IncidenciaLibro.estado_incidencia,
                    IncidenciaLibro.fecha_resolucion
                )
                .outerjoin(
                    Libro,
                    Libro.codigo == IncidenciaLibro.codigo_libro
                )
            )

            if self.estado_filtro != "Todos":
                consulta = consulta.filter(
                    IncidenciaLibro.estado_incidencia
                    == self.estado_filtro
                )

            filas = (
                consulta
                .order_by(IncidenciaLibro.fecha_reporte.desc())
                .all()
            )

            self.tabla.clearSpans()
            self.tabla.setRowCount(0)

            for fila in filas:
                numero = self.tabla.rowCount()
                self.tabla.insertRow(numero)

                for columna, valor in enumerate(fila):
                    if valor is None:
                        texto = ""
                    elif hasattr(valor, "strftime"):
                        texto = valor.strftime("%d/%m/%Y")
                    else:
                        texto = str(valor)

                    self.tabla.setItem(
                        numero,
                        columna,
                        QTableWidgetItem(texto)
                    )

            if not filas:
                self.tabla.setRowCount(1)
                self.tabla.setSpan(0, 0, 1, 7)

                mensaje = QTableWidgetItem(
                    "No hay registros en esta categoría."
                )
                mensaje.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )
                self.tabla.setItem(0, 0, mensaje)

        except Exception as error:
            QMessageBox.warning(
                self,
                "Error al cargar registros",
                "No se pudieron consultar los registros.\n\n"
                + str(error)
            )

        finally:
            sesion.close()



    def cambiar_estado(self):
        fila = self.tabla.currentRow()

        if fila < 0:
            QMessageBox.warning(
                self,
                "Aviso",
                "Seleccione una incidencia de la tabla."
            )
            return

        elemento_id = self.tabla.item(fila, 0)

        if elemento_id is None:
            return

        id_incidencia = elemento_id.text()

        estados = [
            "Por revisar",
            "Necesita reparación",
            "En reparación",
            "Reparado"
        ]

        nuevo_estado, aceptado = QInputDialog.getItem(
            self,
            "Cambiar estado",
            "Seleccione el nuevo estado:",
            estados,
            0,
            False
        )

        if not aceptado:
            return

        sesion = obtener_sesion()

        try:
            incidencia = sesion.get(
                IncidenciaLibro,
                int(id_incidencia)
            )

            if incidencia is None:
                QMessageBox.warning(
                    self,
                    "Aviso",
                    "No se encontró la incidencia."
                )
                return

            incidencia.estado_incidencia = nuevo_estado

            if nuevo_estado == "Reparado":
                incidencia.fecha_resolucion = date.today()
            else:
                incidencia.fecha_resolucion = None

            libro = sesion.query(Libro).filter_by(
                codigo=incidencia.codigo_libro
            ).first()

            if libro:
                estado_actual = str(libro.estado).strip().lower()

                if nuevo_estado in [
                    "Necesita reparación",
                    "En reparación"
                ]:
                    if estado_actual != "prestado":
                        libro.estado = "En mantenimiento"

                elif nuevo_estado == "Reparado":
                    otras_incidencias = sesion.query(
                        IncidenciaLibro
                    ).filter(
                        IncidenciaLibro.codigo_libro == incidencia.codigo_libro,
                        IncidenciaLibro.id != incidencia.id,
                        IncidenciaLibro.estado_incidencia.in_([
                            "Por revisar",
                            "Necesita reparación",
                            "En reparación"
                        ])
                    ).count()

                    if (
                        otras_incidencias == 0
                        and estado_actual == "en mantenimiento"
                    ):
                        libro.estado = "Disponible"

            sesion.commit()

            QMessageBox.information(
                self,
                "Éxito",
                "El estado se actualizó correctamente."
            )

            self.actualizar()

        except Exception as e:
            sesion.rollback()
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo actualizar el estado:\n{e}"
            )

        finally:
            sesion.close()
        

    

               

    def actualizar(self):
        self.actualizar_tarjetas()
        self.cargar_datos()