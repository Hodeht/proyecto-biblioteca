from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QFrame, QComboBox,
    QFormLayout, QHeaderView, QMenu, QDateEdit, QMessageBox,
    QScrollArea, QAbstractItemView
)
from base_datos.conexion import conectar
from base_datos.conexion_orm import obtener_sesion
from modelos.libro import Libro
from modelos.usuario import Usuario
from modelos.prestamo import Prestamo  
from datetime import date 


class Prestamos(QWidget):

    def __init__(self, volver):
        super().__init__()

        self.volver = volver
        self.fila_editando = None
        self.libro_seleccionado = None
        self.usuario_seleccionado = None
        self.prestamos = []

        # ---------- Área desplazable ----------
        contenedor = QVBoxLayout(self)
        contenedor.setContentsMargins(0, 0, 0, 0)

        desplazamiento = QScrollArea()
        desplazamiento.setWidgetResizable(True)
        desplazamiento.setFrameShape(QFrame.NoFrame)

        contenido = QWidget()
        principal = QVBoxLayout(contenido)
        principal.setContentsMargins(30, 15, 30, 15)
        principal.setSpacing(10)

        desplazamiento.setWidget(contenido)
        contenedor.addWidget(desplazamiento)

        # ---------- Encabezado ----------
        encabezado = QHBoxLayout()
        textos = QVBoxLayout()

        titulo = QLabel("Administración de préstamos")
        titulo.setObjectName("tituloPagina")

        descripcion = QLabel(
            "Registre préstamos, consulte usuarios y controle devoluciones."
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

        # ---------- Tarjeta del formulario ----------
        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta")
        tarjeta.setStyleSheet("background-color: white;")

        tarjeta_layout = QVBoxLayout(tarjeta)
        tarjeta_layout.setContentsMargins(20, 15, 20, 15)
        tarjeta_layout.setSpacing(10)

        titulo_formulario = QLabel("Nuevo préstamo")
        titulo_formulario.setStyleSheet(
            "font-size: 17px; font-weight: bold;"
        )
        tarjeta_layout.addWidget(titulo_formulario)

        formulario = QFormLayout()
        formulario.setSpacing(9)

        # Buscar libro
        self.buscar_libro = QLineEdit()
        self.buscar_libro.setPlaceholderText(
            "Buscar por código, título o autor..."
        )
        self.buscar_libro.textChanged.connect(self.buscar_libros)
        formulario.addRow("Buscar libro:", self.buscar_libro)

        self.resultados_libros = QComboBox()
        self.resultados_libros.setPlaceholderText(
            "Seleccione un libro disponible"
        )
        self.resultados_libros.addItem("Seleccione un libro...", None)
        self.resultados_libros.currentIndexChanged.connect(
            self.seleccionar_libro
        )
        self.resultados_libros.setStyleSheet("""
            QComboBox {
                background-color: white;
                color: #332C27;
                padding: 6px;
                border: 1px solid #D8CDBD;
                border-radius: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFDF8;
                color: #332C27;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #8B5E3C;
                color: white;
            }
        """)
        formulario.addRow("Resultados:", self.resultados_libros)

        self.libro_mostrado = QLabel(
            "Seleccione un libro de los resultados."
        )
        self.libro_mostrado.setWordWrap(True)
        self.libro_mostrado.setStyleSheet("""
            padding: 8px;
            border: 1px solid #D8CDBD;
            border-radius: 5px;
        """)
        formulario.addRow("Libro elegido:", self.libro_mostrado)

        # Cédula del usuario
        self.cedula_usuario = QLineEdit()
        self.cedula_usuario.setPlaceholderText(
            "Ingrese el número de cédula"
        )
        self.cedula_usuario.editingFinished.connect(
            self.consultar_usuario
        )
        formulario.addRow("Cédula del usuario:", self.cedula_usuario)

        self.usuario_mostrado = QLabel(
            "Ingrese una cédula para consultar al usuario."
        )
        self.usuario_mostrado.setWordWrap(True)
        self.usuario_mostrado.setStyleSheet("""
            padding: 8px;
            border: 1px solid #D8CDBD;
            border-radius: 5px;
        """)
        formulario.addRow("Usuario:", self.usuario_mostrado)

        # Fechas
        self.fecha_prestamo = QDateEdit()
        self.fecha_prestamo.setDate(QDate.currentDate())
        self.fecha_prestamo.setCalendarPopup(True)
        self.fecha_prestamo.setDisplayFormat("dd/MM/yyyy")
        formulario.addRow("Fecha de préstamo:", self.fecha_prestamo)

        self.fecha_devolucion = QDateEdit()
        self.fecha_devolucion.setDate(
            QDate.currentDate().addDays(7)
        )
        self.fecha_devolucion.setCalendarPopup(True)
        self.fecha_devolucion.setDisplayFormat("dd/MM/yyyy")
        formulario.addRow(
            "Fecha límite de devolución:",
            self.fecha_devolucion
        )

        tarjeta_layout.addLayout(formulario)

        # Botón registrar / guardar cambios
        botones = QHBoxLayout()
        botones.addStretch()

        self.btn_registrar = QPushButton("+ Registrar préstamo")
        self.btn_registrar.setObjectName("btnPrincipal")
        self.btn_registrar.setStyleSheet("""
            QPushButton {
                background-color: #234B4A;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1C3E3D;
            }
            QPushButton:pressed {
                background-color: #163332;
            }
        """)
        self.btn_registrar.clicked.connect(self.registrar_prestamo)
        botones.addWidget(self.btn_registrar)

        tarjeta_layout.addLayout(botones)
        principal.addWidget(tarjeta)

        # ---------- Búsqueda y filtro de préstamos ----------
        barra = QHBoxLayout()

        self.buscar = QLineEdit()
        self.buscar.setPlaceholderText(
            "Buscar préstamos por código, libro, usuario o cédula..."
        )
        self.buscar.textChanged.connect(self.filtrar)
        barra.addWidget(self.buscar)

        self.filtro_estado = QComboBox()
        self.filtro_estado.addItems([
            "Todos", "Prestado", "Devuelto", "Vencido"
        ])
        self.filtro_estado.currentTextChanged.connect(self.filtrar)
        self.filtro_estado.setStyleSheet("""
            QComboBox {
                background-color: white;
                color: #332C27;
                padding: 6px;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFDF8;
                color: #332C27;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #8B5E3C;
                color: white;
            }
        """)
        barra.addWidget(self.filtro_estado)

        principal.addLayout(barra)

        # ---------- Tabla ----------
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(9)

        self.tabla.setHorizontalHeaderLabels([
            "Código", "Código libro", "Libro", "Usuario", "Cédula",
            "Préstamo", "Fecha límite", "Estado", "Acciones"
        ])

        self.tabla.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )
        self.tabla.setSelectionMode(
            QAbstractItemView.SingleSelection
        )
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setMinimumHeight(300)

        principal.addWidget(self.tabla)

        self.cargar_prestamos()

    # ---------- Conexión ----------
    def abrir_conexion(self):
        conexion = conectar()

        if conexion is None:
            raise Exception(
                "No se pudo conectar con la base de datos."
            )

        return conexion

    def mostrar_error(self, mensaje):
        QMessageBox.warning(self, "Aviso", mensaje)

# ---------- Búsqueda de libros ----------
    def buscar_libros(self, texto=None):
        self.resultados_libros.clear()
        self.resultados_libros.addItem(
            "Seleccione un libro...", None
        )
        self.libro_seleccionado = None

        if not texto:
            return

        sesion = obtener_sesion()

        try:
            libros = (
                sesion.query(Libro)
                .filter(
                    Libro.estado == "Disponible",
                    (
                        Libro.codigo.ilike(f"%{texto}%") |
                        Libro.titulo.ilike(f"%{texto}%") |
                        Libro.autor.ilike(f"%{texto}%") |
                        Libro.edicion.ilike(f"%{texto}%")
                    )
                )
                .order_by(Libro.titulo, Libro.edicion)
                .all()
            )

            for libro in libros:
                edicion = str(libro.edicion or "").strip()

                datos = {
                    "codigo": libro.codigo,
                    "titulo": libro.titulo,
                    "autor": libro.autor,
                    "edicion": edicion,
                    "estado": libro.estado
                }

                nombre = libro.titulo

                if edicion:
                    nombre += f" - {edicion}"

                self.resultados_libros.addItem(
                    f"{libro.codigo} - {nombre} ({libro.autor})",
                    datos
                )

        except Exception as e:
            self.mostrar_error(
                f"Error al buscar libros: {e}"
            )

        finally:
            sesion.close()

    def seleccionar_libro(self, indice):
        dato = self.resultados_libros.itemData(indice)
        self.libro_seleccionado = dato

        if not dato:
            self.libro_mostrado.setText(
                "Seleccione un libro de los resultados."
            )
            return

        estado = dato["estado"].strip().lower()
        edicion = dato.get("edicion", "")

        nombre = dato["titulo"]

        if edicion:
            nombre += f" - {edicion}"

        if estado == "disponible":
            self.libro_mostrado.setText(
                f'{dato["codigo"]} — {nombre} — '
                f'{dato["autor"]}\nEstado: Disponible'
            )
        else:
            self.libro_mostrado.setText(
                f'{dato["codigo"]} — {nombre} — '
                f'{dato["autor"]}\n'
                f'Estado: {dato["estado"]}. '
                "Este ejemplar no se puede prestar."
            )

    # ---------- Usuarios ----------
    def consultar_usuario(self):
        cedula = self.cedula_usuario.text().strip()
        self.usuario_seleccionado = None

        if not cedula:
            self.usuario_mostrado.setText(
                "Ingrese una cédula para consultar al usuario."
            )
            return

        try:
            usuario = self.buscar_usuario(cedula)

            if not usuario:
                self.usuario_mostrado.setText(
                    "Usuario no encontrado. "
                    "Regístrelo primero en el módulo Usuarios."
                )
                return

            self.usuario_seleccionado = usuario
            self.usuario_mostrado.setText(
                f'Usuario encontrado: {usuario["nombre"]}'
            )

            vencidos = self.obtener_vencidos(cedula)

            if vencidos:
                detalle = "\n".join(
                    f'• {p["libro"]} '
                    f'(fecha límite: {p["fecha_devolucion"]})'
                    for p in vencidos
                )

                QMessageBox.warning(
                    self,
                    "Devoluciones vencidas",
                    "Este usuario tiene préstamos vencidos:\n\n"
                    + detalle
                    + "\n\nDebe registrar la devolución antes "
                    "de un nuevo préstamo."
                )

        except Exception as error:
            self.mostrar_error(
                "No se pudo consultar el usuario.\n"
                "Comprueba las columnas de la tabla usuarios "
                "y de la tabla prestamos.\n\n"
                + str(error)
            )

   # ---------- Buscar usuario por cédula ----------
    def buscar_usuario(self, cedula):
        sesion = obtener_sesion()

        try:
            usuario = (
                sesion.query(Usuario)
                .filter(Usuario.cedula == cedula)
                .first()
            )

            if not usuario:
                return None

            return {
                "cedula": str(usuario.cedula),
                "nombre": str(usuario.nombre or "").strip()
            }

        except Exception as e:
            self.mostrar_error(f"Error al buscar usuario: {e}")
            return None

        finally:
            sesion.close()


  # ---------- Obtener préstamos vencidos ----------
    def obtener_vencidos(self, cedula):
        sesion = obtener_sesion()

        try:
            prestamos = (
                sesion.query(Prestamo)
                .filter(
                    Prestamo.cedula_usuario == cedula,
                    Prestamo.estado.in_(["Prestado", "Vencido"]),
                    Prestamo.fecha_devolucion < date.today()
                )
                .all()
            )

            return [
                {
                    "libro": prestamo.libro,
                    "fecha_devolucion": str(prestamo.fecha_devolucion)
                }
                for prestamo in prestamos
            ]

        except Exception as e:
            self.mostrar_error(f"Error al consultar préstamos vencidos: {e}")
            return []

        finally:
            sesion.close()

    # ---------- Código automático ----------
   
# ---------- Generar código de préstamo ----------
    def generar_codigo(self, sesion):
        ultimo = (
            sesion.query(Prestamo.codigo_prestamo)
            .filter(Prestamo.codigo_prestamo.like("P-%"))
            .order_by(Prestamo.codigo_prestamo.desc())
            .first()
        )

        if not ultimo or not ultimo[0]:
            return "P-001"

        try:
            numero = int(str(ultimo[0]).split("-")[-1]) + 1
        except ValueError:
            numero = 1

        return f"P-{numero:03d}"

   # ---------- Registrar préstamo ----------
    def registrar_prestamo(self):

        # Si estamos editando, guardar las fechas.
        if self.fila_editando is not None:
            fecha_p = self.fecha_prestamo.date()
            fecha_d = self.fecha_devolucion.date()

            if fecha_d < fecha_p:
                self.mostrar_error(
                    "La fecha límite no puede ser anterior "
                    "a la fecha del préstamo."
                )
                return

            sesion = obtener_sesion()

            try:
                prestamo = (
                    sesion.query(Prestamo)
                    .filter(
                        Prestamo.codigo_prestamo == self.fila_editando,
                        Prestamo.estado.in_(["Prestado", "Vencido"])
                    )
                    .first()
                )

                if not prestamo:
                    self.mostrar_error(
                        "No se pudo modificar el préstamo. "
                        "Comprueba que siga activo."
                    )
                    return

                prestamo.fecha_prestamo = date(
                    fecha_p.year(), fecha_p.month(), fecha_p.day()
                )
                prestamo.fecha_devolucion = date(
                    fecha_d.year(), fecha_d.month(), fecha_d.day()
                )

                sesion.commit()

                QMessageBox.information(
                    self,
                    "Cambios guardados",
                    "Las fechas se actualizaron correctamente."
                )

                self.limpiar_formulario()
                self.cargar_prestamos()

            except Exception as error:
                sesion.rollback()
                self.mostrar_error(
                    "No se pudieron guardar los cambios.\n\n"
                    + str(error)
                )

            finally:
                sesion.close()

            return

        # Validar el libro seleccionado.
        libro = self.libro_seleccionado

        if not libro:
            self.mostrar_error(
                "Primero busque y seleccione un libro."
            )
            return

        if libro["estado"].strip().lower() != "disponible":
            self.mostrar_error(
                "Este libro no está disponible. "
                "Seleccione otro ejemplar."
            )
            return

        # Validar al usuario.
        cedula = self.cedula_usuario.text().strip()

        if not cedula or not self.usuario_seleccionado:
            self.consultar_usuario()

            if not self.usuario_seleccionado:
                self.mostrar_error(
                    "Ingrese la cédula de un usuario registrado."
                )
                return

        # Verificar que la cédula corresponda al usuario consultado.
        if self.usuario_seleccionado["cedula"] != cedula:
            self.consultar_usuario()

            if not self.usuario_seleccionado:
                self.mostrar_error(
                    "No se pudo verificar al usuario."
                )
                return

        # No permitir préstamos si hay devoluciones vencidas.
        try:
            vencidos = self.obtener_vencidos(cedula)
        except Exception as error:
            self.mostrar_error(
                "No se pudieron comprobar los préstamos vencidos.\n\n"
                + str(error)
            )
            return

        if vencidos:
            self.mostrar_error(
                "No se puede registrar el préstamo porque el "
                "usuario tiene devoluciones vencidas."
            )
            return

        fecha_p = self.fecha_prestamo.date()
        fecha_d = self.fecha_devolucion.date()

        if fecha_d < fecha_p:
            self.mostrar_error(
                "La fecha límite no puede ser anterior "
                "a la fecha del préstamo."
            )
            return

        sesion = obtener_sesion()

        try:
            # Comprobar nuevamente la disponibilidad.
            libro_db = (
                sesion.query(Libro)
                .filter(Libro.codigo == libro["codigo"])
                .first()
            )

            if (
                not libro_db
                or str(libro_db.estado or "").strip().lower()
                != "disponible"
            ):
                self.mostrar_error(
                    "El libro ya no está disponible. "
                    "Vuelva a buscarlo."
                )
                return

            # Generar código del préstamo.
            codigo = self.generar_codigo(sesion)
            nombre_usuario = self.usuario_seleccionado["nombre"]

            nombre_libro = libro["titulo"]

            if libro.get("edicion"):
                nombre_libro += f' - {libro["edicion"]}'

            titulo_autor = (
                f'{nombre_libro} — {libro["autor"]}'
            )

            # Crear el préstamo.
            nuevo_prestamo = Prestamo(
                codigo_prestamo=codigo,
                codigo_libro=libro["codigo"],
                libro=titulo_autor,
                usuario=nombre_usuario,
                cedula_usuario=cedula,
                fecha_prestamo=date(
                    fecha_p.year(), fecha_p.month(), fecha_p.day()
                ),
                fecha_devolucion=date(
                    fecha_d.year(), fecha_d.month(), fecha_d.day()
                ),
                estado="Prestado"
            )

            sesion.add(nuevo_prestamo)

            # Actualizar el estado del libro.
            libro_db.estado = "Prestado"

            sesion.commit()

            QMessageBox.information(
                self,
                "Préstamo registrado",
                f"Se registró el préstamo {codigo}."
            )

            self.limpiar_formulario()
            self.cargar_prestamos()

        except Exception as error:
            sesion.rollback()

            self.mostrar_error(
                "No se pudo registrar el préstamo.\n\n"
                "Comprueba las columnas de las tablas libros, "
                "usuarios y prestamos.\n\n"
                + str(error)
            )

        finally:
            sesion.close()

    # ---------- Cargar préstamos ----------
   # ---------- Cargar préstamos ----------
    def cargar_prestamos(self):
        sesion = obtener_sesion()

        try:
            prestamos = (
                sesion.query(Prestamo)
                .order_by(
                    Prestamo.fecha_prestamo.desc(),
                    Prestamo.codigo_prestamo.desc()
                )
                .all()
            )

            self.prestamos = [
                (
                    p.codigo_prestamo,
                    p.codigo_libro,
                    p.libro,
                    p.usuario,
                    p.cedula_usuario,
                    p.fecha_prestamo,
                    p.fecha_devolucion,
                    p.estado
                )
                for p in prestamos
            ]

            self.tabla.setRowCount(0)

            hoy = QDate.currentDate()

            for datos in self.prestamos:
                (
                    codigo, codigo_libro, libro, usuario,
                    cedula, fecha_p, fecha_d, estado
                ) = datos

                fecha_d_q = self.convertir_fecha(fecha_d)
                estado_mostrado = str(estado or "Prestado")

                if (
                    estado_mostrado == "Prestado"
                    and fecha_d_q.isValid()
                    and fecha_d_q < hoy
                ):
                    estado_mostrado = "Vencido"

                fila = self.tabla.rowCount()
                self.tabla.insertRow(fila)

                valores = [
                    codigo,
                    codigo_libro,
                    libro,
                    usuario,
                    cedula,
                    self.formatear_fecha(fecha_p),
                    self.formatear_fecha(fecha_d),
                    estado_mostrado
                ]

                for columna, valor in enumerate(valores):
                    item = QTableWidgetItem(str(valor or ""))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tabla.setItem(fila, columna, item)

                boton = QPushButton("⋮")
                boton.setObjectName("btnAccion")
                boton.setStyleSheet("""
                    QPushButton {
                        border: none;
                        background-color: transparent;
                        color: #332C27;
                        font-size: 20px;
                    }
                    QPushButton:hover {
                        background-color: transparent;
                    }
                """)

                boton.clicked.connect(
                    lambda checked=False, b=boton, f=fila:
                    self.mostrar_menu(b, f)
                )

                self.tabla.setCellWidget(fila, 8, boton)

            self.filtrar()

        except Exception as error:
            self.mostrar_error(
                "No se pudieron cargar los préstamos.\n\n"
                + str(error)
            )

        finally:
            sesion.close()

    # ---------- Manejo de fechas ----------
    def convertir_fecha(self, fecha):
        if isinstance(fecha, QDate):
            return fecha

        if (
            hasattr(fecha, "year")
            and hasattr(fecha, "month")
            and hasattr(fecha, "day")
        ):
            return QDate(
                fecha.year,
                fecha.month,
                fecha.day
            )

        texto = str(fecha or "")
        return QDate.fromString(texto[:10], "yyyy-MM-dd")

    def formatear_fecha(self, fecha):
        fecha_q = self.convertir_fecha(fecha)

        if fecha_q.isValid():
            return fecha_q.toString("dd/MM/yyyy")

        return str(fecha or "")

    # ---------- Menú de acciones ----------
    def mostrar_menu(self, boton, fila):
        menu = QMenu(self)

        detalles = menu.addAction("Ver detalles")
        editar = menu.addAction("Editar fechas")
        devolver = menu.addAction("Registrar devolución")
        eliminar = menu.addAction("Eliminar")

        accion = menu.exec(
            boton.mapToGlobal(boton.rect().bottomLeft())
        )

        if accion == detalles:
            datos = []

            for columna in range(8):
                encabezado = (
                    self.tabla.horizontalHeaderItem(columna).text()
                )

                elemento = self.tabla.item(fila, columna)
                valor = elemento.text() if elemento else ""

                datos.append(f"{encabezado}: {valor}")

            QMessageBox.information(
                self,
                "Detalles del préstamo",
                "\n".join(datos)
            )

        elif accion == editar:
            self.editar_prestamo(fila)

        elif accion == devolver:
            self.registrar_devolucion(fila)

        elif accion == eliminar:
            self.eliminar_prestamo(fila)

    # ---------- Editar préstamo ----------
    def editar_prestamo(self, fila):
        codigo = self.tabla.item(fila, 0).text()
        fecha_p = self.tabla.item(fila, 5).text()
        fecha_d = self.tabla.item(fila, 6).text()
        estado = self.tabla.item(fila, 7).text()

        if estado == "Devuelto":
            self.mostrar_error(
                "No se pueden editar las fechas de un "
                "préstamo devuelto."
            )
            return

        fecha_p_q = QDate.fromString(fecha_p, "dd/MM/yyyy")
        fecha_d_q = QDate.fromString(fecha_d, "dd/MM/yyyy")

        if not fecha_p_q.isValid() or not fecha_d_q.isValid():
            self.mostrar_error(
                "Las fechas del préstamo no son válidas."
            )
            return

        self.fila_editando = codigo
        self.fecha_prestamo.setDate(fecha_p_q)
        self.fecha_devolucion.setDate(fecha_d_q)
        self.btn_registrar.setText("Guardar cambios")

        QMessageBox.information(
            self,
            "Editar préstamo",
            "Modifica las fechas en el formulario y pulsa "
            "'Guardar cambios'."
        )

    # ---------- Eliminar préstamo ----------
    def eliminar_prestamo(self, fila):
        codigo = self.tabla.item(fila, 0).text()
        codigo_libro = self.tabla.item(fila, 1).text()

        respuesta = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Deseas eliminar el préstamo {codigo}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if respuesta != QMessageBox.Yes:
            return

        sesion = obtener_sesion()

        try:
            prestamo = (
                sesion.query(Prestamo)
                .filter(Prestamo.codigo_prestamo == codigo)
                .first()
            )

            if not prestamo:
                self.mostrar_error("El préstamo ya no existe.")
                return

            estado_real = str(prestamo.estado or "").strip()

            if estado_real == "Devuelto":
                QMessageBox.warning(
                    self,
                    "No se puede eliminar",
                    "Este préstamo ya fue devuelto.\n\n"
                    "Se conservará el registro para proteger "
                    "el historial de la biblioteca."
                )
                return

            if estado_real in ("Prestado", "Vencido"):
                libro = (
                    sesion.query(Libro)
                    .filter(Libro.codigo == codigo_libro)
                    .first()
                )

                if libro and libro.estado == "Prestado":
                    libro.estado = "Disponible"

            sesion.delete(prestamo)
            sesion.commit()

            if self.fila_editando == codigo:
                self.limpiar_formulario()

            QMessageBox.information(
                self,
                "Préstamo eliminado",
                "El registro se eliminó correctamente."
            )

            self.cargar_prestamos()

        except Exception as error:
            sesion.rollback()

            QMessageBox.critical(
                self,
                "Error",
                str(error)
            )

        finally:
            sesion.close()
           
    # ---------- Registrar devolución ----------
    def registrar_devolucion(self, fila):
        codigo_prestamo = self.tabla.item(fila, 0).text()
        codigo_libro = self.tabla.item(fila, 1).text()
        estado = self.tabla.item(fila, 7).text()

        if estado == "Devuelto":
            QMessageBox.information(
                self,
                "Información",
                "Este préstamo ya está devuelto."
            )
            return

        respuesta = QMessageBox.question(
            self,
            "Confirmar devolución",
            "¿Confirmas que el libro fue devuelto?",
            QMessageBox.Yes | QMessageBox.No
        )

        if respuesta != QMessageBox.Yes:
            return

        sesion = obtener_sesion()

        try:
            prestamo = (
                sesion.query(Prestamo)
                .filter(
                    Prestamo.codigo_prestamo == codigo_prestamo
                )
                .first()
            )

            if not prestamo:
                self.mostrar_error("El préstamo ya no existe.")
                return

            libro = (
                sesion.query(Libro)
                .filter(Libro.codigo == codigo_libro)
                .first()
            )

            prestamo.estado = "Devuelto"

            if libro:
                estado_libro = str(
                    libro.estado or ""
                ).strip().lower()

                if estado_libro == "prestado":
                    libro.estado = "Disponible"

            sesion.commit()

            mensaje = (
                "La devolución se registró correctamente."
            )

            if libro and str(libro.estado or "").strip().lower() == "en mantenimiento":
                mensaje += (
                    "\n\nEl libro permanece en mantenimiento "
                    "y no está disponible para nuevos préstamos."
                )
            else:
                mensaje += "\nEl libro volvió a estar disponible."

            QMessageBox.information(
                self,
                "Devolución registrada",
                mensaje
            )

            self.cargar_prestamos()

        except Exception as error:
            sesion.rollback()

            self.mostrar_error(
                "No se pudo registrar la devolución.\n\n"
                + str(error)
            )

        finally:
            sesion.close()
            




    # ---------- Limpiar formulario ----------
    def limpiar_formulario(self):
        self.buscar_libro.clear()

        self.resultados_libros.blockSignals(True)
        self.resultados_libros.clear()
        self.resultados_libros.addItem(
            "Seleccione un libro...", None
        )
        self.resultados_libros.blockSignals(False)

        self.libro_seleccionado = None
        self.libro_mostrado.setText(
            "Seleccione un libro de los resultados."
        )

        self.cedula_usuario.clear()
        self.usuario_seleccionado = None
        self.usuario_mostrado.setText(
            "Ingrese una cédula para consultar al usuario."
        )

        self.fecha_prestamo.setDate(QDate.currentDate())
        self.fecha_devolucion.setDate(
            QDate.currentDate().addDays(7)
        )

        self.btn_registrar.setText("+ Registrar préstamo")
        self.fila_editando = None

    # ---------- Filtrar tabla ----------
    def filtrar(self, *args):
        texto = self.buscar.text().strip().lower()
        estado_filtro = self.filtro_estado.currentText()

        for fila in range(self.tabla.rowCount()):
            coincide_texto = any(
                texto in (
                    self.tabla.item(fila, columna).text().lower()
                    if self.tabla.item(fila, columna)
                    else ""
                )
                for columna in range(8)
            )

            estado_item = self.tabla.item(fila, 7)
            estado = (
                estado_item.text() if estado_item else ""
            )

            coincide_estado = (
                estado_filtro == "Todos"
                or estado == estado_filtro
            )

            self.tabla.setRowHidden(
                fila,
                not (coincide_texto and coincide_estado)
            )