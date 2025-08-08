"""
----------------------------------
Nombre del archivo:     control_Sesiones.py
Descripción:            Este script controla la ventana de sesiones de la aplicación, 
                        gestionando la interacción con las sesiones y la navegación
                        a la ventana de satélites.

Entrada(s):             Fecha de la sesión seleccionada.
Salida(s):              Muestra la ventana de sesiones de la aplicación y llama a la ventana de satélites.
Dependencias:           PyQt6 (V 6.4.2)
Autor:                  Luis Alonso Palancar
Fecha:                  Julio 2025
----------------------------------
"""
import os
from PyQt6.QtWidgets import QWidget, QListWidgetItem, QAbstractItemView, QMessageBox
from PyQt6.QtCore import Qt,pyqtSignal

from vistas.Window_Sesiones_ui import Ui_Form as Ventana_lista_sesiones  # Ventana Sesiones (esta)
class SesionesWindow(QWidget):
    sesiones_seleccionadas = pyqtSignal(list) #signal que emite la lista de sesiones seleccionadas

    def __init__(self, fecha, sesiones):
        super().__init__()

        self.fecha = fecha  # Guarda la fecha recibida
        self.ui = Ventana_lista_sesiones()  # Crear una instancia de la clase
        self.ui.setupUi(self)  # Configurar la interfaz de usuario

        self.sesiones = sesiones  # Lista de sesiones seleccionadas entrantes

        #Formato de carpetas: Sessions_yyyymmdd
        #Ruta base de las carpetas: opt/scope/data/export/processing/Sessions_yyyymmdd

        #Paso de formato de fecha al formato yyyymmdd
        fecha_str = self.fecha.toString("yyyyMMdd")
        self.ruta_sesion_fecha = f"./Sesiones/Sessions_{fecha_str}"
        ruta_rel_session_fecha = os.path.relpath(self.ruta_sesion_fecha)
        self.ruta_base = os.path.dirname(os.path.dirname(__file__)) + "/" + ruta_rel_session_fecha
        #self.ruta_base = f"/opt/scope/data/export/processing/Sessions_{fecha_str}" # Ruta de la sesión
        
        # Establecer la fecha en el widget, en formato dd/MM/yyyy
        self.ui.fecha_entrada.setStyleSheet("font-size: 14pt; font-weight: 700;")
        self.ui.fecha_entrada.setText(f"Fecha: {fecha.toString('dd/MM/yyyy')}")

        # Configurar la lista de carpetas
        self.ui.listaCarpetas.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection) #Desactivar selección de elementos
        self.cargar_carpetas(self.ruta_base) #Llama al método para cargar las carpetas
        if self.ui.listaCarpetas.count() == 0:
            QMessageBox.information(self, "Sin sesiones", "No hay sesiones disponibles para la fecha seleccionada.")
        self.ui.BotonVeri.clicked.connect(self.contar_seleccionadas) # Botón para verificar las carpetas seleccionadas
        self.ui.BotonRecargar.clicked.connect(lambda: self.cargar_carpetas(self.ruta_base))# Recargar las carpetas desde la ruta base

    def cargar_carpetas(self, ruta_entrada):
        #OBJ: Cargar subarpetas de la fecha indicada por la vaRiable fecha,cada subcapeta es una sesión de Scope
        #PRE: Ruta base debe ser válida
        #POST: Lista de carpetas se llena con los nombres de las SESIONES encontradas
        #IN: ruta_entrada(str): Ruta de entrada donde buscar las sesiones

        self.ui.listaCarpetas.clear()  # Limpiar la lista antes de agregar elementos
        if os.path.exists(ruta_entrada):
            sesiones_fecha = [] #Sesiones de la fecha seleccionada
            for sesion in os.listdir(ruta_entrada):  # Recorre y añade los nombres  de las carpetas (sesiones)
                ruta_completa = os.path.join(ruta_entrada, sesion)
                if os.path.isdir(ruta_completa):  # Verifica si es un directorio/carpeta
                    sesiones_fecha.append(sesion)
            for sesion in sorted(sesiones_fecha):  # Ordena alfabéticamente las carpetas
                item = QListWidgetItem(sesion)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)  # Añade la opción de check
                item.setCheckState(Qt.CheckState.Checked if sesion in self.sesiones else Qt.CheckState.Unchecked)  # Marca las sesiones seleccionadas
                self.ui.listaCarpetas.addItem(item)  # Añade a la lista
        else:
            print(f"La ruta {ruta_entrada} no existe. Sesión no existente?.")

    def contar_seleccionadas(self):
        #OBJ: Contar las carpetas seleccionadas y mostrar un mensaje de confirmación
        #PRE: Lista de carpetas debe estar cargada
        #POST: Muestra un mensaje con las carpetas seleccionadas y pregunta si se desea continuar

        seleccionadas = [] # Lista para almacenar las carpetas seleccionadas
        for i in range(self.ui.listaCarpetas.count()): #Cuenta las seleccionadas
            item = self.ui.listaCarpetas.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                seleccionadas.append(item.text())

        if not seleccionadas: #Si no hay seleccionadas, salta aviso
            QMessageBox.warning(self, "Aviso", "No se ha seleccionado ninguna carpeta.")
            return
        mensaje = "Carpetas seleccionadas:\n" + "\n".join(seleccionadas)
        respuesta = QMessageBox.question(
            self,
            "Confirmar selección",
            mensaje,
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
        ) # Muestra un mensaje de confirmación con las carpetas seleccionadas

        if respuesta == QMessageBox.StandardButton.Ok:
            self.sesiones_seleccionadas.emit(seleccionadas)  # Emite la señal con las carpetas seleccionadas
            self.close()  # Cierra la ventana después de enviar
        else:
            pass