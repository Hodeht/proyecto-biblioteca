import sys
import os


from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QStackedWidget,

)

from recursos.estilos import Estilos
from vistas.login import InicioSesion
from vistas.panel import PanelPrincipal
from modulos.registros import Registros
from modulos.prestamos import Prestamos
from modulos.usuarios import Usuarios
from modulos.cuentas import Cuentas

from reportes.alertas import (
    MenuAlertas,
    AlertasDevolucion,
    EstadoFisicoLibros
)

from reportes.estadisticas import EstadisticasPrestamos


class BibliotecaLeon(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "Sistema de Gestión Bibliotecaria - León"
        )

        self.resize(1150, 700)
        self.setMinimumSize(900, 600)

        self.rol_actual = None

        
        self.paginas = QStackedWidget()
        self.setCentralWidget(self.paginas)

        
        self.pagina_login = InicioSesion(
            self.mostrar_panel
        )

        
        self.pagina_panel = PanelPrincipal(
            self.mostrar_registros,
            self.mostrar_prestamos,
            self.mostrar_usuarios,
            self.cerrar_sesion,
            self.mostrar_cuentas,
            self.mostrar_alertas
        )

       
        self.pagina_registros = Registros(
            self.mostrar_panel_sin_rol
        )

        
        self.pagina_prestamos = Prestamos(
            self.mostrar_panel_sin_rol
        )

       
        self.pagina_usuarios = Usuarios(
            self.mostrar_panel_sin_rol
        )

       
        self.pagina_cuentas = Cuentas(
            self.mostrar_panel_sin_rol
        )

        
        self.pagina_alertas = AlertasDevolucion(
            self.mostrar_menu_alertas
        )

        
        self.pagina_estado_fisico = EstadoFisicoLibros(
            self.mostrar_menu_alertas
        )

       
        self.pagina_estadisticas = EstadisticasPrestamos(
            self.mostrar_menu_alertas
        )

        
        self.pagina_menu_alertas = MenuAlertas(
            self.abrir_alertas_devolucion,
            self.mostrar_estado_fisico,
            self.mostrar_estadisticas_prestamos,
            self.mostrar_panel_sin_rol
        )

        self.paginas.addWidget(self.pagina_login)
        self.paginas.addWidget(self.pagina_panel)
        self.paginas.addWidget(self.pagina_registros)
        self.paginas.addWidget(self.pagina_prestamos)
        self.paginas.addWidget(self.pagina_usuarios)
        self.paginas.addWidget(self.pagina_cuentas)
        self.paginas.addWidget(self.pagina_menu_alertas)
        self.paginas.addWidget(self.pagina_alertas)
        self.paginas.addWidget(self.pagina_estado_fisico)
        self.paginas.addWidget(self.pagina_estadisticas)

       
        self.paginas.setCurrentWidget(
            self.pagina_login
        )

    def mostrar_panel(self, rol):
        if rol is not None:
            self.rol_actual = rol

        self.pagina_panel.configurar_rol(
            self.rol_actual
        )

        self.pagina_panel.actualizar_datos()

        self.paginas.setCurrentWidget(
            self.pagina_panel
        )

    def mostrar_cuentas(self):
        if self.rol_actual != "administrador":
            return

        self.paginas.setCurrentWidget(
            self.pagina_cuentas
        )

    
    def mostrar_panel_sin_rol(self):
        self.pagina_panel.configurar_rol(
            self.rol_actual
        )

        self.pagina_panel.actualizar_datos()

        self.paginas.setCurrentWidget(
            self.pagina_panel
        )

   
    def mostrar_registros(self):
        self.paginas.setCurrentWidget(
            self.pagina_registros
        )

    # MOSTRAR PRÉSTAMOS
    def mostrar_prestamos(self):
        self.paginas.setCurrentWidget(
            self.pagina_prestamos
        )

    def mostrar_usuarios(self):
        self.paginas.setCurrentWidget(
            self.pagina_usuarios
        )

    
    def mostrar_alertas(self):
        self.paginas.setCurrentWidget(
            self.pagina_menu_alertas
        )

   
    def abrir_alertas_devolucion(self):
        self.pagina_alertas.cargar_alertas()

        self.paginas.setCurrentWidget(
            self.pagina_alertas
        )

   
    def mostrar_menu_alertas(self):
        self.paginas.setCurrentWidget(
            self.pagina_menu_alertas
        )

    
    def mostrar_estado_fisico(self):
        self.pagina_estado_fisico.cargar_libros()
        self.pagina_estado_fisico.cargar_datos()

        self.paginas.setCurrentWidget(
            self.pagina_estado_fisico
        )

   
    def mostrar_estadisticas_prestamos(self):
        self.pagina_estadisticas.cargar_estadisticas()

        self.paginas.setCurrentWidget(
            self.pagina_estadisticas
        )

    
    def cerrar_sesion(self):
        self.rol_actual = None

        self.pagina_panel.configurar_rol(None)

        self.pagina_login.clave.clear()
        self.pagina_login.usuario.clear()

        self.paginas.setCurrentWidget(
            self.pagina_login
        )


if __name__ == "__main__":

    app = QApplication(sys.argv)
    app.setStyleSheet(Estilos)

    ventana = BibliotecaLeon()
    ventana.show()

    sys.exit(app.exec())