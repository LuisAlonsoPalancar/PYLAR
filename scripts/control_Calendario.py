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


from PyQt6.QtWidgets import QWidget, QCalendarWidget
from PyQt6.QtCore import QDate,pyqtSignal


from vistas.Window_Calendario_ui import Ui_Form  # Ventana Calendario/Principal
class MainWindow(QWidget):
    fecha_seleccionada = pyqtSignal(QDate, list)

    def __init__(self, fecha_input=None):
        super().__init__()
        #uic.loadUi(os.path.join("vistas", "Window_Main.ui"), self)

        self.ui = Ui_Form()  # Crear una instancia de la clase Ui_Form
        self.ui.setupUi(self)  # Configurar la interfaz de usuario

        self.ui.Fecha.setDate(QDate.currentDate()) if not fecha_input else self.ui.Fecha.setDate(fecha_input)
        self.ui.Fecha.dateChanged.connect(self.ui.calendario.setSelectedDate)
        self.ui.calendario.setSelectedDate(self.ui.Fecha.date())
        self.ui.calendario.clicked.connect(self.actualizar_fecha)
        self.ui.SigVentana.clicked.connect(self.abrir_sesiones)
        # Ocultar la columna de las semanas en el calendario
        self.ui.calendario.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)

    def actualizar_fecha(self, fecha): 
        # Actualiza la fecha en el widget Fecha
        self.ui.Fecha.setDate(fecha)

    def abrir_sesiones(self): 
        #Abre la ventana de Sesiones con la fecha seleccionada
        fecha = self.ui.Fecha.date() # "Get" la fecha del widget
        self.fecha_seleccionada.emit(fecha,[]) #Fecha y lista de sesiones vacía
