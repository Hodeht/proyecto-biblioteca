Estilos = '''
QMainWindow {
    background-color: #F4F1EA;
}

QStackedWidget {
    background-color: #F4F1EA;
}

QWidget {
    background-color: #F4F1EA;
    color: #332C27;
    font-family: "Segoe UI";
    font-size: 14px;
}


/* LOGIN */

#loginCard {
    background-color: #FFFDF8;
    border: 1px solid #D8CDBD;
    border-radius: 16px;
}

#loginTitle {
    background-color: transparent;
    color: #234B4A;
    font-size: 30px;
    font-weight: bold;
}

#loginSub {
    background-color: transparent;
    color: #756B61;
    font-size: 15px;
}


/* MENU */

#menu {
    background-color: #234B4A;
    border: none;
}

#logo {
    background-color: transparent;
    color: #F5D98B;
    font-size: 19px;
    font-weight: bold;
}

#menuSub {
    background-color: transparent;
    color: #D8E4DF;
    font-size: 12px;
}

#menuButton {
    background-color: #2B5654;
    color: white;
    border: none;
    border-radius: 8px;
    text-align: left;
    padding: 11px 13px;
}

#menuButton:hover {
    background-color: #31615F;
}

#menuButton:pressed {
    background-color: #1A3938;
}

#menuButtonActivo {
    background-color: #31615F;
    color: white;
    border: none;
    border-left: 3px solid #F5D98B;
    border-radius: 8px;
    text-align: left;
    padding: 11px 13px 11px 10px;
    font-weight: bold;
}


/* TITULOS */

#tituloPagina {
    background-color: transparent;
    color: #234B4A;
    font-size: 28px;
    font-weight: bold;
}

#descripcion {
    background-color: transparent;
    color: #756B61;
}


/* TARJETAS */


#tarjeta {
    background-color: white;
    border: 1px solid #D8CDBD;
    border-radius: 12px;
}

#tarjetaTitulo {
    background-color: transparent;
    color: #756B61;
}

#tarjetaNumero {
    background-color: transparent;
    color: #A06A32;
    font-size: 28px;
    font-weight: bold;
}


QLabel {
    background-color: transparent;
    border: none;
    color: #332C27;
}


/* TARJETAS SIN SOMBRAS */

QFrame#tarjeta {
    background-color: #FFFDF8;
    border: 1px solid #D8CDBD;
    border-radius: 12px;
}

QLabel#tarjetaTitulo {
    background-color: transparent;
    color: #756B61;
    border: none;
}

QLabel#tarjetaNumero {
    background-color: transparent;
    color: #A06A32;
    border: none;
    font-size: 28px;
    font-weight: bold;
}

/* CAMPOS */

QLineEdit {
    background-color: white;
    color: #332C27;
    border: 1px solid #CFC4B5;
    border-radius: 8px;
    padding: 10px;
}

QLineEdit:focus {
 background-color: white;
    border: 1px solid #B8894A;
}


/*COMBOBOX */

QComboBox {
    background-color: white;
    color: #332C27;
    border: 1px solid #CFC4B5;
    border-radius: 8px;
    padding: 10px;
}
QComboBox:hover {
    border: 1px solid #B8894A;
}
QComboBox:focus {
    border: 2px solid #B8894A;
}
QComboBox QAbstractItemView {
    background-color: #FFFDF8;
    color: #332C27;
    border: 1px solid #CFC4B5;
}
QCombobox QAbstractItemView::item:selected:active
 {
    background-color: #A06A32;
    color: White;
}
QComboBox QAbstractItemView::item:selected:!active 
{
    background-color: #A06A32;
    color: White;
}

QComboBox QAbstractItemView::item:hover {
    background-color: #B8894A;
    color:white;
}

/* BOTON PRINCIPAL */

#btnPrincipal {
    background-color: #A06A32;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: bold;
}

#btnSecundario {
    background-color: #A06A32;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: bold;
}

#btnPrincipal:hover {
    background-color: #B77B3E;
}

#btnPrincipal:pressed {
    background-color: #805225;
}


/* TABLA */

QTableWidget {
    background-color: #FFFDF8;
    color: #332C27;
    border: 1px solid #D8CDBD;
    border-radius: 10px;
    gridline-color: #E5DED5;
}

QTableWidget::item {
    background-color: #FFFDF8;
    color: #332C27;
}

QTableWidget::item:selected {
    background-color: #E7EFEC;
    color: #234B4A;
}

QHeaderView::section {
    background-color: #234B4A;
    color: white;
    padding: 10px;
    border: none;
    font-weight: bold;
}


/* MENSAJES */

QMessageBox {
    background-color: #FFFDF8;
}

QMessageBox QLabel {
    background-color: transparent;
    color: #332C27;
}

QMessageBox QPushButton {
    background-color: #234B4A;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
}

QMessageBox QPushButton:hover {
    background-color: #31615F;
}


/* CHECKBOX */

QCheckBox {
    background-color: transparent;
    color: #332C27;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
}

QCheckBox::indicator:unchecked {
    background-color: white;
    border: 1px solid #CFC4B5;
    border-radius: 3px;
}

QCheckBox::indicator:checked {
    background-color: #A06A32;
    border: 1px solid #A06A32;
    border-radius: 3px;
}


/* SCROLLBAR */

QScrollBar:vertical {
    background-color: #E8E1D8;
    width: 10px;
}

QScrollBar::handle:vertical {
    background-color: #B8894A;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #A06A32;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    background: none;
    border: none;
}
QPushButton#btnAccion {
    background-color: #8B5E3C;
    color: #FFFFFF;
    border: 1px solid #8B5E3C;
    border-radius: 6px;
    padding: 6px 10px;
    font-weight: bold;
}

QPushButton#btnAccion:hover {
    background-color: #A06A32;

}

QPushButton#btnAccion:pressed {
    background-color: #70472E;

}


/* LOGIN */

#pantallaLogin {
    background-color: #F4F1EA;
}

#loginCard {
    background-color: #FFFDF8;
    border: 1px solid #D8CDBD;
    border-radius: 20px;
}

#loginIcon {
    background-color: transparent;
    padding: 8px;
}

#loginTitle {
    background-color: transparent;
    color: #234B4A;
    font-family: "Segoe UI";
    font-size: 30px;
    font-weight: bold;
}

#loginSub {
    background-color: transparent;
    color: #756B61;
    font-size: 14px;
}

#loginAviso {
    background-color: transparent;
    color: #756B61;
    font-size: 11px;
}


/* CAMPOS DEL LOGIN */

QLineEdit#loginInput {
    background-color: #FFFFFF;
    color: #332C27;
    border: 1px solid #CFC4B5;
    border-radius: 10px;
    padding: 0px 13px;
    font-size: 14px;
    selection-background-color: #234B4A;
    selection-color: #FFFFFF;
}

QLineEdit#loginInput:hover {
    border: 1px solid #B8894A;
}

QLineEdit#loginInput:focus {
    background-color: #FFFFFF;
    border: 2px solid #234B4A;
}


/* BOTÓN PRINCIPAL */

QPushButton#btnPrincipal {
    background-color: #8B5E3C;
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    padding: 10px 20px;
    font-size: 15px;
    font-weight: bold;
}

QPushButton#btnPrincipal:hover {
    background-color: #A06A32;
}

QPushButton#btnPrincipal:pressed {
    background-color: #70472E;
}

QPushButton#btnPrincipal:disabled {
    background-color: #CFC4B5;
    color: #756B61;

}




# ESTADO FÍSICO DE LOS LIBROS

QFrame#tarjetaEstado {
    background-color: #FFFDF8;
    border: 1px solid #D8CDBD;
    border-radius: 12px;
}

QLabel#tarjetaEstadoTitulo {
    background-color: transparent;
    color: #756B61;
    font-size: 13px;
}

QLabel#tarjetaEstadoNumero {
    background-color: transparent;
    color: #A06A32;
    font-size: 28px;
    font-weight: bold;
}

QFrame#formularioEstado {
    background-color: #FFFDF8;
    border: 1px solid #D8CDBD;
    border-radius: 12px;
}

QLabel#seccionEstado {
    background-color: transparent;
    color: #234B4A;
    font-size: 17px;
    font-weight: bold;
}
'''