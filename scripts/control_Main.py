"""
----------------------------------
Nombre del archivo:     control_Main.py
Descripción:            Este script controla la ventana principal de la aplicación, 
                        gestionando la interacción con el calendario, las sesiones y los pases.

Entrada(s):             
Salida(s):              Muestra la ventana principal de la aplicación y llama a las ventanas secundarias.
Dependencias:           PyQt6 (V 6.4.2)
Autor:                  Luis Alonso Palancar
Fecha:                  Julio 2025
----------------------------------
"""

import re
import sys
import os
import subprocess

from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtCore import QDate
from PyQt6.QtGui import QIcon

from scripts.control_Calendario import MainWindow as controlCalendarWindow # Control Ventana Calendario
from scripts.control_Satelites import SatelitesWindow as controlSatelitesWindow # Control Ventana de Pases
from scripts.control_Sesiones import SesionesWindow as controlSesionesWindow # Control Ventana de Sesiones

from vistas.Window_Main_ui import Ui_MainWindow  # Ventana Principal

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()  # Crear una instancia de la clase Ui_MainWindow
        self.ui.setupUi(self)  # Configurar la interfaz de usuario

        # Variables de la ventana principal
        self.fecha = QDate.currentDate()  # Variable de la fecha seleccionada, inicialmente la fecha actual
        self.sesiones = []  # Lista de sesiones seleccionadas

        # Asociar acciones a los botones
        self.ui.BotonCalendario.clicked.connect(lambda: self.abrir_calendario(self.fecha))  # Botón para abrir el calendario
        self.ui.BotonPases.clicked.connect(self.abrir_satelites)
        self.ui.BotonSesiones.clicked.connect(self.abrir_sesiones)
        self.ui.BotonCerrar.clicked.connect(sys.exit)  # Conectar el botón de cerrar a la función close
        self.ui.BotonProcesado.clicked.connect(self.procesar_pases_export)

        # Abrir la ventana de calendario al iniciar la aplicación
        self.abrir_calendario()

    def procesar_pases_export(self):
        #OBJ: Mover los ficheros de los pases en Export a la carpeta de sesion que corresponda y llamar a NPgo
        #PRE: Comprobar que existen los archivos necesarios y que la ruta de destino es válida
        #POST: Los archivos se han movido y NPgo ha sido llamado

        ruta_export = f"/opt/scope/data/export/"
        # Comprobar los archivos .frd que hay en la ruta_export
        archivos_frd = [f for f in os.listdir(ruta_export) if f.lower().endswith('.frd')]
        archivos_cpf = [f for f in os.listdir(ruta_export) if f.lower().endswith('.cpf')]

        print("Archivos .frd encontrados:", archivos_frd)
        print("Archivos .cpf encontrados:", archivos_cpf)

        if archivos_frd and archivos_cpf:
            
            try:
                fecha_str = self.fecha.toString("yyyyMMdd")
                sesion_dia_actual = f"{ruta_export}/processing/Sessions_{fecha_str}"
                print("Ruta de la sesión del día:", sesion_dia_actual)

                if os.path.exists(sesion_dia_actual):
                    # Existe la sesión del día actual
                    # Buscar la sesión con índice más alto y crear una nueva

                    sesiones_path = sesion_dia_actual #Sesion de la fecha del procesado
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
                        last_session_num = 0

                    ruta_destino = f"{sesion_dia_actual}/Session{last_session_num+1:02d}"

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
                else:
                    ruta_destino = f"{sesion_dia_actual}/Session01"
                    last_session_num = 0
                    print("No existe el directorio de la sesión del día actual.")
                    print(f"Creando la estructura de carpetas en {ruta_destino}...")
                    os.makedirs(ruta_destino, exist_ok=True)
                    # Crear las subcarpetas requeridas dentro de la nueva sesión
                    subcarpetas = ["RAW", "CPF", "FRD", "FRDv1", "NPT", "NPTv1", "PNG"]
                    for carpeta in subcarpetas:
                        os.makedirs(os.path.join(ruta_destino, carpeta), exist_ok=True)
                try:

                    for frd in archivos_frd:
                        # Mover el archivo .frd a la carpeta RAW de la nueva sesión
                        src_frd = os.path.join(ruta_export, frd)
                        dst_frd = os.path.join(ruta_destino, "/RAW/", frd)
                        print(f"Moviendo {frd} a {dst_frd}...")
                        os.rename(src_frd, dst_frd)
                    for cpf in archivos_cpf:
                        src_cpf = os.path.join(ruta_export, cpf)
                        dst_cpf = os.path.join(ruta_destino, "/CPF/", cpf)
                        print(f"Moviendo {cpf} a {dst_cpf}...")
                        os.rename(src_cpf, dst_cpf)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"No se puede procesar los pases. \nError al mover los archivos: {e}")
                    return
                try:
                    script_path = "/opt/scope/bin/processing/npgo-auto-run.sh"
                    ruta_config = "/opt/scope/bin/processing/config_processing.ini"
                    ruta_sesion_comando = f"{ruta_destino}"  # Ruta de la sesión
                    comando = [script_path, ruta_config, ruta_sesion_comando, str(last_session_num+1)]
                    # Ejecutar el comando en segundo plano, sin bloquear la interfaz
                    subprocess.Popen(comando)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error al llamar a NPgo: {e}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Al crear la carpeta de sesion: {e}")
        else:
            QMessageBox.information(self, "Archivos no encontrados", "No se encontraron archivos .frd o .cpf en la carpeta.")

    def abrir_calendario(self, fecha_input=None):
        #OBJ: Abre la ventana de Calendario en el Frame de contenido
        #POST: Establece la fecha actual y la lista de sesiones vacía
        #IN: fecha_input (QDate): La fecha seleccionada

        self.fecha = fecha_input if fecha_input else QDate.currentDate()  # Actualiza la fecha si se proporciona una nueva
        self.contenidoFrame = controlCalendarWindow(self.fecha)
        self.contenidoFrame.fecha_seleccionada.connect(self.abrir_sesiones)  # Conectar la señal que vuelve con la fecha seleccionada
        
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
        #IN: fecha_input(QDate): Fecha seleccionada. sesiones_input(list): Lista de sesiones seleccionadas.

        self.fecha = fecha_input if fecha_input else self.fecha  # Actualiza la fecha si se proporciona una nueva
        self.sesiones = sesiones_input if sesiones_input != None else self.sesiones  # Actualiza las sesiones si se proporciona una nueva
        
        # Abre la ventana de Sesiones
        self.contenidoFrame = controlSesionesWindow(self.fecha, self.sesiones)
        self.contenidoFrame.sesiones_seleccionadas.connect(self.abrir_satelites)  # Conectar la señal que vuelve con la lista de sesiones seleccionadas
        
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
        #IN: sesiones_input(list): Lista de sesiones seleccionadas.

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
        #IN: sesiones_nuevas(list): Lista de sesiones seleccionadas.
        self.sesiones = sesiones_nuevas

def main():
        app = QApplication(sys.argv)
        app.setWindowIcon(QIcon(os.path.dirname(os.path.dirname(__file__)) + "/vistas/logos/Logo YLARA.png"))  # Icono del programa
        window = MainWindow()
        window.showMaximized()
        sys.exit(app.exec())
