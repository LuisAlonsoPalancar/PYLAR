"""
----------------------------------
Nombre del archivo:     control_Satelites.py
Descripción:            Este script controla la ventana de satélites de la aplicación, 
                        gestionando la interacción con los pases de satélites,
                        bien sea subiéndolos, reprocesándolos o eliminándolos

Entrada(s):             Lista de sesiones seleccionadas y fecha de la sesión.
Salida(s):              Muestra la ventana de satélites de la aplicación.
Dependencias:           PyQt6 (V 6.4.2), paramiko (V 3.5.1)
Autor:                  Luis Alonso Palancar
Fecha:                  Julio 2025
----------------------------------
"""
import os
import csv
import re
import paramiko
import json
import configparser
import sys

from PyQt6.QtWidgets import QWidget, QTableWidgetItem, QCheckBox, QHeaderView, QMessageBox, QProgressDialog
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor

from scripts.ClickableLabel import ClickableLabel # Clase para ampliar imagen de grafica
from scripts.control_Sesiones import SesionesWindow as Ventana_lista_sesiones  # Control de sesiones
from vistas.Window_Satelites_ui import Ui_Form  # Ventana de Satélites

class SatelitesWindow(QWidget):
    sesiones_seleccionadas = pyqtSignal(list) # Signal que emite la lista de sesiones seleccionadas

    def __init__(self, sesiones_seleccionadas, fecha):
        super().__init__()

        self.ui = Ui_Form()  # Crear una instancia de la clase
        self.ui.setupUi(self)  # Configurar la interfaz de usuario

        # Variables de la instancia
        self.fecha_input = fecha  # Guardar la fecha recibida (QDate)
        self.datos_satelites = [] # Lista para almacenar los diccionarios de los satélites
        self.sesiones = sesiones_seleccionadas # Lista de sesiones seleccionadas entrantes
        self.fecha_str = self.fecha_input.toString("yyyyMMdd")  # Fecha en formato yyyyMMdd

        # RUTAS DE PRUEBAS LOCALES
        ruta_sesion_fecha_str = f"./Sesiones/Sessions_{self.fecha_str}" # Ruta de la sesión
        ruta_rel_session_fecha = os.path.relpath(ruta_sesion_fecha_str)  # Asegurarse de que la ruta sea absoluta
        self.ruta_sesion_fecha = os.path.dirname(os.path.dirname(__file__)) + "/" + ruta_rel_session_fecha

        # RUTA EN PC DE ESTACION
        #self.ruta_sesion_fecha = f"/opt/scope/data/export/processing/Sessions_{self.fecha_str}" # Ruta de la sesión

        # Establecer la fecha en el widget, en formato dd/MM/yyyy
        self.ui.fecha_entrada.setStyleSheet("font-size: 14pt; font-weight: 700;")
        self.ui.fecha_entrada.setText(f"Fecha: {fecha.toString('dd/MM/yyyy')}")
        
        #Cargar los datos de los satélites en la tabla
        self.cargar_datos()
        #Conectar botones con sus acciones correspondientes
        self.ui.BotonSubir.clicked.connect(self.SubirDatos)  # Conectar el botón a la función de checkboxes seleccionados
        self.ui.BotonProcMan.clicked.connect(self.ProcesadoMan)  # Conectar el botón a la función de Procesado Manual
        self.ui.BotonBorrar.clicked.connect(self.Eliminar_datos)  # Conectar el botón a la función de eliminar datos
        self.ui.BotonProcAuto.clicked.connect(self.ProcesadoAuto)  # Conectar el botón a la función de Procesado Automático
        self.ui.BotonAddSessions.clicked.connect(self.AgregarSesiones)  # Conectar el botón de añadir sesiones a la función AgregarSesiones
        self.ui.SelectAll.clicked.connect(self.seleccionar_todos)  # Conectar el checkbox de seleccionar todos a la función seleccionar_todos

    def AgregarSesiones(self):
        #OBJ: Abrir la ventana de sesiones para añadir sesiones a la lista
        #POST: Muestra la ventana de sesiones
        self.ui.tablaSatelites.clearSelection()  # Limpiar la selección de la tabla
        self.hija = Ventana_lista_sesiones(self.fecha_input, self.sesiones)  # Crear una instancia de la ventana de sesiones
        self.hija.sesiones_seleccionadas.connect(self.anadir_sesion)  # Conectar señal
        self.hija.show()
        
    def anadir_sesion(self, sesiones_nuevas):
        #OBJ: Añadir sesiones a la lista de sesiones seleccionadas
        #POST: Actualiza la lista de sesiones con las nuevas sesiones
        #IN: sesiones_nuevas(list): Lista de sesiones seleccionadas.
        self.sesiones = sesiones_nuevas
        self.sesiones_seleccionadas.emit(self.sesiones)  # Emite la señal con las sesiones seleccionadas
        self.ui.tablaSatelites.clear()  # Limpiar la tabla antes de recargar los datos
        self.cargar_datos()  # Recargar los datos de los satélites en la tabla

    def cargar_datos(self):
        #OBJ: Cargar los datos de los pases en la tabla
        #POST: Tabla de satélites se llena con los datos de los satélites

        cabeceras = [
            "","Sesión","Longitud de onda", "Nombre Satélite", "  Hora  ", "  Estado  ",
            " NP RMS (mm)  ", "  NP SD (mm)  ", "Num de NPs", "Retornos por NP", "Gráficas"
        ]
        #Las comumnas son el checkbox, el numero de sesion, la longitud de onda, el nombre del satelite,
        #la hora de cada satelite, el estado del satelite, 
        # el RMS, la SD, el numero de NPs, los retornos captados por NP y la grafica de cada uno
        
        fila = 0
        self.ui.tablaSatelites.setRowCount(fila)
        self.ui.tablaSatelites.verticalHeader().setVisible(False)
        self.ui.tablaSatelites.setColumnCount(cabeceras.__len__())  # Número de columnas
        self.ui.tablaSatelites.setHorizontalHeaderLabels(cabeceras)
        
        # Evitar que el usuario cambie el tamaño de las columnas y añade un color al fondo de las cabeceras
        header = self.ui.tablaSatelites.horizontalHeader()
        header.setSectionResizeMode(header.ResizeMode.Fixed)
        self.ui.tablaSatelites.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: lightgray; }")

        #Tamaño de las columnas proporcionales y la primera columna con ancho fijo
        self.ui.tablaSatelites.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.ui.tablaSatelites.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.ui.tablaSatelites.setColumnWidth(0, 40)  # Ancho de la columna del checkbox


        #Tamaño de las imagenes/graficas
        TAM_X = 210  # Ancho deseado de la imagen
        TAM_Y = 130   # Alto deseado de la imagen

        # Helper para crear QTableWidgetItem centrado y no editable
        def item_centrado(texto):
            item = QTableWidgetItem(str(texto))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            return item 

        #Recorre las sesiones seleccionadas y carga los datos de los satélites 
        for sesion in self.sesiones: #Sesiones seleccionadas
            #Recorre todas las sesiones leyendo los datos de los satelites
            # o bien del .csv o bien saca el nombre de los archivos .frd

            ruta_sesion = f"{self.ruta_sesion_fecha}/{sesion}" # Ruta de la sesión
            datos_sesion_satelites = self.extraer_datos_satelite(ruta_sesion) # Extrae los datos de los satélites de la sesión
            self.datos_satelites.extend(datos_sesion_satelites) # Añade los datos de los satélites a la lista de datos
            
            for datos in datos_sesion_satelites: #Pases de la sesión
                
                self.ui.tablaSatelites.insertRow(fila)
                # Añadir checkbox en la primera columna
                checkbox = QCheckBox()
                checkbox.setStyleSheet("margin-left:13px;")  # Añadir margen al checkbox
                self.ui.tablaSatelites.setCellWidget(fila, 0, checkbox)
                
                # Añadir los datos del satélite en las columnas correspondientes
                self.ui.tablaSatelites.setItem(fila, 1, item_centrado(sesion))

                #longitud de onda, si 1064.0 poner en rojo, si 532.0 poner en verde
                if datos["longitud_onda"] == str(1064.0):
                    item_longitud_onda = item_centrado(datos["longitud_onda"])
                    item_longitud_onda.setForeground(QColor("#E73D3D"))  # Letras en blanco
                elif datos["longitud_onda"] == str(532.0):
                    item_longitud_onda = item_centrado(datos["longitud_onda"])
                    item_longitud_onda.setForeground(QColor("#1DA51D"))  # Verde en hexadecimal
                else:
                    item_longitud_onda = item_centrado(datos["longitud_onda"])  # Si no es 1064.0 ni 532.0, se pone el color por defecto
                self.ui.tablaSatelites.setItem(fila, 2, item_longitud_onda)
                
                self.ui.tablaSatelites.setItem(fila, 3, item_centrado(datos["NomSat"]))
                self.ui.tablaSatelites.setItem(fila, 4, item_centrado(datos["hora"]))

                # Depende del estado, el fondo varía
                if datos["estado"].lower() == "passed." or datos["estado"].lower() == "success":
                    item_estado = item_centrado(datos["estado"])
                    item_estado.setBackground(Qt.GlobalColor.green)
                    self.ui.tablaSatelites.setItem(fila, 5, item_estado)
                elif datos["estado"].lower() == "warning":
                    item_estado = item_centrado(datos["estado"])
                    item_estado.setBackground(Qt.GlobalColor.yellow)
                    self.ui.tablaSatelites.setItem(fila, 5, item_estado)
                elif datos["estado"].lower() == "fail":
                    item_estado = item_centrado("Fail.")
                    item_estado.setBackground(Qt.GlobalColor.red)
                    self.ui.tablaSatelites.setItem(fila, 5, item_estado)
                else:
                    datos["estado"] = "Desconocido" # Si el estado no es reconocido, se pone "Desconocido"
                    self.ui.tablaSatelites.setItem(fila, 5, item_centrado(datos["estado"]))

                self.ui.tablaSatelites.setItem(fila, 6, item_centrado(datos["rms"]))
                self.ui.tablaSatelites.setItem(fila, 7, item_centrado(datos["sd"]))
                self.ui.tablaSatelites.setItem(fila, 8, item_centrado(datos["num_nps"]))
                self.ui.tablaSatelites.setItem(fila, 9, item_centrado(datos["retornos_por_np"]))

                #Imagen (gráfica)
                ruta_imagen = datos["ruta_foto"].replace(".png", "_manual.png") if os.path.exists(datos["ruta_foto"].replace(".png", "_manual.png")) else datos["ruta_foto"]
                label_img = ClickableLabel(ruta_imagen) # Llama a la clase ClickableLabel para mostrar la imagen y que se pueda ampliar
                pixmap = QPixmap(ruta_imagen)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(TAM_X, TAM_Y, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    label_img.setPixmap(pixmap)
                else:
                    label_img.setText("No img")
                    label_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.ui.tablaSatelites.setCellWidget(fila, 10, label_img)
                fila += 1

    def extraer_datos_satelite(self, ruta_sesion_input):
        #OBJ: Extraer los datos de los satélites de una sesión
        #PRE: Ruta de la sesión debe ser válida
        #POST: Devuelve una lista de diccionarios con los datos de los satélites
        #IN: ruta_sesion_input(str): Ruta de la sesión

        archivo_csv = (f"{ruta_sesion_input}/session_info_transposed.csv")
        resultados_lista = [] #Lista para almacenar los los diccionarios de cada satélite
        resultados = {} # Diccionario para almacenar los resultados de un satélite
        lista_satelites_frd = [] #Lista con los nombres de los archivos .frd encontrados en la subcarpeta RAW
        
        #Obtengo nombre por lectura de archivo en subcarpeta RAW

        ruta_RAW = (f"{ruta_sesion_input}/RAW")# Ruta a la subcarpeta RAW
        if os.path.exists(ruta_RAW): # si existe la ruta de la subcarpeta RAW, se buscan los archivos .frd
            for nombre_archivo in os.listdir(ruta_RAW):
                if nombre_archivo.endswith(".frd"):
                    lista_satelites_frd.append(nombre_archivo.replace(".frd", ""))  # Añadir el nombre del archivo sin la extensión .frd
        else:
            pass

        if os.path.exists(archivo_csv): #Si el archivo CSV existe, si no se buscará en la subcarpeta RAW
            with open(archivo_csv, newline='') as archivo:
                lector = csv.reader(archivo)
                # Leer la primera fila (encabezados)
                next(lector) # Quitar encabezados
                def obtener(col_idx): 
                        #OBJ: Obtener el valor de una columna específica de la fila
                        #PRE: La fila debe tener suficientes columnas
                        #POST: Devuelve el valor de la columna o "-" si no hay valor
                        return fila[col_idx] if len(fila) > col_idx and fila[col_idx].strip() != '' else "-"
                for fila in lector:
                    fecha_hora_nombre = obtener(0) #Nombre del archivo (formato: yyyymmdd_hhmm_nombre_codigo)
                    if fecha_hora_nombre in lista_satelites_frd:
                        longitud_onda = obtener(8)  # Longitud de onda
                        NPs = obtener(14) # Número de NPs
                        ObsPerNp = obtener(15) # Retornos por NP
                        RMS = obtener(19) # Columna 20 para el RMS
                        NP_mm = obtener(21) # Columna 22 para el NP en mm
                        estao_leido  = obtener(42)  # Columna 43 para el estado
                        ruta_satelite = ruta_sesion_input #Ruta de la sesion del pase
                        nombre_fr2 = obtener(1) # nombre del archivo FR2
                        nombre_cpf = obtener(2) # nombre del archivo CPF
                        nombre_np2 = obtener(3) # nombre del archivo NP2
                        nombre_png = obtener(4) # #nombre de la gráfica (formato: PNG/grafA.png)
                        
                        ruta_foto = f"{ruta_satelite}/PNG/{nombre_png}"  # Ruta de la gráfica
                        ruta_fr2 = f"{ruta_satelite}/FRD/{nombre_fr2}"   # Ruta del archivo FR2
                        ruta_cpf = f"{ruta_satelite}/CPF/{nombre_cpf}"   # Ruta del archivo CPF
                        ruta_np2 = f"{ruta_satelite}/NPT/{nombre_np2}"   # Ruta del archivo NP2
                        #Seleccionar de RMS el numero entero y 2 decimales
                        RMS = f"{float(RMS):.2f}" if RMS != "-" else "-"
                        NP_mm = f"{float(NP_mm):.2f}" if NP_mm != "-" else "-"
                        if (not os.path.exists(ruta_cpf)):
                            try:
                                patron = re.compile(r"\d{8}_(\d{4})_(.*?)_\w")
                                coincidencia = patron.match(fecha_hora_nombre)
                                if coincidencia:
                                    fecha_medicion = coincidencia.group(0)[:8]  # yyyyMMdd (primeros 8 dígitos)
                                    hora = f"{coincidencia.group(1)[:2]}:{coincidencia.group(1)[2:]}"  # Formato HH:MM
                                    nombre = coincidencia.group(2)
                                    # Eliminar la cadena ".frd" del fecha_hora_nombre
                                    nombre_archivo_sin_ext = fecha_hora_nombre.replace(".frd", "")
                                    try:
                                        ruta_fr2,ruta_np2 = self.encontrar_archivo_fr2_np2(ruta_sesion_input, nombre, fecha_medicion, hora)
                                        if ruta_np2:
                                            bueno = ruta_np2.split("/")[-1]
                                            bueno = bueno.split("\\")[-1]  # Extraer el nombre del archivo sin la ruta
                                        nombre_png = bueno.replace(".np2", ".png") if bueno else "grafA.png"  # Ruta de la gráfica
                                    except Exception as e:
                                        nombre_png = "grafA.png"
                                        ruta_np2 = None
                                        ruta_fr2 = None
                                    partes_nombre = nombre_archivo_sin_ext.split('_')
                                    partes_nombre = partes_nombre[:-1]
                                    nombre_cpf = f"{partes_nombre[0]}_{partes_nombre[1]}_{partes_nombre[2]}"
                                    ruta_cpf = f"{ruta_satelite}/CPF/{nombre_cpf}.cpf"  # Ruta del archivo CPF
                                    ruta_foto = f"{ruta_satelite}/PNG/{nombre_png}"  # Ruta de la gráfica
                            except Exception as e:
                                print(f"Error al procesar el archivo {fecha_hora_nombre}: {e}")
                                continue
                        # Procesar columna 0 (formato esperado: yyyymmdd_hhmm_nombre_codigo)
                        try: # Divide la cadena para obtener la hora y el nombre del satelite
                            partes = fecha_hora_nombre.split('_')
                            fecha_medicion = partes[0]  # yyyyMMdd (primeros 8 dígitos)
                            #hora_raw = partes[1]  # hhmm (últimos 4 dígitos)
                            hora = f"{partes[1][:2]}:{partes[1][2:]}"  # Formato HH:MM
                            nombre = partes[2]
                            #Except por si no se pude extraer la hora o el nombre
                        except:
                            hora = "-"
                            nombre = "-"
                        resultados= { 
                            'NomSat': nombre, # Nombre del satélite
                            'fecha_medicion': fecha_medicion, # Fecha de observación
                            'hora': hora, # Hora de observación
                            'estado': estao_leido, # Estado del pase
                            'rms': RMS, # Root Mean Square del pase
                            'sd': NP_mm, # Standar Deviation del pase
                            'longitud_onda': longitud_onda, # Longitud de onda
                            'num_nps': NPs, # Número de Puntos Normales
                            'retornos_por_np': ObsPerNp, # Retornos por NP
                            'ruta_foto': ruta_foto, # Ruta de la gráfica
                            'nombre_archivo': fecha_hora_nombre, # Nombre del archivo .FRD
                            'ruta_satelite': ruta_satelite, # Ruta del satélite
                            'ruta_fr2': ruta_fr2,  # Ruta del archivo FR2
                            'ruta_cpf': ruta_cpf,  # Ruta del archivo CPF
                            'ruta_np2': ruta_np2   # Ruta del archivo NP2

                        } #Diccionario con los datos del satélite
                        resultados_lista.append(resultados) #Añade el diccionario a la lista de resultados
                    else: # Si no está en la lista de satélites con .FRD
                        continue    
        else: # CSV no exite, buscar en la subcarpeta RAW
            nombre = "-" 
            fecha_medicion = "-"
            hora = "-"
            RMS = "-"
            NP_mm = "-"
            longitud_onda = "-"
            NPs = "-"
            ObsPerNp = "-"
            ruta_satelite = ruta_sesion_input

            # Expresión regular para extraer hora y nombre
            patron = re.compile(r"\d{8}_(\d{4})_(.*?)_\w")
            #8 digitos para la fecha, 4 dígitos para la hora, nombre del satélite y código alfanumérico
            
            # Recorremos los archivos de la subcarpeta
            if os.path.exists(ruta_RAW): # si existe la ruta de la subcarpeta RAW, se buscan los archivos .frd
                for nombre_archivo in lista_satelites_frd:
                        try:
                            coincidencia = patron.match(nombre_archivo)
                            if coincidencia:
                                fecha_medicion = coincidencia.group(0)[:8]  # yyyyMMdd (primeros 8 dígitos)
                                hora = f"{coincidencia.group(1)[:2]}:{coincidencia.group(1)[2:]}"  # Formato HH:MM
                                nombre = coincidencia.group(2)
                                # Eliminar la cadena ".frd" del nombre_archivo
                                nombre_archivo_sin_ext = nombre_archivo.replace(".frd", "")
                                try:
                                    ruta_fr2,ruta_np2 = self.encontrar_archivo_fr2_np2(ruta_sesion_input, nombre, fecha_medicion, hora)
                                    if ruta_np2:
                                        bueno = ruta_np2.split("/")[-1]
                                        bueno = bueno.split("\\")[-1]  # Extraer el nombre del archivo sin la ruta
                                    nombre_png = bueno.replace(".np2", "_manual.png") if bueno else "grafA.png"  # Ruta de la gráfica
                                except Exception as e:
                                    nombre_png = "grafA.png"
                                    ruta_np2 = None
                                    ruta_fr2 = None
                                partes_nombre = nombre_archivo_sin_ext.split('_')
                                partes_nombre = partes_nombre[:-1]
                                nombre_cpf = f"{partes_nombre[0]}_{partes_nombre[1]}_{partes_nombre[2]}"
                                ruta_cpf = f"{ruta_satelite}/CPF/{nombre_cpf}.cpf"  # Ruta del archivo CPF
                                ruta_foto = f"{ruta_satelite}/PNG/{nombre_png}"  # Ruta de la gráfica
                                resultados= {
                                    'NomSat': nombre,
                                    'fecha_medicion': fecha_medicion,
                                    'hora': hora,
                                    'estado': '-',
                                    'rms': RMS,
                                    'sd': NP_mm,
                                    'longitud_onda': longitud_onda,
                                    'num_nps': NPs,
                                    'retornos_por_np': ObsPerNp,
                                    'ruta_foto': ruta_foto,
                                    'nombre_archivo': nombre_archivo_sin_ext,
                                    'ruta_satelite': ruta_satelite,

                                    'ruta_fr2': ruta_fr2,  # Ruta del archivo FR2
                                    'ruta_cpf':ruta_cpf,  # Ruta del archivo CPF
                                    'ruta_np2': ruta_np2   # Ruta del archivo NP2
                                }
                                resultados_lista.append(resultados)
                        except Exception as e:
                            print(f"Error al procesar el archivo {nombre_archivo}: {e}")
                            continue    
            else:
                pass
        return resultados_lista     

    def checkboxes_seleccionados(self):
        #OBJ: Obtener los índices de las filas seleccionadas en tablaSatelites
        #POST: Devuelve una lista de índices de las filas seleccionadas
        seleccionados = []
        for fila in range(self.ui.tablaSatelites.rowCount()):
            checkbox = self.ui.tablaSatelites.cellWidget(fila, 0)
            if checkbox.isChecked():
                seleccionados.append(fila)
        return seleccionados    
    
    def seleccionar_todos(self):
        #OBJ: Seleccionar o deseleccionar todos los checkboxes de la tabla
        #POST: Marca o desmarca todos los checkboxes de la tabla

        seleccionar = self.ui.SelectAll.isChecked()
        for fila in range(self.ui.tablaSatelites.rowCount()):
            checkbox = self.ui.tablaSatelites.cellWidget(fila, 0)
            checkbox.setChecked(seleccionar)

    def ProcesadoMan(self):
        #OBJ: Lama a copiar_archivos para crear la nueva sesión y llama a NPgo en modo manual
        #PRE: Deben estar seleccionados los satélites a procesar

        seleccionados = self.checkboxes_seleccionados()
        if not seleccionados:
            QMessageBox.warning(self, "Advertencia", f"No hay satélites seleccionados para procesar.")
        else:
            lista_errores, entero = self.copiar_archivos(seleccionados)
            QMessageBox.information(self, "Información", f"Satelites copiados en nueva sesion: Sesion {entero}.")
            
            if lista_errores:
                QMessageBox.warning(self, "Advertencia", f"No se encontraron los archivos de los satelites: {', '.join(lista_errores)}")
    
            try:
                script_path = "/opt/scope/bin/processing/npgo-manual-run.sh"
                ruta_config = "/opt/scope/bin/processing/config_processing.ini"
                ruta_sesion_comando = f"{self.ruta_sesion_fecha}"  # Ruta de la sesión
                comando = f"{script_path} {ruta_config} {ruta_sesion_comando}"
                os.system(comando)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al llamar a NPgo: {e}")
            
    def ProcesadoAuto(self):
        #OBJ: Lama a copiar_archivos para crear la nueva sesión y llama a NPgo en modo automático
        #PRE: Deben estar seleccionados los satélites a procesar

        seleccionados = self.checkboxes_seleccionados()
        if not seleccionados:
            QMessageBox.warning(self, "Advertencia", f"No hay satélites seleccionados para procesar.")
        else:
            lista_errores, entero = self.copiar_archivos(seleccionados)
            QMessageBox.information(self, "Información", f"Satelites copiados en nueva sesion: Sesion {entero}.")

            if lista_errores:
                QMessageBox.warning(self, "Advertencia", f"No se encontraron los archivos de los satelites: {', '.join(lista_errores)}")
            
            try:
                script_path = "/opt/scope/bin/processing/npgo-auto-run.sh"
                ruta_config = "/opt/scope/bin/processing/config_processing.ini"
                ruta_sesion_comando = f"{self.ruta_sesion_fecha}"  # Ruta de la sesión
                comando = f"{script_path} {ruta_config} {ruta_sesion_comando} {entero}"
                os.system(comando)
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al llamar a NPgo: {e}")
    
    def copiar_archivos(self, seleccionados):
        #OBJ: Copiar los archivos de los satélites seleccionados a una nueva carpeta de sesion (SessionUltimo+1)
        #PRE: "Seleccionados" no debe estar vacío, todos los satélites deben ser de la misma sesión
        #POST: Devuelve una lista con los nombres de los satélites cuyos archivos no se pudieron copiar
        #IN: seleccionados(list): Lista de índices de las filas seleccionadas en la tabla
        
        # Buscar la última carpeta SessionX en la ruta de sesiones
        sesiones_path = self.ruta_sesion_fecha #Sesion de la fecha del procesado
        session_folders = [
            d for d in os.listdir(sesiones_path)
            if os.path.isdir(os.path.join(sesiones_path, d)) and re.match(r"Session\d{2}$", d)
        ] #Lista de carpetas que cumplen con el patrón SessionXX

        if session_folders:
            # Extraer el número de sesión con dos dígitos y encontrar el máximo
            last_session_num = max(
                int(re.search(r"Session(\d{2})$", s).group(1))
                for s in session_folders if re.search(r"Session(\d{2})$", s)
            )
            last_session_name = f"Session{last_session_num:02d}"
        else:
            last_session_name = None

        ruta_destino = f"{self.ruta_sesion_fecha}/Session{last_session_num+1:02d}"
        
        # Copiar la estructura de carpetas internas de la última sesión (sin archivos)
        if last_session_name:
            ruta_ultima_sesion = os.path.join(sesiones_path, last_session_name)
            for item in os.listdir(ruta_ultima_sesion):
                src_path = os.path.join(ruta_ultima_sesion, item)
                dst_path = os.path.join(ruta_destino, item)
                if os.path.isdir(src_path):
                    os.makedirs(dst_path, exist_ok=True)
                    # Crear subcarpetas (sin copiar archivos)
                    for subitem in os.listdir(src_path):
                        sub_src = os.path.join(src_path, subitem)
                        sub_dst = os.path.join(dst_path, subitem)
                        if os.path.isdir(sub_src):
                            os.makedirs(sub_dst, exist_ok=True)

        #Copia los ficheros de los satélites seleccionados a la nueva carpeta de sesión y los ficheros de datos
        lista_errores = []
        satelite_selecc = self.datos_satelites[seleccionados[0]]  # Tomar el primer satélite para obtener la ruta de destino
        try: 
            os.system(f"cp '{satelite_selecc['ruta_satelite']}/session_info.csv' '{ruta_destino}/'")
            os.system(f"cp '{satelite_selecc['ruta_satelite']}/session_info.json' '{ruta_destino}/'")
            os.system(f"cp '{satelite_selecc['ruta_satelite']}/session_info_transposed.csv' '{ruta_destino}/'")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al copiar los archivos de datos: {e}")

        for fila in seleccionados:
            satelite_selecc = self.datos_satelites[fila]
            # Copiar los archivos .FRD y .cpf a la nueva carpeta de sesiones
            ruta_frd = f"{satelite_selecc['ruta_satelite']}/RAW/{satelite_selecc['nombre_archivo']}.frd"
            if (os.path.exists(ruta_frd) and os.path.exists(satelite_selecc['ruta_cpf'])):
                try:
                    # Copiar el archivo .frd y .cpf a las subcarpetas correspondientes
                    try:
                        os.system(f"cp '{ruta_frd}' '{ruta_destino}/RAW/'")
                        os.system(f"cp '{satelite_selecc['ruta_cpf']}' '{ruta_destino}/CPF/'")
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Error al copiar los archivos FRD y CPF de {satelite_selecc['nombre_archivo']}: {e}")
                        lista_errores.append(satelite_selecc['nombre_archivo'])
                        continue
                        #Solo añade en estos casos, ya que son los ficheros que se necesitan para procesar

                    if (os.path.exists(satelite_selecc['ruta_foto'])):
                        os.system(f"cp '{satelite_selecc['ruta_foto']}' '{ruta_destino}/PNG/'")
                    # Copiar el archivo .np2 a la subcarpeta NPT
                    if (satelite_selecc['ruta_np2'] and os.path.exists(satelite_selecc['ruta_np2'])):
                        os.system(f"cp '{satelite_selecc['ruta_np2']}' '{ruta_destino}/NPT/'")
                    #Copiar el archivo .fr2 a la subcarpeta FRD
                    if (satelite_selecc['ruta_fr2'] and os.path.exists(satelite_selecc['ruta_fr2'])):
                        os.system(f"cp '{satelite_selecc['ruta_fr2']}' '{ruta_destino}/FRD/'")
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Error al copiar archivos secundarios de {satelite_selecc['nombre_archivo']}: {e}")
                    continue
            else:
                lista_errores.append(satelite_selecc['nombre_archivo'])
        return lista_errores,(last_session_num+1)  # Devuelve la lista de errores si no se pudieron copiar los archivos de algún satélite

    def SubirDatos(self):
        #OBJ: Subir los datos de los satélites seleccionados a edc
        #PRE: Deben estar seleccionados los satélites a subir
        
        seleccionados = self.checkboxes_seleccionados()
        if not seleccionados:
            QMessageBox.warning(self, "Advertencia", f"No hay satelites seleccionados para subir.")        
        else:
            lista_dirs_fr2 = [] # Lista de rutas de archivos .fr2
            lista_dirs_np2 = [] # Lista de rutas de archivos .np2
            lista_errores = []  # Lista de pases que han generado errores
            i = 0  # Contador para ajustar el índice de las filas restantes
            for fila in seleccionados:
                satelite_selecc = self.datos_satelites[fila]
                nombre_sat = satelite_selecc['NomSat']
                try:
                    fr2 = satelite_selecc['ruta_fr2']
                    np2 = satelite_selecc['ruta_np2']
                    if os.path.exists(fr2) and os.path.exists(np2):
                        lista_dirs_fr2.append(fr2)
                        lista_dirs_np2.append(np2)
                        # Eliminar la fila de la tabla y de la lista de datos
                        self.ui.tablaSatelites.removeRow(fila - i)  # -i para ajustar el índice después de eliminar
                        self.datos_satelites[fila]= None  # Limpiar los datos del satélite eliminado
                        i += 1  # Incrementar el contador para ajustar el índice de las filas restantes
                    else:
                        raise FileNotFoundError(f"No se encontraron archivos .fr2 o .np2 para el satélite {nombre_sat}.")    
                except Exception as e:
                    print(f"Error: {e}")
                    lista_errores.append(satelite_selecc['nombre_archivo'])
            self.datos_satelites = [s for s in self.datos_satelites if s is not None]  # Filtrar los None
            if lista_errores:
                QMessageBox.warning(self, "Advertencia", f"No se encontraron archivos .fr2 o .np2 para los siguientes satélites:\n{', '.join(lista_errores)}")        
            

            config = configparser.ConfigParser(interpolation=None)
            ruta_credenciales = os.path.dirname(os.path.dirname(__file__)) + "/" +"datos_externos/sftp_credenciales.ini"
            config.read(ruta_credenciales)

            host = config['SFTP']['host']
            puerto = int(config['SFTP']['port'])
            usuario = config['SFTP']['username']
            contrasena = config['SFTP']['password']
            ruta_remota = config['SFTP']['remote_path']

            try:
                # Barra de progreso emergente
                total = len(lista_dirs_fr2) + len(lista_dirs_np2)
                progreso = QProgressDialog("Subiendo archivos...", "Cancelar", 0, total, self)
                progreso.setWindowTitle("Progreso de subida")
                progreso.setWindowModality(Qt.WindowModality.ApplicationModal)
                progreso.setAutoClose(True)
                i = 0  # Contador para actualizar la barra de progreso

                # Establecer conexión SFTP
                transport = paramiko.Transport((host, puerto))
                transport.connect(username=usuario, password=contrasena)
                sftp = paramiko.SFTPClient.from_transport(transport)

                # Subir archivos de ambas listas          
                for archivo_local in lista_dirs_fr2 + lista_dirs_np2:
                    if progreso.wasCanceled():
                        break
                    if not os.path.exists(archivo_local):
                        QMessageBox.warning(self, "Archivo no encontrado", f"No existe: {archivo_local}")
                        continue
                    nombre = os.path.basename(archivo_local)
                    ruta_destino = os.path.join(ruta_remota, nombre).replace("\\", "/")
                    sftp.put(archivo_local, ruta_destino)
                    i += 1
                    progreso.setValue(i)
                    progreso.setLabelText(f"Subiendo: {nombre}, {i} de {total}")
                sftp.close()
                transport.close()
                progreso.close()  # Cerrar la barra de progreso
                QMessageBox.information(self, "Éxito", "Todos los archivos fueron subidos correctamente")
            except Exception as e:
                progreso.close()
                QMessageBox.critical(self, "Error", f"Error al subir archivos:\n{e}")

    
    def Eliminar_datos(self):
        #OBJ: Eliminar los datos de los satélites seleccionados de los ficheros de datos y los ficheros de los pases
        #PRE: Deben estar seleccionados los satélites a eliminar
        
        seleccionados = self.checkboxes_seleccionados()
        if not seleccionados:
            QMessageBox.warning(self, "Advertencia", f"No hay satélites seleccionados para eliminar.")
        else:
            seleccionados_nombres = [self.datos_satelites[fila]['nombre_archivo'] for fila in seleccionados]
            
            mensaje = "Pases a eliminar:\n" + "\n".join(seleccionados_nombres) + "\n\n¿Estás seguro de que quieres eliminar estos pases?"
            respuesta = QMessageBox.question(
                self,
                "Confirmar selección",
                mensaje,
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
            ) # Muestra un mensaje de confirmación con los pases seleccionadas

            if respuesta == QMessageBox.StandardButton.Ok:
                satelites_eliminados = []
                i=0
                for fila in seleccionados:
                    satelite_selecc = self.datos_satelites[fila]
                    try:
                        if satelite_selecc['ruta_cpf'] and os.path.exists(satelite_selecc['ruta_cpf']):
                            try:
                                os.remove(satelite_selecc['ruta_cpf'])
                            except Exception as e:
                                print(f"Error al eliminar {satelite_selecc['ruta_cpf']}: {e}")
                        else:
                            print(f"Archivo no encontrado: {satelite_selecc['ruta_cpf']}")
                        ruta_fr2 = satelite_selecc['ruta_fr2']
                        if ruta_fr2 and os.path.exists(ruta_fr2):
                            try:
                                os.remove(ruta_fr2)
                            except Exception as e:
                                print(f"Error al eliminar {ruta_fr2}: {e}")
                        else:
                            print(f"Archivo no encontrado: {ruta_fr2}")
                        if satelite_selecc['ruta_np2'] and os.path.exists(satelite_selecc['ruta_np2']):
                            try:
                                os.remove(satelite_selecc['ruta_np2'])
                            except Exception as e:
                                print(f"Error al eliminar {satelite_selecc['ruta_np2']}: {e}")
                        else:
                            print(f"Archivo no encontrado: {satelite_selecc['ruta_np2']}")
                        # Eliminar la imagen de la gráfica
                        if satelite_selecc['ruta_foto'] and os.path.exists(satelite_selecc['ruta_foto']):
                            try:
                                os.remove(satelite_selecc['ruta_foto'])
                            except Exception as e:
                                print(f"Error al eliminar {satelite_selecc['ruta_foto']}: {e}")
                        else:
                            print(f"Archivo no encontrado: {satelite_selecc['ruta_foto']}")

                        if os.path.exists(f"{satelite_selecc['ruta_satelite']}/RAW/{satelite_selecc['nombre_archivo']}.frd"):
                            try:
                                os.remove(f"{satelite_selecc['ruta_satelite']}/RAW/{satelite_selecc['nombre_archivo']}.frd")
                            except Exception as e:
                                print(f"Error al eliminar {satelite_selecc['ruta_satelite']}/RAW/{satelite_selecc['nombre_archivo']}.frd: {e}")
                        else:
                            print(f"Archivo no encontrado: {satelite_selecc['ruta_satelite']}/RAW/{satelite_selecc['nombre_archivo']}.frd")
                        
                        # Eliminar la fila de la tabla y de la lista de datos
                        self.ui.tablaSatelites.removeRow(fila - i)  # -i para ajustar el índice después de eliminar
                        satelites_eliminados.append(satelite_selecc['nombre_archivo'])
                        # Eliminar la fila correspondiente del archivo CSV
                        self.datos_satelites[fila]= None  # Limpiar los datos del satélite eliminado
                        i += 1  # Incrementar el contador para ajustar el índice de las filas restantes
                    except Exception as e:
                        print(f"Error al procesar el satélite seleccionado: {e}")
                        print(f"Nombre del satélite: {satelite_selecc['NomSat']}")
                self.datos_satelites = [s for s in self.datos_satelites if s is not None]  # Filtrar los None

                try:
                    archivo_csv = os.path.join(satelite_selecc['ruta_satelite'], "session_info_transposed.csv")
                    if os.path.exists(archivo_csv):
                        filas_nuevas = []
                        with open(archivo_csv, newline='', encoding='utf-8') as f:
                            reader = list(csv.reader(f))
                            encabezados = reader[0]
                            for row in reader[1:]:
                                if row and row[0] not in satelites_eliminados:
                                    filas_nuevas.append(row)
                        with open(archivo_csv, 'w', newline='', encoding='utf-8') as f:
                            writer = csv.writer(f)
                            writer.writerow(encabezados)
                            writer.writerows(filas_nuevas)
                            f.close()
                except Exception as e:
                    print(f"Error al eliminar la fila del CSV: {e}")
                    # Eliminar también las filas correspondientes del archivo sesion_info.csv si existe
                try:
                    archivo_info = os.path.join(satelite_selecc['ruta_satelite'], "session_info.csv")
                    if os.path.exists(archivo_info):
                        with open(archivo_info, newline='', encoding='utf-8') as f:
                            reader = list(csv.reader(f))
                            filas = reader
                            # Transponer para trabajar por columnas (cada columna es un satélite)
                            columnas = list(zip(*filas))
                            # Buscar índices de columnas a eliminar (por nombre_archivo)
                            indices_a_eliminar = []
                            for idx, col in enumerate(columnas):
                                if idx == 0:
                                    continue  # Saltar encabezado
                                if col[0] in satelites_eliminados:
                                    indices_a_eliminar.append(idx)
                            # Eliminar columnas marcadas
                            columnas_nuevas = [col for idx, col in enumerate(columnas) if idx not in indices_a_eliminar]
                            # Volver a filas
                            filas_nuevas = list(zip(*columnas_nuevas))
                        with open(archivo_info, 'w', newline='', encoding='utf-8') as f:
                            writer = csv.writer(f)
                            writer.writerows(filas_nuevas)
                except Exception as e:
                    print(f"Error al eliminar columnas del CSV sesion_info.csv: {e}")
                    # Eliminar también los datos correspondientes del archivo session_info.json si existe
                try:
                    archivo_json = os.path.join(satelite_selecc['ruta_satelite'], "session_info.json")
                    if os.path.exists(archivo_json):
                        with open(archivo_json, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        # Suponiendo que los datos de los satélites están en una lista o dict bajo una clave conocida
                        # Aquí se asume que es una lista de dicts con clave 'nombre_archivo'
                        for clave in satelites_eliminados:
                            data.pop(clave, None)
                        with open(archivo_json, "w", encoding="utf-8") as f:
                            json.dump(data, f, ensure_ascii=False, indent=4)
                except Exception as e:
                    print(f"Error al eliminar datos del JSON session_info.json: {e}")
            else:
                pass  # Si el usuario cancela la operación, no se hace nada
    
    def encontrar_archivo_fr2_np2(self,directorio, nombre, fecha, hora):
        #OBJ: Encontrar los archivos .fr2 y .np2 de un satélite
        #PRE: El directorio debe existir y contener los archivos .fr2 y .np2
        #POST: Devuelve las rutas de los archivos .fr2 y .np2 si existen, si no devuelve None
        #IN: directorio(str): Ruta del directorio donde buscar los archivos, nombre(str): Nombre del satélite, 
        #IN: fecha(str): Fecha en formato YYYYMMDD, hora(str): Hora en formato HHMM

        hora = hora.replace(":", "")  # Eliminar los dos puntos de la hora para que coincida con el patrón
        patron = re.compile(rf"\d{{4}}_{re.escape(nombre)}_[A-Z]{{3}}_{fecha}_{hora}_\d{{2}}\.fr2$", re.IGNORECASE)
        ruta_fr2 = None
        ruta_np2 = None
        directorio_frd = f'{directorio}/FRD'
        for archivo in os.listdir(directorio_frd):
            if patron.match(archivo):
                ruta_fr2 = os.path.join(directorio_frd, archivo)
        if ruta_fr2:
            directorio_npt = f'{directorio}/NPT'
            patron = re.compile(rf"\d{{4}}_{re.escape(nombre)}_[A-Z]{{3}}_{fecha}_{hora}_\d{{2}}\.np2$", re.IGNORECASE)
            for archivo in os.listdir(directorio_npt):
                if patron.match(archivo):
                    ruta_np2 = os.path.join(directorio_npt,archivo)
        return ruta_fr2, ruta_np2
