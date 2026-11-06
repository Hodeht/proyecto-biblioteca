from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox,
    QAbstractItemView
)

import bcrypt

from base_datos.conexion_orm import obtener_sesion
from modelos.cuenta_acceso import Cuenta


class Cuentas(QWidget):

    def __init__(self, volver):
        super().__init__()

        self.volver = volver

        principal = QVBoxLayout(self)
        principal.setContentsMargins(30, 25, 30, 25)
        principal.setSpacing(12)

        
        titulo = QLabel("Gestión de cuentas")
        titulo.setObjectName("tituloPagina")

        descripcion = QLabel(
            "Administración de las cuentas de acceso a la biblioteca."
        )
        descripcion.setObjectName("descripcion")

        principal.addWidget(titulo)
        principal.addWidget(descripcion)

      
        formulario = QHBoxLayout()

        self.nombre = QLineEdit()
        self.nombre.setPlaceholderText("Nombre completo")

        self.usuario = QLineEdit()
        self.usuario.setPlaceholderText("Nombre de usuario")

        self.clave = QLineEdit()
        self.clave.setPlaceholderText("Contraseña")
        self.clave.setEchoMode(QLineEdit.EchoMode.Password)

        formulario.addWidget(self.nombre)
        formulario.addWidget(self.usuario)
        formulario.addWidget(self.clave)

        principal.addLayout(formulario)

        
        botones = QHBoxLayout()

        crear = QPushButton("Crear bibliotecario")
        crear.setObjectName("btnPrincipal")
        crear.clicked.connect(self.crear_cuenta)

        actualizar = QPushButton("Actualizar lista")
        actualizar.setObjectName("menuButton")
        actualizar.clicked.connect(self.cargar_cuentas)

        volver_boton = QPushButton("Volver al panel")
        volver_boton.setObjectName("menuButton")
        volver_boton.clicked.connect(self.volver)

        botones.addWidget(crear)
        botones.addWidget(actualizar)
        botones.addWidget(volver_boton)

        principal.addLayout(botones)

        
        self.tabla = QTableWidget(0, 5)

        self.tabla.setHorizontalHeaderLabels([
            "ID", "Nombre", "Usuario", "Estado", "Acción"
        ])

        encabezado = self.tabla.horizontalHeader()

        
        for columna in range(4):
            encabezado.setSectionResizeMode(
                columna,
                QHeaderView.ResizeMode.Stretch
            )

        encabezado.setSectionResizeMode(
            4,
            QHeaderView.ResizeMode.Fixed
        )

       
        self.tabla.setColumnWidth(4, 180)

        self.tabla.verticalHeader().setVisible(False)

        self.tabla.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.tabla.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.tabla.setAlternatingRowColors(True)

        principal.addWidget(self.tabla)

        self.cargar_cuentas()

    # Crear cuenta de bibliotecario
    def crear_cuenta(self):

        nombre = self.nombre.text().strip()
        usuario = self.usuario.text().strip()
        clave = self.clave.text()

        if not nombre or not usuario or not clave:
            QMessageBox.warning(
                self,
                "Datos incompletos",
                "Completá el nombre, el usuario y la contraseña."
            )
            return

        if len(clave) < 8:
            QMessageBox.warning(
                self,
                "Contraseña insegura",
                "La contraseña debe tener al menos 8 caracteres."
            )
            return


            # Conexión con SQLAlchemy: abre la sesión para consultar la base de datos
        sesion = obtener_sesion()

        try:
            cuenta_existente = (
                sesion.query(Cuenta)
                .filter(Cuenta.usuario == usuario)
                .first()
            )

            if cuenta_existente:
                QMessageBox.warning(
                    self,
                    "Usuario existente",
                    "Ese nombre de usuario ya está registrado."
                )
                return

            clave_cifrada = bcrypt.hashpw(
                clave.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")

            nueva_cuenta = Cuenta(
                nombre=nombre,
                usuario=usuario,
                clave=clave_cifrada,
                rol="bibliotecario",
                activo=True
            )

            sesion.add(nueva_cuenta)
            sesion.commit()

            QMessageBox.information(
                self,
                "Cuenta creada",
                "La cuenta del bibliotecario se creó correctamente."
            )

            self.nombre.clear()
            self.usuario.clear()
            self.clave.clear()

            self.cargar_cuentas()

        except Exception as error:
            sesion.rollback()

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo crear la cuenta.\n{error}"
            )

        finally:
            sesion.close()

        # Cierra la sesión de SQLAlchemy



    
    def cargar_cuentas(self):

        sesion = obtener_sesion()

        try:
            cuentas = (
                sesion.query(Cuenta)
                .filter(Cuenta.rol == "bibliotecario")
                .order_by(Cuenta.id.desc())
                .all()
            )

            self.tabla.setRowCount(0)

            for fila, cuenta in enumerate(cuentas):

                self.tabla.insertRow(fila)

                valores = [
                    cuenta.id,
                    cuenta.nombre,
                    cuenta.usuario,
                    "Activa" if cuenta.activo else "Desactivada"
                ]

                for columna, valor in enumerate(valores):

                    elemento = QTableWidgetItem(str(valor))

                    self.tabla.setItem(
                        fila,
                        columna,
                        elemento
                    )

                # Botón activar / desactivar
                boton = QPushButton(
                    "Desactivar" if cuenta.activo else "Activar"
                )

                boton.setObjectName("menuButton")
                boton.setMinimumSize(150, 35)
                boton.setMaximumWidth(160)

                boton.clicked.connect(
                    lambda checked=False,
                    id_cuenta=cuenta.id,
                    estado=cuenta.activo: self.cambiar_estado(
                        id_cuenta,
                        estado
                    )
                )

                self.tabla.setCellWidget(
                    fila,
                    4,
                    boton
                )

                
                self.tabla.setRowHeight(fila, 48)

        except Exception as error:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudieron cargar las cuentas.\n{error}"
            )

        finally:
            sesion.close()

   
    def cambiar_estado(self, identificador, activo):

        nuevo_estado = not bool(activo)

        respuesta = QMessageBox.question(
            self,
            "Confirmar cambio",
            "¿Querés cambiar el estado de esta cuenta?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if respuesta != QMessageBox.StandardButton.Yes:
            return

        sesion = obtener_sesion()

        try:
            cuenta = (
                sesion.query(Cuenta)
                .filter(
                    Cuenta.id == identificador,
                    Cuenta.rol == "bibliotecario"
                )
                .first()
            )

            if cuenta is None:
                QMessageBox.warning(
                    self,
                    "Cuenta no encontrada",
                    "No se encontró la cuenta seleccionada."
                )
                return

            cuenta.activo = nuevo_estado

            sesion.commit()

            self.cargar_cuentas()

        except Exception as error:
            sesion.rollback()

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo cambiar el estado.\n{error}"
            )

        finally:
            sesion.close()