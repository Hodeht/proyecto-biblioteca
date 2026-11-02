from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QFrame,
    QMessageBox,
    QComboBox,
    QFormLayout,
    QHeaderView,
    QMenu,
    QSpinBox,
    QScrollArea
)


from base_datos.conexion_orm import obtener_sesion
from modelos.libro import Libro
from sqlalchemy.exc import IntegrityError


class Registros(QWidget):

    def __init__(self, volver):
        super().__init__()

        self.volver = volver
        self.fila_editando = None

       
        # SCROLL PRINCIPAL
        

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        contenido = QWidget()
        scroll.setWidget(contenido)

        principal = QVBoxLayout(contenido)
        principal.setContentsMargins(30, 25, 30, 25)
        principal.setSpacing(10)

        ventana = QVBoxLayout(self)
        ventana.setContentsMargins(0, 0, 0, 0)
        ventana.addWidget(scroll)

        
        # ENCABEZADO
       

        encabezado = QHBoxLayout()
        textos = QVBoxLayout()

        titulo = QLabel("Administración de registros")
        titulo.setObjectName("tituloPagina")

        descripcion = QLabel(
            "Agregue, consulte y administre los libros de la biblioteca."
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

        formulario = QFormLayout(formulario_frame)
        formulario.setContentsMargins(20, 15, 20, 15)
        formulario.setSpacing(10)

        # Código

        self.codigo = QLineEdit()
        self.codigo.setReadOnly(True)
        self.codigo.setPlaceholderText("Código automático")

        # Título

        self.titulo_libro = QLineEdit()
        self.titulo_libro.setPlaceholderText("Título del libro")

        # Autor

        self.autor = QLineEdit()
        self.autor.setPlaceholderText("Autor del libro")

        
        # CATEGORÍA
     

        self.categoria = QComboBox()

        self.categoria.addItems([
            "Literatura",
            "Historia",
            "Tecnología",
            "Ciencias",
            "Educación",
            "Ciencias Sociales",
            "Geografía y Turismo",
            "Filosofía y Psicología",
            "Medicina y Salud",
            "Infantil"
        ])

        # SECCIÓN
     

        self.seccion = QComboBox()

       
        # AÑO
        

        self.anio = QSpinBox()
        self.anio.setRange(1000, 2100)
        self.anio.setValue(2026)

       
        # EDICIÓN
    

        self.edicion = QLineEdit()
        self.edicion.setPlaceholderText(
            "Ejemplo: Primera edición"
        )

      
        # ESTADO
       

        self.estado = QComboBox()

        self.estado.addItems([
            "Disponible",
            "Prestado",
            "En mantenimiento"
        ])

       
        estilo_combo = """
            QComboBox {
                background-color: white;
                color: #332C27;
            }

            QComboBox QAbstractItemView {
                background-color: #FFFDF8;
                color: #332C27;
            }

            QComboBox QAbstractItemView::item:selected {
                background-color: #8B5E3C;
                color: white;
            }
        """

        self.categoria.setStyleSheet(estilo_combo)
        self.seccion.setStyleSheet(estilo_combo)
        self.estado.setStyleSheet(estilo_combo)

        self.categoria.currentTextChanged.connect(
            self.actualizar_secciones
        )

     
        # CAMPOS DEL FORMULARIO
      

        etiquetas = [
            "Código:",
            "Título:",
            "Autor:",
            "Categoría:",
            "Sección:",
            "Año:",
            "Edición:",
            "Estado:"
        ]

        widgets = [
            self.codigo,
            self.titulo_libro,
            self.autor,
            self.categoria,
            self.seccion,
            self.anio,
            self.edicion,
            self.estado
        ]

        for texto, widget in zip(etiquetas, widgets):

            etiqueta = QLabel(texto)

            etiqueta.setStyleSheet(
                "background-color: transparent;"
            )

            formulario.addRow(
                etiqueta,
                widget
            )

        principal.addWidget(formulario_frame)

       
        
        botones = QHBoxLayout()

        self.guardar = QPushButton("Guardar registro")
        self.guardar.setObjectName("btnPrincipal")
        self.guardar.clicked.connect(
            self.guardar_registro
        )

        limpiar = QPushButton("Limpiar")
        limpiar.setObjectName("btnSecundario")
        limpiar.clicked.connect(
            self.limpiar
        )

        botones.addWidget(self.guardar)
        botones.addWidget(limpiar)
        botones.addStretch()

        principal.addLayout(botones)

      

        busqueda = QHBoxLayout()

        self.buscar = QLineEdit()

        self.buscar.setPlaceholderText(
            "Buscar por código, título o autor..."
        )

        self.buscar.textChanged.connect(
            self.filtrar
        )

        busqueda.addWidget(self.buscar)

        principal.addLayout(busqueda)

        

        self.tabla = QTableWidget(0, 11)

        self.tabla.setHorizontalHeaderLabels([
            "Código",
            "Título",
            "Autor",
            "Categoría",
            "Sección",
            "Año",
            "Pasillo",
            "Estante",
            "Repisa",
            "Estado",
            "Acciones"
        ])

        self.tabla.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.tabla.setColumnWidth(10, 100)

        self.tabla.horizontalHeader().setSectionResizeMode(
            10,
            QHeaderView.Fixed
        )

        self.tabla.verticalHeader().setVisible(False)

        self.tabla.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.tabla.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.tabla.setMinimumHeight(450)

        principal.addWidget(self.tabla)

      

        self.actualizar_secciones()
        self.cargar_registros()
        self.generar_codigo()

    # ==================================================
    # SECCIONES
    # ==================================================

    def actualizar_secciones(self):

        categoria = self.categoria.currentText()

        secciones = {

            "Literatura": [
                "Novela",
                "Poesía",
                "Cuentos",
                "Teatro",
                "Literatura nicaragüense",
                "Fantasía",
                "Ciencia ficción"
            ],

            "Historia": [
                "Historia de Nicaragua",
                "Historia de América",
                "Historia Universal",
                "Historia Antigua",
                "Historia Contemporánea"
            ],

            "Tecnología": [
                "Programación",
                "Bases de datos",
                "Redes",
                "Sistemas",
                "Informática",
                "Inteligencia Artificial"
            ],

            "Ciencias": [
                "Matemáticas",
                "Física",
                "Química",
                "Biología",
                "Ciencias Naturales"
            ],

            "Educación": [
                "Pedagogía",
                "Didáctica",
                "Educación Infantil",
                "Educación Especial",
                "Métodos de Enseñanza"
            ],

            "Ciencias Sociales": [
                "Sociología",
                "Economía",
                "Derecho",
                "Política",
                "Antropología"
            ],

            "Geografía y Turismo": [
                "Geografía",
                "Turismo",
                "Cultura",
                "Patrimonio",
                "Viajes y destinos"
            ],

            "Filosofía y Psicología": [
                "Filosofía",
                "Psicología",
                "Ética",
                "Pensamiento humano",
                "Desarrollo personal"
            ],

            "Medicina y Salud": [
                "Medicina general",
                "Enfermería",
                "Anatomía",
                "Salud pública",
                "Nutrición"
            ],

            "Infantil": [
                "Cuentos infantiles",
                "Libros educativos",
                "Aventuras",
                "Fábulas",
                "Actividades infantiles"
            ]
        }

        self.seccion.clear()

        self.seccion.addItems(
            secciones.get(categoria, [])
        )

    # ==================================================
    # UBICACIÓN AUTOMÁTICA
    # ==================================================

    def obtener_ubicacion(
        self,
        categoria,
        seccion,
        autor
    ):

        pasillos = {

            "Literatura": "Pasillo 1",
            "Historia": "Pasillo 2",
            "Tecnología": "Pasillo 3",
            "Ciencias": "Pasillo 4",
            "Educación": "Pasillo 5",
            "Ciencias Sociales": "Pasillo 6",
            "Geografía y Turismo": "Pasillo 7",
            "Filosofía y Psicología": "Pasillo 8",
            "Medicina y Salud": "Pasillo 9",
            "Infantil": "Pasillo 10"
        }

        estantes = {

            "Novela": "Estante 1",
            "Poesía": "Estante 2",
            "Cuentos": "Estante 3",
            "Teatro": "Estante 4",
            "Literatura nicaragüense": "Estante 5",
            "Fantasía": "Estante 6",
            "Ciencia ficción": "Estante 7",
            

            "Historia de Nicaragua": "Estante 1",
            "Historia de América": "Estante 2",
            "Historia Universal": "Estante 3",
            "Historia Antigua": "Estante 4",
            "Historia Contemporánea": "Estante 5",

            "Programación": "Estante 1",
            "Bases de datos": "Estante 2",
            "Redes": "Estante 3",
            "Sistemas": "Estante 4",
            "Informática": "Estante 5",
            "Inteligencia Artificial": "Estante 6",

            "Matemáticas": "Estante 1",
            "Física": "Estante 2",
            "Química": "Estante 3",
            "Biología": "Estante 4",
            "Ciencias Naturales": "Estante 5",

            "Pedagogía": "Estante 1",
            "Didáctica": "Estante 2",
            "Educación Infantil": "Estante 3",
            "Educación Especial": "Estante 4",
            "Métodos de Enseñanza": "Estante 5",

            "Sociología": "Estante 1",
            "Economía": "Estante 2",
            "Derecho": "Estante 3",
            "Política": "Estante 4",
            "Antropología": "Estante 5",

            "Geografía": "Estante 1",
            "Turismo": "Estante 2",
            "Cultura": "Estante 3",
            "Patrimonio": "Estante 4",
            "Viajes y destinos": "Estante 5",

            "Filosofía": "Estante 1",
            "Psicología": "Estante 2",
            "Ética": "Estante 3",
            "Pensamiento humano": "Estante 4",
            "Desarrollo personal": "Estante 5",

            "Medicina general": "Estante 1",
            "Enfermería": "Estante 2",
            "Anatomía": "Estante 3",
            "Salud pública": "Estante 4",
            "Nutrición": "Estante 5",

            "Cuentos infantiles": "Estante 1",
            "Libros educativos": "Estante 2",
            "Aventuras": "Estante 3",
            "Fábulas": "Estante 4",
            "Actividades infantiles": "Estante 5"
        }

        autor = autor.strip()

        if autor:
            letra = autor[0].upper()
        else:
            letra = "A"

        if letra in "ABCDE":
            repisa = "Repisa 1"

        elif letra in "FGHIJ":
            repisa = "Repisa 2"

        elif letra in "KLMNO":
            repisa = "Repisa 3"

        elif letra in "PQRST":
            repisa = "Repisa 4"

        else:
            repisa = "Repisa 5"

        pasillo = pasillos.get(
            categoria,
            "Pasillo 1"
        )

        estante = estantes.get(
            seccion,
            "Estante 1"
        )

        return pasillo, estante, repisa

   
   # ==================================================
    # GENERAR CÓDIGO AUTOMÁTICO MEDIANTE ORM
    # ==================================================

    def generar_codigo(self):

        sesion = obtener_sesion()

        try:

            registros = sesion.query(Libro.codigo).all()

            mayor = -1

            for registro in registros:

                codigo = str(registro[0])

                if codigo.startswith("B-"):

                    try:
                        numero = int(codigo.split("-")[1])

                        if numero > mayor:
                            mayor = numero

                    except ValueError:
                        pass

            siguiente = mayor + 1

            self.codigo.setText(
                f"B-{siguiente:03d}"
            )

        except Exception:

            self.codigo.setText("B-000")

        finally:
            sesion.close()
    

   
        


   # ==================================================
    # CARGAR REGISTROS MEDIANTE ORM
    # ==================================================

    def cargar_registros(self):

        sesion = obtener_sesion()

        try:

            registros = sesion.query(Libro).order_by(
                Libro.codigo
            ).all()

            self.tabla.setRowCount(0)

            for libro in registros:

                datos = (
                    libro.codigo,
                    libro.titulo,
                    libro.autor,
                    libro.categoria,
                    libro.seccion,
                    libro.anio,
                    libro.pasillo,
                    libro.estante,
                    libro.repisa,
                    libro.estado
                )

                self.agregar(datos)

        except Exception as error:

            QMessageBox.warning(
                self,
                "Aviso",
                f"No se pudieron cargar los registros:\n\n{error}"
            )

        finally:
            sesion.close()

               

    # ==================================================
    # AGREGAR FILA
    # ==================================================

    def agregar(self, datos):

        fila = self.tabla.rowCount()

        self.tabla.insertRow(fila)

        for columna, valor in enumerate(datos):

            self.tabla.setItem(
                fila,
                columna,
                QTableWidgetItem(
                    str(valor)
                )
            )

        contenedor = QWidget()

        contenedor.setStyleSheet("""
            QWidget {
                background-color: white;
                border: none;
            }
        """)

        botones = QHBoxLayout(contenedor)

        botones.setContentsMargins(
            0,
            0,
            0,
            0
        )

        botones.setAlignment(
            Qt.AlignCenter
        )

        boton_menu = QPushButton("⋮")

        boton_menu.setFixedSize(
            40,
            30
        )

        boton_menu.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: none;
                font-size: 24px;
                font-weight: bold;
                color: #8B5E3C;
                padding: 0px;
            }

            QPushButton:hover {
                background-color: #F5EFEA;
            }
        """)

        boton_menu.clicked.connect(
            lambda checked=False,
            fila=fila:
            self.mostrar_menu_acciones(
                fila,
                boton_menu
            )
        )

        botones.addWidget(
            boton_menu
        )

        self.tabla.setCellWidget(
            fila,
            10,
            contenedor
        )

    

    def mostrar_menu_acciones(
        self,
        fila,
        boton
    ):

        if fila < 0:
            return

        menu = QMenu(self)

        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                color: #332C27;
                border: 1px solid #E0E0E0;
                padding: 5px;
            }

            QMenu::item {
                background-color: white;
                padding: 9px 25px;
            }

            QMenu::item:selected {
                background-color: #F0E6DD;
            }
        """)

        editar = menu.addAction("Editar")

        eliminar = menu.addAction("Eliminar")

        accion = menu.exec(
            boton.mapToGlobal(
                boton.rect().bottomRight()
            )
        )

        if accion == editar:

            self.editar_registro(
                fila
            )

        elif accion == eliminar:

            self.eliminar_registro(
                fila
            )

   
   # ==================================================
    # GUARDAR Y ACTUALIZAR REGISTROS MEDIANTE ORM
    # ==================================================

    def guardar_registro(self):

        titulo = self.titulo_libro.text().strip()
        autor = self.autor.text().strip()

        if not titulo:

            QMessageBox.warning(
                self,
                "Información",
                "Ingrese el título del libro."
            )

            self.titulo_libro.setFocus()
            return

        if not autor:

            QMessageBox.warning(
                self,
                "Información",
                "Ingrese el autor del libro."
            )

            self.autor.setFocus()
            return

        codigo = self.codigo.text().strip()
        categoria = self.categoria.currentText()
        seccion = self.seccion.currentText()
        anio = self.anio.value()
        edicion = self.edicion.text().strip()
        estado = self.estado.currentText()

        pasillo, estante, repisa = self.obtener_ubicacion(
            categoria,
            seccion,
            autor
        )

        sesion = obtener_sesion()

        try:

            # ACTUALIZAR LIBRO EXISTENTE

            if self.fila_editando is not None:

                fila = self.fila_editando

                codigo_anterior = self.tabla.item(
                    fila,
                    0
                ).text()

                libro = sesion.query(Libro).filter_by(
                    codigo=codigo_anterior
                ).first()

                if libro is None:

                    QMessageBox.warning(
                        self,
                        "Aviso",
                        "No se encontró el libro que desea actualizar."
                    )

                    return

                libro.titulo = titulo
                libro.autor = autor
                libro.categoria = categoria
                libro.anio = anio
                libro.edicion = edicion
                libro.seccion = seccion
                libro.pasillo = pasillo
                libro.estante = estante
                libro.repisa = repisa
                libro.estado = estado

                sesion.commit()

                valores = [
                    codigo_anterior,
                    titulo,
                    autor,
                    categoria,
                    seccion,
                    anio,
                    pasillo,
                    estante,
                    repisa,
                    estado
                ]

                for columna, valor in enumerate(valores):

                    self.tabla.setItem(
                        fila,
                        columna,
                        QTableWidgetItem(str(valor))
                    )

                QMessageBox.information(
                    self,
                    "Registro actualizado",
                    "El libro fue actualizado correctamente."
                )

            # REGISTRAR LIBRO NUEVO

            else:

                nuevo_libro = Libro(
                    codigo=codigo,
                    titulo=titulo,
                    autor=autor,
                    categoria=categoria,
                    anio=anio,
                    edicion=edicion,
                    seccion=seccion,
                    pasillo=pasillo,
                    estante=estante,
                    repisa=repisa,
                    estado=estado
                )

                sesion.add(nuevo_libro)
                sesion.commit()

                valores = [
                    codigo,
                    titulo,
                    autor,
                    categoria,
                    seccion,
                    anio,
                    pasillo,
                    estante,
                    repisa,
                    estado
                ]

                self.agregar(valores)

                QMessageBox.information(
                    self,
                    "Registro guardado",
                    "El libro fue registrado correctamente."
                )

            self.limpiar()

        except IntegrityError:

            sesion.rollback()

            QMessageBox.warning(
                self,
                "Registro duplicado",
                "No se pudo guardar el libro.\n\n"
                "Es posible que el código ya exista."
            )

        except Exception as error:

            sesion.rollback()

            QMessageBox.critical(
                self,
                "Error",
                f"Ocurrió un error:\n\n{error}"
            )

        finally:
            sesion.close()

           

    def limpiar(self):

        self.titulo_libro.clear()
        self.autor.clear()
        self.edicion.clear()

        self.categoria.setCurrentIndex(0)

        self.actualizar_secciones()

        self.estado.setCurrentIndex(0)

        self.fila_editando = None

        self.guardar.setText(
            "Guardar registro"
        )

        self.generar_codigo()

    # ==================================================
    # BUSCAR
    # ==================================================

    def filtrar(self, texto):

        texto = texto.lower().strip()

        for fila in range(
            self.tabla.rowCount()
        ):

            codigo = self.tabla.item(
                fila,
                0
            )

            titulo = self.tabla.item(
                fila,
                1
            )

            autor = self.tabla.item(
                fila,
                2
            )

            encontrado = False

            for item in [
                codigo,
                titulo,
                autor
            ]:

                if item:

                    if texto in item.text().lower():

                        encontrado = True
                        break

            self.tabla.setRowHidden(
                fila,
                not encontrado
            )

  

    # ELIMINAR REGISTRO MEDIANTE ORM
   

    # ELIMINAR REGISTRO MEDIANTE ORM

def eliminar_registro(self, fila):

    if fila < 0:
        return

    item_codigo = self.tabla.item(fila, 0)

    if not item_codigo:
        return

    codigo = item_codigo.text()

    titulo = self.tabla.item(fila, 1)

    nombre_libro = ""

    if titulo:
        nombre_libro = titulo.text()

    respuesta = QMessageBox.question(
        self,
        "Eliminar registro",
        f"¿Está seguro de que desea eliminar el libro\n"
        f"'{nombre_libro}'?",
        QMessageBox.Yes |
        QMessageBox.No,
        QMessageBox.No
    )

    if respuesta != QMessageBox.Yes:
        return

    sesion = obtener_sesion()

    try:

        # BUSCAR EL LIBRO
        libro = sesion.query(Libro).filter_by(
            codigo=codigo
        ).first()

        if libro is None:

            QMessageBox.warning(
                self,
                "Aviso",
                "No se encontró el libro que desea eliminar."
            )

            return

        # COMPROBAR SI EL LIBRO TIENE PRÉSTAMOS
        from modelos.prestamo import Prestamo

        cantidad_prestamos = sesion.query(Prestamo).filter_by(
            codigo_libro=codigo
        ).count()

        if cantidad_prestamos > 0:

            QMessageBox.warning(
                self,
                "No se puede eliminar",
                "Este libro tiene préstamos registrados.\n\n"
                "No se eliminó para proteger el historial de préstamos."
            )

            return

        # ELIMINAR LIBRO
        sesion.delete(libro)
        sesion.commit()

        self.tabla.removeRow(fila)

        QMessageBox.information(
            self,
            "Registro eliminado",
            "El libro se eliminó correctamente."
        )

        self.generar_codigo()

    except Exception as error:

        sesion.rollback()

        QMessageBox.critical(
            self,
            "Error",
            f"No se pudo eliminar el libro:\n\n{error}"
        )

    finally:
        sesion.close()

       

    # ==================================================
    # EDITAR
    # ==================================================

    def editar_registro(self, fila):

        if fila < 0:
            return

        self.fila_editando = fila

        codigo = self.tabla.item(
            fila,
            0
        ).text()

        titulo = self.tabla.item(
            fila,
            1
        ).text()

        autor = self.tabla.item(
            fila,
            2
        ).text()

        categoria = self.tabla.item(
            fila,
            3
        ).text()

        seccion = self.tabla.item(
            fila,
            4
        ).text()

        anio = self.tabla.item(
            fila,
            5
        ).text()

        estado = self.tabla.item(
            fila,
            9
        ).text()

        self.codigo.setText(
            codigo
        )

        self.titulo_libro.setText(
            titulo
        )

        self.autor.setText(
            autor
        )

        self.categoria.setCurrentText(
            categoria
        )

        self.seccion.setCurrentText(
            seccion
        )

        try:

            self.anio.setValue(
                int(anio)
            )

        except ValueError:

            self.anio.setValue(
                2026
            )

        self.estado.setCurrentText(
            estado
        )

      

       # OBTENER EDICIÓN MEDIANTE ORM

        sesion = obtener_sesion()

        try:

            libro = sesion.query(Libro).filter_by(
                codigo=codigo
            ).first()

            if libro and libro.edicion:

                self.edicion.setText(
                    str(libro.edicion)
                )

            else:

                self.edicion.clear()

        except Exception:

            self.edicion.clear()

        finally:

            sesion.close()

   

        self.guardar.setText(
            "Actualizar registro"
        )

        self.titulo_libro.setFocus()