from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QFrame,
    QMessageBox
)

import qtawesome as qta
import bcrypt
from base_datos.conexion import conectar


class InicioSesion(QWidget):

    def __init__(self, entrar):
        super().__init__()

        self.entrar = entrar
        self.setObjectName("pantallaLogin")

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setAlignment(Qt.AlignmentFlag.AlignCenter)

        tarjeta = QFrame()
        tarjeta.setObjectName("loginCard")
        tarjeta.setFixedWidth(450)

        layout = QVBoxLayout(tarjeta)
        layout.setContentsMargins(38, 32, 38, 30)
        layout.setSpacing(14)

        self.label_icono = QLabel()
        self.label_icono.setObjectName("loginIcon")
        self.label_icono.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icono_libro = qta.icon(
            "fa5s.book-open",
            color="#234B4A"
        )
        self.label_icono.setPixmap(icono_libro.pixmap(48, 48))

        titulo = QLabel("Biblioteca León")
        titulo.setObjectName("loginTitle")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitulo = QLabel("Sistema de Gestión Bibliotecaria")
        subtitulo.setObjectName("loginSub")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitulo.setWordWrap(True)

        self.usuario = QLineEdit()
        self.usuario.setObjectName("loginInput")
        self.usuario.setPlaceholderText("Ingrese su usuario")
        self.usuario.setFixedHeight(48)
        self.usuario.setClearButtonEnabled(True)

        self.clave = QLineEdit()
        self.clave.setObjectName("loginInput")
        self.clave.setPlaceholderText("Ingrese su contraseña")
        self.clave.setEchoMode(QLineEdit.EchoMode.Password)
        self.clave.setFixedHeight(48)

        self.accion_clave = self.clave.addAction(
            qta.icon("fa5s.eye", color="#756B61"),
            QLineEdit.ActionPosition.TrailingPosition
        )
        self.accion_clave.setToolTip("Mostrar contraseña")
        self.accion_clave.triggered.connect(self.mostrar_clave)

        self.boton = QPushButton("Iniciar sesión")
        self.boton.setObjectName("btnPrincipal")
        self.boton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.boton.setFixedHeight(48)
        self.boton.clicked.connect(self.validar)

        aviso = QLabel("Ingrese sus datos para acceder al sistema.")
        aviso.setObjectName("loginAviso")
        aviso.setAlignment(Qt.AlignmentFlag.AlignCenter)
        aviso.setWordWrap(True)

        layout.addWidget(self.label_icono)
        layout.addSpacing(4)
        layout.addWidget(titulo)
        layout.addWidget(subtitulo)
        layout.addSpacing(14)
        layout.addWidget(self.usuario)
        layout.addWidget(self.clave)
        layout.addSpacing(8)
        layout.addWidget(self.boton)
        layout.addSpacing(8)
        layout.addWidget(aviso)

        layout_principal.addWidget(tarjeta)

        self.usuario.returnPressed.connect(self.enfocar_clave)
        self.clave.returnPressed.connect(self.validar)

    def enfocar_clave(self):
        self.clave.setFocus()

    def mostrar_clave(self):
        if self.clave.echoMode() == QLineEdit.EchoMode.Password:
            self.clave.setEchoMode(QLineEdit.EchoMode.Normal)
            self.accion_clave.setIcon(
                qta.icon("fa5s.eye-slash", color="#756B61")
            )
            self.accion_clave.setToolTip("Ocultar contraseña")
        else:
            self.clave.setEchoMode(QLineEdit.EchoMode.Password)
            self.accion_clave.setIcon(
                qta.icon("fa5s.eye", color="#756B61")
            )
            self.accion_clave.setToolTip("Mostrar contraseña")

    def validar(self):
        usuario = self.usuario.text().strip()
        clave = self.clave.text()

        if not usuario or not clave:
            QMessageBox.warning(
                self,
                "Datos incompletos",
                "Ingrese el usuario y la contraseña."
            )
            return

        conexion = None
        cursor = None

        try:
            conexion = conectar()
            cursor = conexion.cursor()

            cursor.execute(
                """
                SELECT clave, rol, activo
                FROM cuentas_acceso
                WHERE usuario = %s
                """,
                (usuario,)
            )

            cuenta = cursor.fetchone()

            if cuenta is None:
                QMessageBox.warning(
                    self,
                    "Acceso denegado",
                    "El usuario o la contraseña son incorrectos."
                )
                return

            clave_guardada, rol, activo = cuenta

            if not activo or not bcrypt.checkpw(
                clave.encode("utf-8"),
                clave_guardada.encode("utf-8")
            ):
                QMessageBox.warning(
                    self,
                    "Acceso denegado",
                    "El usuario o la contraseña son incorrectos, "
                    "o la cuenta está desactivada."
                )
                return

            self.usuario_actual = usuario
            self.entrar(rol)

        except Exception as error:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo verificar el acceso.\n{error}"
            )

        finally:
            if cursor is not None:
                cursor.close()
            if conexion is not None:
                conexion.close()