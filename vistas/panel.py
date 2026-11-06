from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QFrame,
    QHeaderView
)
from PySide6.QtCore import Qt
import qtawesome as qta

from PySide6.QtWidgets import QGraphicsDropShadowEffect
from base_datos.conexion import conectar


class PanelPrincipal(QWidget):

    def __init__(
        self,
        abrir_registros,
        abrir_prestamos,
        abrir_usuarios,
        cerrar_sesion,
        abrir_cuentas,
        abrir_reportes
    ):
        super().__init__()

        self.abrir_registros = abrir_registros
        self.abrir_prestamos = abrir_prestamos
        self.abrir_usuarios = abrir_usuarios
        self.cerrar_sesion = cerrar_sesion
        self.abrir_cuentas = abrir_cuentas
        self.rol = None
        self.abrir_reportes = abrir_reportes

        
        
        principal = QHBoxLayout(self)
        principal.setContentsMargins(0, 0, 0, 0)
        principal.setSpacing(0)

        menu = QFrame()
        menu.setObjectName("menu")
        menu.setFixedWidth(225)

        menu_layout = QVBoxLayout(menu)
        menu_layout.setContentsMargins(15, 25, 15, 20)
        menu_layout.setSpacing(5)

        logo = QLabel("BIBLIOTECA LEÓN")
        logo.setObjectName("logo")

        sub = QLabel("Gestión bibliotecaria")
        sub.setObjectName("menuSub")

        menu_layout.addWidget(logo)
        menu_layout.addWidget(sub)
        menu_layout.addSpacing(20)

       
        inicio = QPushButton("  Inicio")
        inicio.setObjectName("menuButtonActivo")
        inicio.clicked.connect(self.actualizar_datos)

       #botone

        registros = QPushButton("  Registros")
        registros.setObjectName("menuButton")
        registros.clicked.connect(self.abrir_registros)

      
        prestamos = QPushButton("  Préstamos")
        prestamos.setObjectName("menuButton")
        prestamos.clicked.connect(self.abrir_prestamos)

        
        usuarios = QPushButton("  Usuarios")
        usuarios.setObjectName("menuButton")
        usuarios.clicked.connect(self.abrir_usuarios)

        
        reportes = QPushButton("  Reportes")
        reportes.setObjectName("menuButton")
        reportes.clicked.connect(self.abrir_reportes)

      
        self.gestion_cuentas = QPushButton(
            "  Gestión de cuentas"
        )
        self.gestion_cuentas.setObjectName("menuButton")
        self.gestion_cuentas.clicked.connect(
            self.abrir_gestion_cuentas
        )

        # se oculta si se inicia como biblio
        self.gestion_cuentas.hide()

        menu_layout.addWidget(inicio)
        menu_layout.addWidget(registros)
        menu_layout.addWidget(prestamos)
        menu_layout.addWidget(usuarios)
        menu_layout.addWidget(reportes)
        menu_layout.addWidget(self.gestion_cuentas)

        menu_layout.addStretch()

        
        salir = QPushButton("  Cerrar sesión")
        salir.setObjectName("menuButton")
        salir.clicked.connect(self.cerrar_sesion)
        menu_layout.addWidget(salir)

      
        contenido = QWidget()

        layout = QVBoxLayout(contenido)
        layout.setContentsMargins(35, 30, 35, 30)
        layout.setSpacing(10)

        titulo = QLabel("Panel principal")
        titulo.setObjectName("tituloPagina")

        descripcion = QLabel(
            "Resumen general de la gestión bibliotecaria."
        )
        descripcion.setObjectName("descripcion")

        layout.addWidget(titulo)
        layout.addWidget(descripcion)
        layout.addSpacing(15)

        
        tarjetas = QHBoxLayout()
        tarjetas.setSpacing(15)

        tarjetas.addWidget(
            self.crear_tarjeta(
                "Libros registrados",
                "0",
                "fa5s.book",
                "#234B4A"
            )
        )

        tarjetas.addWidget(
            self.crear_tarjeta(
                "Usuarios registrados",
                "0",
                "fa5s.users",
                "#234B4A"
            )
        )

        tarjetas.addWidget(
            self.crear_tarjeta(
                "Préstamos activos",
                "0",
                "fa5s.book-reader",
                "#234B4A"
            )
        )

        tarjetas.addWidget(
            self.crear_tarjeta(
                "Pendientes",
                "0",
                "fa5s.clock",
                "#9C5B48"
            )
        )

        layout.addLayout(tarjetas)
        layout.addSpacing(20)

        
        titulo_tabla = QLabel("Últimos registros")
        titulo_tabla.setStyleSheet(
            "font-size: 17px; font-weight: bold;"
        )

        layout.addWidget(titulo_tabla)

        self.tabla_libros = QTableWidget(0, 4)

        self.tabla_libros.setHorizontalHeaderLabels([
            "Código",
            "Título",
            "Categoría",
            "Estado"
        ])

        self.tabla_libros.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.tabla_libros.verticalHeader().setVisible(False)

        self.tabla_libros.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        layout.addWidget(self.tabla_libros)

        # MOSTRAR MENÚ Y CONTENIDO
        principal.addWidget(menu)
        principal.addWidget(contenido)

        self.actualizar_datos()

    
    def crear_tarjeta(
        self, titulo, numero, nombre_icono, color_icono
    ):
        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta")
        tarjeta.setMinimumHeight(130)


        tarjeta.setGraphicsEffect(None)
        tarjeta.setFrameShape(QFrame.NoFrame)
        tarjeta.setGraphicsEffect(None)


        tarjeta.setStyleSheet("""
            QFrame#tarjeta {
              background-color: #FFFDF8;
              border: 1px solid #D8CDBD;
               border-radius: 12px;
              }
            """)
        
        
        layout = QVBoxLayout(tarjeta)
        layout.setContentsMargins(18, 15, 18, 15)
        layout.setSpacing(8)

        # FILA SUPERIOR: TÍTULO E ICONO
        fila_superior = QHBoxLayout()
        fila_superior.setSpacing(8)

        nombre = QLabel(titulo)
        nombre.setObjectName("tarjetaTitulo")
        nombre.setWordWrap(True)

        # CONTENEDOR DEL ICONO
        fondo_icono = QFrame()
        fondo_icono.setFixedSize(42, 42)
        fondo_icono.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
               
            }
        """)

        icono_layout = QVBoxLayout(fondo_icono)
        icono_layout.setContentsMargins(0, 0, 0, 0)
        icono_layout.setAlignment(Qt.AlignCenter)

        icono_label = QLabel()
        icono_label.setPixmap(
            qta.icon(
                nombre_icono,
                color=color_icono
            ).pixmap(24, 24)
        )
        icono_label.setAlignment(Qt.AlignCenter)

        icono_layout.addWidget(icono_label)

        fila_superior.addWidget(nombre, 1)
        fila_superior.addWidget(fondo_icono, 0, Qt.AlignTop)

        # NÚMERO DE LA TARJETA
        cantidad = QLabel(numero)
        cantidad.setObjectName("tarjetaNumero")

        # GUARDAR REFERENCIAS PARA ACTUALIZAR LOS CONTADORES
        if titulo == "Libros registrados":
            self.libros_numero = cantidad

        elif titulo == "Usuarios registrados":
            self.usuarios_numero = cantidad

        elif titulo == "Préstamos activos":
            self.prestamos_numero = cantidad

        elif titulo == "Pendientes":
            self.pendientes_numero = cantidad

        layout.addLayout(fila_superior)
        layout.addStretch()
        layout.addWidget(cantidad)

        return tarjeta
      #se actualizan los datos en el panel 
    def actualizar_datos(self):

        conexion = None
        cursor = None

        try:
            conexion = conectar()
            cursor = conexion.cursor()

            
            cursor.execute(
                "SELECT COUNT(*) FROM libros"
            )

            total_libros = cursor.fetchone()[0]
            self.libros_numero.setText(str(total_libros))

            
            cursor.execute(
                "SELECT COUNT(*) FROM usuarios"
            )

            total_usuarios = cursor.fetchone()[0]
            self.usuarios_numero.setText(str(total_usuarios))

           
            cursor.execute("""
                SELECT COUNT(*)
                FROM prestamos
                WHERE estado = 'Prestado'
            """)

            total_prestamos = cursor.fetchone()[0]
            self.prestamos_numero.setText(
                str(total_prestamos)
            )

            # PRÉSTAMOS VENCIDOS
            cursor.execute("""
                SELECT COUNT(*)
                FROM prestamos
                WHERE estado = 'Prestado'
                  AND fecha_devolucion < CURDATE()
            """)

            total_pendientes = cursor.fetchone()[0]
            self.pendientes_numero.setText(
                str(total_pendientes)
            )

            # se registran ultimo 5 libros
            cursor.execute("""
                SELECT codigo, titulo, categoria, estado
                FROM libros
                ORDER BY id DESC
                LIMIT 5
            """)

            datos = cursor.fetchall()
            self.tabla_libros.setRowCount(0)

            for fila, registro in enumerate(datos):
                self.tabla_libros.insertRow(fila)

                for columna, valor in enumerate(registro):
                    texto = (
                        "" if valor is None
                        else str(valor)
                    )

                    self.tabla_libros.setItem(
                        fila,
                        columna,
                        QTableWidgetItem(texto)
                    )

        except Exception as error:
            print(
                "Error al actualizar el panel:",
                error
            )

        finally:
            if cursor:
                cursor.close()

            if conexion:
                conexion.close()

    
    def configurar_rol(self, rol):

        self.rol = rol

        if rol == "administrador":
            self.gestion_cuentas.show()
        else:
            self.gestion_cuentas.hide()

   
    def abrir_gestion_cuentas(self):

        if self.rol == "administrador":
            self.abrir_cuentas()