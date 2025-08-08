"""
----------------------------------
Nombre del archivo:     control_Calendario.py
Descripción:            Este script controla la ventana del calendario, 
                        gestionando la selección de fechas y el envío de 
                        las mismas a la ventana principal.

Entrada(s):             
Salida(s):              Muestra la ventana del calendario de la aplicación y devuelve la fecha seleccionada.
Dependencias:           PyQt6 (V 6.4.2)
Autor:                  Luis Alonso Palancar
Fecha:                  Julio 2025
----------------------------------
"""


from PyQt6.QtWidgets import QWidget, QCalendarWidget
from PyQt6.QtCore import QDate,pyqtSignal


from vistas.Window_Calendario_ui import Ui_Form  # Ventana Calendario
class MainWindow(QWidget):
    fecha_seleccionada = pyqtSignal(QDate, list) #Signal que devuelve la fecha seleccionada y la lista de sesiones

    def __init__(self, fecha_input=None):
        super().__init__()

        self.ui = Ui_Form()  # Crear una instancia de la clase Ui_Form
        self.ui.setupUi(self)  # Configurar la interfaz de usuario

        #Conectar botones con sus acciones correspondientes
        self.ui.Fecha.setDate(QDate.currentDate()) if not fecha_input else self.ui.Fecha.setDate(fecha_input)
        self.ui.Fecha.dateChanged.connect(self.ui.calendario.setSelectedDate)
        self.ui.calendario.setSelectedDate(self.ui.Fecha.date())
        self.ui.calendario.clicked.connect(self.actualizar_fecha)
        self.ui.SigVentana.clicked.connect(self.abrir_sesiones)
        
        # Ocultar la columna de las semanas en el calendario
        self.ui.calendario.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)

    def actualizar_fecha(self, fecha): 
        #OBJ: Actualiza la fecha en el widget Fecha
        #IN: fecha (QDate): La nueva fecha a establecer
        self.ui.Fecha.setDate(fecha)

    def abrir_sesiones(self): 
        #OBJ: Emitir la señal con la fecha seleccionada
        fecha = self.ui.Fecha.date() # "Get" la fecha del widget
        self.fecha_seleccionada.emit(fecha,[]) # Emitir la fecha y lista de sesiones vacía
