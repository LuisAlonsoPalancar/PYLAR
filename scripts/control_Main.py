"""
----------------------------------
Nombre del archivo:     control_Main.py
Descripción:            Este script controla la ventana principal de la aplicación, 
                        gestionando la interacción con el calendario 
                        y la navegación a la ventana de sesiones.

Entrada(s):             
Salida(s):              Muestra la ventana principal de la aplicación y llama a la ventana de sesiones.
Dependencias:           PyQt6 (V 6.4.2)
Autor:                  Luis Alonso Palancar
Fecha:                  Julio 2025
----------------------------------
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QDate
from PyQt6.QtGui import QIcon

from scripts.control_Calendario import MainWindow as controlCalendarWindow
from scripts.control_Satelites import SatelitesWindow as controlSatelitesWindow
from scripts.control_Sesiones import SesionesWindow as controlSesionesWindow # Ventana de Sesiones

from vistas.Window_Main_ui import Ui_MainWindow  # Ventana Principal

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #uic.loadUi(os.path.join("vistas", "Window_Main.ui"), self)
        
        self.ui = Ui_MainWindow()  # Crear una instancia de la clase Ui_MainWindow
        self.ui.setupUi(self)  # Configurar la interfaz de usuario
        #Variables de la ventana principal
        self.fecha = QDate.currentDate()  # Guarda la fecha seleccionada, inicialmente la fecha actual
        self.sesiones = []  # Lista de sesiones seleccionadas

        # Crear una instancia de la ventana secundaria desde su controlador
        self.ui.BotonCalendario.clicked.connect(lambda: self.abrir_calendario(self.fecha))  # Botón para abrir el calendario
        self.ui.BotonPases.clicked.connect(self.abrir_satelites)
        self.ui.BotonSesiones.clicked.connect(self.abrir_sesiones)
        self.ui.BotonCerrar.clicked.connect(sys.exit)  # Conectar el botón de cerrar a la función close
        self.abrir_calendario()  # Abrir la ventana de calendario al iniciar la aplicación
        
    def abrir_calendario(self, fecha_input=None):
        #OBJ: Abre la ventana de Calendario en el Frame de contenido
        #POST: Establece la fecha actual y la lista de sesiones vacía
        self.fecha = fecha_input if fecha_input else QDate.currentDate()  # Actualiza la fecha si se proporciona una nueva
        self.contenidoFrame = controlCalendarWindow(self.fecha)
        self.contenidoFrame.fecha_seleccionada.connect(self.abrir_sesiones)  # Conectar la señal de fecha seleccionada
        # Limpiar el QFrame_Contenido antes de añadir el nuevo widget
        for i in reversed(range(self.ui.QFrame_Contenido.layout().count())):
            widget_to_remove = self.ui.QFrame_Contenido.layout().itemAt(i).widget()
            if widget_to_remove is not None:
                widget_to_remove.setParent(None)
        # Añadir la ventana secundaria al QFrame_Contenido
        self.ui.QFrame_Contenido.layout().addWidget(self.contenidoFrame)

    def abrir_sesiones(self,fecha_input=None, sesiones_input=None):
        #OBJ: Abre la ventana de Sesiones en el Frame de contenido con la fecha seleccionada
        #POST: Actualiza la lista de sesiones si se proporcionan nuevas
        self.fecha = fecha_input if fecha_input else self.fecha  # Actualiza la fecha si se proporciona una nueva
        self.sesiones = sesiones_input if sesiones_input != None else self.sesiones  # Actualiza las sesiones si se proporciona una nueva
        # Abre la ventana de Sesiones
        self.contenidoFrame = controlSesionesWindow(self.fecha, self.sesiones)
        self.contenidoFrame.sesiones_seleccionadas.connect(self.abrir_satelites)  # Conectar la señal de sesiones seleccionadas
        # Limpiar el QFrame_Contenido antes de añadir el nuevo widget
        for i in reversed(range(self.ui.QFrame_Contenido.layout().count())):
            widget_to_remove = self.ui.QFrame_Contenido.layout().itemAt(i).widget()
            if widget_to_remove is not None:
                widget_to_remove.setParent(None)
        # Añadir la ventana secundaria al QFrame_Contenido
        self.ui.QFrame_Contenido.layout().addWidget(self.contenidoFrame)
        
    def abrir_satelites(self,sesiones_input=None):
        #OBJ: Abre la ventana de Satélites en el Frame de contenido con las sesiones seleccionadas
        #POST: Actualiza la lista de sesiones con las sesiones si se cambian
        
        self.sesiones = sesiones_input if sesiones_input else self.sesiones  # Actualiza la lista de sesiones si se proporciona una nueva
        
        # Abre la ventana de Satélites
        self.contenidoFrame = controlSatelitesWindow(self.sesiones, self.fecha)
        self.contenidoFrame.sesiones_seleccionadas.connect(self.actualizar_sesiones)  # Conectar la señal de sesiones seleccionadas

        # Limpiar el QFrame_Contenido antes de añadir el nuevo widget
        for i in reversed(range(self.ui.QFrame_Contenido.layout().count())):
            widget_to_remove = self.ui.QFrame_Contenido.layout().itemAt(i).widget()
            if widget_to_remove is not None:
                widget_to_remove.setParent(None)
        
        # Añadir la ventana secundaria al QFrame_Contenido
        self.ui.QFrame_Contenido.layout().addWidget(self.contenidoFrame)
    
    def actualizar_sesiones(self, sesiones_nuevas):
        #OBJ: Actualizar la lista de sesiones seleccionadas llegadas desde la ventana de Satélites
        #POST: Actualiza la lista de sesiones con las nuevas sesiones
        self.sesiones = sesiones_nuevas

def main():
        app = QApplication(sys.argv)
        app.setWindowIcon(QIcon(os.path.dirname(os.path.dirname(__file__)) + "/vistas/logos/Logo YLARA.png"))  # Icono para la barra de tareas
        window = MainWindow()
        #window.show()
        window.showMaximized()
        sys.exit(app.exec())
