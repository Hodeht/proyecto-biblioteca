from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QFormLayout,
    QHeaderView,
    QMessageBox,
    QFrame,
    QScrollArea,
    QMenu
)

from base_datos.conexion import conectar
from base_datos.conexion_orm import obtener_sesion
from servicios.usuario_servicio import UsuarioServicio


class Usuarios(QWidget):

    def __init__(self, volver):
        super().__init__()

        self.volver = volver
        self.fila_editando = None

        # ÁREA DESPLAZABLE
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        contenido = QWidget()
        scroll.setWidget(contenido)

        principal = QVBoxLayout(contenido)
        principal.setContentsMargins(30, 25, 30, 25)
        principal.setSpacing(15)

        ventana = QVBoxLayout(self)
        ventana.setContentsMargins(0, 0, 0, 0)
        ventana.addWidget(scroll)

        # ENCABEZADO
        encabezado = QHBoxLayout()
        textos = QVBoxLayout()

        titulo = QLabel("Administración de usuarios")
        titulo.setObjectName("tituloPagina")

        descripcion = QLabel(
            "Registre, consulte y administre los usuarios de la biblioteca."
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

        # FORMULARIO
        formulario_frame = QFrame()
        formulario_frame.setObjectName("tarjeta")
        formulario_frame.setGraphicsEffect(None)

        formulario = QFormLayout(formulario_frame)
        formulario.setContentsMargins(20, 15, 20, 15)
        formulario.setSpacing(12)

        self.nombre = QLineEdit()
        self.nombre.setPlaceholderText("Nombre completo")
        self.nombre.setGraphicsEffect(None)

        self.cedula = QLineEdit()
        self.cedula.setPlaceholderText("Número de cédula")
        self.cedula.setGraphicsEffect(None)

        self.telefono = QLineEdit()
        self.telefono.setPlaceholderText("Número de teléfono")
        self.telefono.setGraphicsEffect(None)

        self.direccion = QLineEdit()
        self.direccion.setPlaceholderText("Dirección del usuario")
        self.direccion.setGraphicsEffect(None)

        formulario.addRow("Nombre:", self.nombre)
        formulario.addRow("Cédula:", self.cedula)
        formulario.addRow("Teléfono:", self.telefono)
        formulario.addRow("Dirección:", self.direccion)

        principal.addWidget(formulario_frame)

        # BOTONES
        botones = QHBoxLayout()

        self.registrar = QPushButton("Registrar usuario")
        self.registrar.setObjectName("btnPrincipal")
        self.registrar.clicked.connect(self.registrar_usuario)

        limpiar = QPushButton("Limpiar")
        limpiar.setObjectName("btnSecundario")
        limpiar.clicked.connect(self.limpiar)

        botones.addWidget(self.registrar)
        botones.addWidget(limpiar)
        botones.addStretch()

        principal.addLayout(botones)

        # BÚSQUEDA
        self.buscar = QLineEdit()
        self.buscar.setPlaceholderText(
            "Buscar por nombre o cédula..."
        )
        self.buscar.textChanged.connect(self.buscar_usuarios)

        principal.addWidget(self.buscar)

        # TABLA
        self.tabla = QTableWidget(0, 6)

        self.tabla.setHorizontalHeaderLabels([
            "ID",
            "Nombre",
            "Cédula",
            "Teléfono",
            "Dirección",
            "Acciones"
        ])

        self.tabla.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setMinimumHeight(350)

        principal.addWidget(self.tabla)

        # CARGAR DATOS
        self.cargar_usuarios()

    # REGISTRAR O ACTUALIZAR USUARIO
    # REGISTRAR O ACTUALIZAR USUARIO MEDIANTE ORM
    def registrar_usuario(self):

        nombre = self.nombre.text().strip()
        cedula = self.cedula.text().strip()
        telefono = self.telefono.text().strip()
        direccion = self.direccion.text().strip()

        if not nombre or not cedula:
            QMessageBox.warning(
                self,
                "Datos incompletos",
                "Ingrese el nombre y la cédula del usuario."
            )
            return

        sesion = obtener_sesion()

        try:
            # COMPROBAR QUE LA CÉDULA NO ESTÉ REPETIDA
            usuarios = UsuarioServicio.obtener_usuarios(sesion)

            cedula_repetida = any(
                usuario.cedula == cedula
                and usuario.id != self.fila_editando
                for usuario in usuarios
            )

            if cedula_repetida:
                QMessageBox.warning(
                    self,
                    "Cédula registrada",
                    "Ya existe otro usuario con esa cédula."
                )
                return

            # REGISTRAR USUARIO NUEVO
            if self.fila_editando is None:

                UsuarioServicio.crear_usuario(
                    sesion,
                    nombre,
                    cedula,
                    telefono,
                    direccion
                )

                mensaje = "El usuario se registró correctamente."
                titulo_mensaje = "Usuario registrado"

            # ACTUALIZAR USUARIO EXISTENTE
            else:

                usuario = UsuarioServicio.actualizar_usuario(
                    sesion,
                    self.fila_editando,
                    nombre=nombre,
                    cedula=cedula,
                    telefono=telefono,
                    direccion=direccion
                )

                if usuario is None:
                    QMessageBox.warning(
                        self,
                        "Usuario no encontrado",
                        "No se encontró el usuario que deseas actualizar."
                    )
                    return

                mensaje = "Los datos se actualizaron correctamente."
                titulo_mensaje = "Usuario actualizado"

            QMessageBox.information(
                self,
                titulo_mensaje,
                mensaje
            )

            self.limpiar()
            self.cargar_usuarios()

        except Exception as error:
            sesion.rollback()

            QMessageBox.warning(
                self,
                "Error al guardar",
                f"No se pudo guardar el usuario.\n\n{error}"
            )

        finally:
            sesion.close()

    # CARGAR USUARIOS MEDIANTE ORM
    def cargar_usuarios(self):

        sesion = obtener_sesion()

        try:
            usuarios = UsuarioServicio.obtener_usuarios(sesion)

            registros = [
                (
                    usuario.id,
                    usuario.nombre,
                    usuario.cedula,
                    usuario.telefono,
                    usuario.direccion
                )
                for usuario in usuarios
            ]

            self.mostrar_usuarios(registros)

        except Exception as error:
            QMessageBox.warning(
                self,
                "Error",
                f"No se pudieron cargar los usuarios.\n\n{error}"
            )

        finally:
            sesion.close()

    # MOSTRAR USUARIOS
    def mostrar_usuarios(self, registros):

        self.tabla.setRowCount(0)

        for fila, registro in enumerate(registros):
            self.tabla.insertRow(fila)

            for columna, valor in enumerate(registro):
                texto = "" if valor is None else str(valor)

                elemento = QTableWidgetItem(texto)

                self.tabla.setItem(
                    fila,
                    columna,
                    elemento
                )

            # BOTÓN DE TRES PUNTITOS
            boton_acciones = QPushButton("⋮")
            boton_acciones.setToolTip("Ver opciones del usuario")

            boton_acciones.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #8B5E3C;
                    font-size: 20px;
                    font-weight: bold;
                    border: none;
                    padding: 2px 10px;
                }

                QPushButton:hover {
                    background-color: #E8D6C4;
                    border-radius: 5px;
                }
            """)

            boton_acciones.clicked.connect(
                lambda checked=False, f=fila, b=boton_acciones:
                self.mostrar_menu(b, f)
            )

            self.tabla.setCellWidget(
                fila,
                5,
                boton_acciones
            )

            self.tabla.setRowHeight(fila, 40)

    # MENÚ DE ACCIONES
    def mostrar_menu(self, boton, fila):

        menu = QMenu(self)

        menu.setStyleSheet("""
            QMenu {
                background-color: #FFFDF8;
                color: #332C27;
                border: 1px solid #D8C8B8;
                padding: 5px;
            }

            QMenu::item {
                padding: 8px 20px;
            }

            QMenu::item:selected {
                background-color: #E8D6C4;
                color: #332C27;
            }
        """)

        detalles = menu.addAction("Ver detalles")
        prestamos = menu.addAction("Ver préstamos")
        menu.addSeparator()
        editar = menu.addAction("Editar")
        eliminar = menu.addAction("Eliminar")

        accion = menu.exec(
            boton.mapToGlobal(boton.rect().bottomLeft())
        )

        if accion == detalles:
            self.ver_detalles(fila)

        elif accion == prestamos:
            self.ver_prestamos(fila)

        elif accion == editar:
            self.editar_usuario(fila)

        elif accion == eliminar:
            self.eliminar_usuario(fila)

    # VER DETALLES DEL USUARIO
    def ver_detalles(self, fila):

        datos = []

        for columna in range(5):
            encabezado = self.tabla.horizontalHeaderItem(
                columna
            ).text()

            elemento = self.tabla.item(fila, columna)
            valor = elemento.text() if elemento else ""

            datos.append(f"{encabezado}: {valor}")

        QMessageBox.information(
            self,
            "Detalles del usuario",
            "\n".join(datos)
        )

    # VER PRÉSTAMOS DEL USUARIO MEDIANTE ORM
    def ver_prestamos(self, fila):

        elemento_cedula = self.tabla.item(fila, 2)
        elemento_nombre = self.tabla.item(fila, 1)

        if not elemento_cedula or not elemento_nombre:
            return

        cedula = elemento_cedula.text()
        nombre = elemento_nombre.text()

        sesion = obtener_sesion()

        try:
            from modelos.prestamo import Prestamo

            registros = sesion.query(Prestamo).filter_by(
                cedula_usuario=cedula
            ).order_by(
                Prestamo.fecha_prestamo.desc()
            ).all()

            if not registros:
                QMessageBox.information(
                    self,
                    "Préstamos del usuario",
                    f"Usuario: {nombre}\n"
                    f"Cédula: {cedula}\n\n"
                    "Este usuario todavía no tiene préstamos registrados."
                )
                return

            pendientes = 0
            vencidos = 0
            detalles = []

            from datetime import date

            for prestamo in registros:

                estado_actual = prestamo.estado or ""

                if (
                    estado_actual in ("Prestado", "Vencido")
                    and prestamo.fecha_devolucion
                    and prestamo.fecha_devolucion < date.today()
                ):
                    estado_actual = "Vencido"

                if estado_actual in ("Prestado", "Vencido"):
                    pendientes += 1

                if estado_actual == "Vencido":
                    vencidos += 1

                detalles.append(
                    f"Código de préstamo: {prestamo.codigo_prestamo}\n"
                    f"Libro: {prestamo.libro or 'Sin título'}\n"
                    f"Fecha de préstamo: {prestamo.fecha_prestamo or 'No registrada'}\n"
                    f"Fecha límite: {prestamo.fecha_devolucion or 'No registrada'}\n"
                    f"Estado: {estado_actual}\n"
                )

            resumen = (
                f"Usuario: {nombre}\n"
                f"Cédula: {cedula}\n\n"
                f"Libros pendientes: {pendientes}\n"
                f"Libros vencidos: {vencidos}\n\n"
                "HISTORIAL DE PRÉSTAMOS\n\n"
            )

            mensaje = resumen + "\n--------------------\n".join(detalles)

            QMessageBox.information(
                self,
                "Historial de préstamos",
                mensaje
            )

        except Exception as error:
            QMessageBox.warning(
                self,
                "Error",
                "No se pudieron consultar los préstamos.\n\n"
                + str(error)
            )

        finally:
            sesion.close()

    # EDITAR USUARIO
    def editar_usuario(self, fila):

        elemento_id = self.tabla.item(fila, 0)

        if not elemento_id:
            return

        self.fila_editando = int(elemento_id.text())

        self.nombre.setText(self.tabla.item(fila, 1).text())
        self.cedula.setText(self.tabla.item(fila, 2).text())
        self.telefono.setText(self.tabla.item(fila, 3).text())
        self.direccion.setText(self.tabla.item(fila, 4).text())

        self.registrar.setText("Guardar cambios")

        QMessageBox.information(
            self,
            "Editar usuario",
            "Modifica los datos del formulario y pulsa "
            "'Guardar cambios' para actualizar el usuario."
        )

    # ELIMINAR USUARIO
  # ELIMINAR USUARIO MEDIANTE ORM
    def eliminar_usuario(self, fila):

        elemento_id = self.tabla.item(fila, 0)
        elemento_nombre = self.tabla.item(fila, 1)
        elemento_cedula = self.tabla.item(fila, 2)

        if not elemento_id or not elemento_cedula:
            return

        usuario_id = int(elemento_id.text())
        nombre = elemento_nombre.text()
        cedula = elemento_cedula.text()

        respuesta = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Deseas eliminar al usuario {nombre}?\n\n"
            "Si tiene préstamos registrados, no se podrá eliminar "
            "para proteger su historial.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if respuesta != QMessageBox.Yes:
            return

        sesion = obtener_sesion()

        try:
            # COMPROBAR SI TIENE PRÉSTAMOS
            from modelos.prestamo import Prestamo

            cantidad = sesion.query(Prestamo).filter_by(
                cedula_usuario=cedula
            ).count()

            if cantidad > 0:
                QMessageBox.warning(
                    self,
                    "No se puede eliminar",
                    "Este usuario tiene préstamos registrados.\n\n"
                    "No se eliminó para proteger el historial "
                    "de préstamos."
                )
                return

            # ELIMINAR USUARIO
            eliminado = UsuarioServicio.eliminar_usuario(
                sesion,
                usuario_id
            )

            if not eliminado:
                QMessageBox.warning(
                    self,
                    "Usuario no encontrado",
                    "No se encontró el usuario que deseas eliminar."
                )
                return

            QMessageBox.information(
                self,
                "Usuario eliminado",
                "El usuario se eliminó correctamente."
            )

            self.cargar_usuarios()

        except Exception as error:
            sesion.rollback()

            QMessageBox.warning(
                self,
                "Error al eliminar",
                f"No se pudo eliminar el usuario.\n\n{error}"
            )

        finally:
            sesion.close()
       

    # BUSCAR USUARIOS
    # BUSCAR USUARIOS MEDIANTE ORM
    def buscar_usuarios(self, texto):

        sesion = obtener_sesion()

        try:
            from modelos.usuario import Usuario

            busqueda = texto.strip()

            consulta = sesion.query(Usuario)

            if busqueda:
                consulta = consulta.filter(
                    (Usuario.nombre.ilike(f"%{busqueda}%")) |
                    (Usuario.cedula.ilike(f"%{busqueda}%"))
                )

            usuarios = consulta.order_by(
                Usuario.id.desc()
            ).all()

            registros = [
                (
                    usuario.id,
                    usuario.nombre,
                    usuario.cedula,
                    usuario.telefono,
                    usuario.direccion
                )
                for usuario in usuarios
            ]

            self.mostrar_usuarios(registros)

        except Exception as error:
            QMessageBox.warning(
                self,
                "Error al buscar",
                f"No se pudieron buscar los usuarios.\n\n{error}"
            )

        finally:
            sesion.close()

    

    # LIMPIAR CAMPOS
    def limpiar(self):

        self.nombre.clear()
        self.cedula.clear()
        self.telefono.clear()
        self.direccion.clear()

        self.fila_editando = None
        self.registrar.setText("Registrar usuario")

        self.buscar.clear()
        self.nombre.setFocus()