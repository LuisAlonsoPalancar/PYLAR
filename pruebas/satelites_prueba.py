import os
import csv
import re
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QTableWidgetItem, QCheckBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from ClickableLabel import ClickableLabel 
#TODO:
# añadir funcionalidad a los botones
#  Hoja de Requisitos

class SatelitesWindow(QWidget):
    def __init__(self, sesiones_seleccionadas, fecha):
        super().__init__()
        uic.loadUi("satelites.ui", self)
        self.sesiones = sesiones_seleccionadas
        self.fecha =fecha.toString("yyyyMMdd")

        self.datos_satelites = []
        print(f"Fecha recibida en tercera ventana: {self.fecha}")
        # Establecer la fecha en el widget, en formato dd/MM/yyyy
        self.fecha_entrada.setStyleSheet("font-size: 14pt; font-weight: 700;")
        self.fecha_entrada.setText(f"Fecha: {fecha.toString('dd/MM/yyyy')}")
        self.cargar_datos()
        self.BotonSubir.clicked.connect(self.checkboxes_seleccionados)  # Conectar el botón a la función de checkboxes seleccionados
        self.BotonProcMan.clicked.connect(self.obtener_WidththColumnas)  # Conectar el botón a la función de obtener ancho de columnas

    def cargar_datos(self):
        fila = 0
        self.tablaSatelites.setRowCount(fila)
        #Configurar nombre de las columnas y color gris en las cabeceras
        self.tablaSatelites.verticalHeader().setVisible(False)
        # Añadir una columna extra para el checkbox al principio
        self.tablaSatelites.setColumnCount(10)
        self.tablaSatelites.setHorizontalHeaderLabels([
            "", "Sesión", "Nombre Satelite", "  Hora  ", "  Estado  ",
            "  RMS  ", "  SD  ", "Num de NPs", "Retornos per NP", "Graficas"
        ])
        
        #Tamaño de las columnas
        self.tablaSatelites.setColumnWidth(0, 40)  # Ancho de la columna del checkbox
        self.tablaSatelites.setColumnWidth(1, 79)  # Ancho de la columna de sesión
        self.tablaSatelites.setColumnWidth(2, 94)  # Ancho de la columna del nombre del satélite
        self.tablaSatelites.setColumnWidth(3, 70)   # Ancho de la columna de hora
        self.tablaSatelites.setColumnWidth(4, 60)   # Ancho de la columna de estado
        self.tablaSatelites.setColumnWidth(5, 77)   # Ancho de la columna de RMS
        self.tablaSatelites.setColumnWidth(6, 69)   # Ancho de la columna de SD
        self.tablaSatelites.setColumnWidth(7, 78)  # Ancho de la columna de número de NPs
        self.tablaSatelites.setColumnWidth(8, 98)  # Ancho de la columna de retornos por NP
        self.tablaSatelites.setColumnWidth(9, 204)  # Ancho de la columna de gráficas
        # Establecer el estilo de las cabeceras


        self.tablaSatelites.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: lightgray; }")
        #Las comumnas son el numero de sesion, el nombre del satelite,
        #la hora de cada satelite, el estado del satelite, 
        # el RMS, la SD, el numero de NPs, los retornos captados por NP y la grafica de cada uno
        TAM_X = 210  # Ancho deseado de la imagen
        TAM_Y = 130   # Alto deseado de la imagen
        for sesion in self.sesiones:
            ruta = f"./carpetas/Sessions_{self.fecha}/{sesion}"
            print(f"Ruta de la sesión: {ruta}")
            self.datos_satelites = self.extraer_datos_satelite(ruta)
            for datos in self.datos_satelites:
                self.tablaSatelites.insertRow(fila)
                # Añadir checkbox en la primera columna
                checkbox = QCheckBox()
                self.tablaSatelites.setCellWidget(fila, 0, checkbox)
            # Helper para crear QTableWidgetItem centrado
                def item_centrado(texto):
                    item = QTableWidgetItem(str(texto))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    return item  
                self.tablaSatelites.setItem(fila, 1, item_centrado(sesion))
                self.tablaSatelites.setItem(fila, 2, item_centrado(datos["NomSat"]))
                self.tablaSatelites.setItem(fila, 3, item_centrado(datos["hora"]))
                # Si el estado es "Fallo", cambiar el color de la celda a rojo
                if datos["estado"] == "Bien":
                    item_estado = item_centrado(datos["estado"])
                    item_estado.setBackground(Qt.GlobalColor.green)
                    self.tablaSatelites.setItem(fila, 4, item_estado)
                elif datos["estado"] == "Fallo":
                    item_estado = item_centrado(datos["estado"])
                    item_estado.setBackground(Qt.GlobalColor.red)
                    self.tablaSatelites.setItem(fila, 4, item_estado)
                else:
                    self.tablaSatelites.setItem(fila, 4, item_centrado(datos["estado"]))

                self.tablaSatelites.setItem(fila, 5, item_centrado(datos["rms"]))
                self.tablaSatelites.setItem(fila, 6, item_centrado(datos["sd"]))
                self.tablaSatelites.setItem(fila, 7, item_centrado(datos["num_nps"]))
                self.tablaSatelites.setItem(fila, 8, item_centrado(datos["retornos_por_np"]))
                # Columna 9: Imagen (gráfica)
                ruta_imagen = os.path.join(ruta, "PNG", datos["graficas"])
                label_img = ClickableLabel(ruta_imagen)
                pixmap = QPixmap(ruta_imagen)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(TAM_X, TAM_Y, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    label_img.setPixmap(pixmap)
                else:
                    label_img.setText("No img")
                    label_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tablaSatelites.setCellWidget(fila, 9, label_img)
                fila += 1

    def obtener_WidththColumnas(self):
        #DELETE
        # Método para obtener el ancho de las columnas de la tabla
        anchos = []
        for col in range(self.tablaSatelites.columnCount()):
            ancho_columna = self.tablaSatelites.columnWidth(col)
            anchos.append(ancho_columna)
            print(f"Ancho de la columna {col}: {ancho_columna}")


    def extraer_datos_satelite(self, ruta_sesion):
        archivo_csv = (f"{ruta_sesion}/session_info_transposed.csv")
        resultados_lista = []
        resultados = {}
        if os.path.exists(archivo_csv):
            with open(archivo_csv, newline='') as archivo:
                lector = csv.reader(archivo)
                # Leer la primera fila (encabezados)
                encabezados = next(lector)
                for fila in lector:
                    # Evitar errores con filas incompletas
                    def obtener(col_idx):
                        return fila[col_idx] if len(fila) > col_idx and fila[col_idx].strip() != '' else "-"
                    fecha_hora_nombre = obtener(0)
                    grafica = obtener(4)
                    # Comprobar si la ruta de la gráfica es válida
                    NPs = obtener(14)
                    ObsPerNp = obtener(15)
                    RMS = obtener(19)
                    NP_mm = obtener(21)
                    estao_leido  = obtener(42)  # Columna 43 para el estado

                    #Seleccionar de RMS el numero entero y 2 decimales
                    RMS = f"{float(RMS):.2f}" if RMS != "-" else "-"
                    NP_mm = f"{float(NP_mm):.2f}" if NP_mm != "-" else "-"
                    # Procesar columna 0 (formato esperado: yyyymmdd_hhmm_nombre_codigo)
                    try:
                        partes = fecha_hora_nombre.split('_')
                        hora_raw = partes[1]  # hhmm (últimos 4 dígitos)
                        hora = f"{hora_raw[:2]}:{hora_raw[2:]}"  # Formato HH:MM
                        nombre = partes[2]
                        #Except por si no se pude extraer la hora o el nombre
                    except IndexError:
                        hora = "-"
                        nombre = "-"
                    #Compruebo el valor de la columna 43, y si es "fail", lo cambio a "Fallo"
                    estado = "Desconocido"
                    if estao_leido.lower() == "fail":
                        estado = "Fallo"
                    elif estao_leido.lower() == "passed.":
                        estado = "Bien"
                    resultados= {
                        'NomSat': nombre,
                        'hora': hora,
                        'estado': estado,
                        'rms': RMS,
                        'sd': NP_mm,
                        'num_nps': NPs,
                        'retornos_por_np': ObsPerNp,
                        'graficas': grafica,
                        'nombre_archivo': fecha_hora_nombre
                    }
                    resultados_lista.append(resultados)
        else:
            print("El archivo no existe.")
            hora = "-"
            nombre = "-" 
            NPs = "-"
            ObsPerNp = "-"
            RMS = "-"
            NP_mm = "-"
            #Obtengo nombre por lectura de archivo en subcarpeta RAW
            # Aquí podrías agregar lógica para manejar el caso de que el archivo no exista
            # Ruta a la subcarpeta

            ruta_subcarpeta = "./pruebas/RAW"
            # Expresión regular para extraer hora y nombre
            patron = re.compile(r"\d{8}_(\d{4})_(.*?)_\w+\.frd")
            # Recorremos los archivos de la subcarpeta
            for nombre_archivo in os.listdir(ruta_subcarpeta):
                if nombre_archivo.endswith(".frd"):
                    coincidencia = patron.match(nombre_archivo)
                    #print(f"Nombre del archivo: {nombre_archivo}")
                    #print(f"Coincidencia: {coincidencia}")  
                    if coincidencia:
                        hora_raw = coincidencia.group(1)  # hhmm (últimos 4 dígitos)
                        hora = f"{hora_raw[:2]}:{hora_raw[2:]}"  # Formato HH:MM
                        nombre = coincidencia.group(2)
                resultados= {
                    'NomSat': nombre,
                    'hora': hora,
                    'estado': NPs,
                    'rms': RMS,
                    'sd': NP_mm,
                    'num_nps': NPs,
                    'retornos_por_np': ObsPerNp,
                    'graficas': 'grafA.png',
                    'nombre_archivo': nombre_archivo
                }
                resultados_lista.append(resultados)
                #print(f'Hora: {hora[:2]}:{hora[2:]}, Nombre: {nombre}, NPs: {NPs}, ObsPerNp: {ObsPerNp}, RMS: {RMS}, NP_mm: {NP_mm}')
        return resultados_lista

    def checkboxes_seleccionados(self):
        seleccionados = []
        for fila in range(self.tablaSatelites.rowCount()):
            checkbox = self.tablaSatelites.cellWidget(fila, 0)
            if checkbox.isChecked():
                seleccionados.append(fila)
                print(f"Fila {fila} seleccionada. Nombre del fichero: {self.datos_satelites[fila]['nombre_archivo']}")
        #return seleccionados
        print(f"Checkboxes seleccionados: {seleccionados}")
            