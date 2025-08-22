from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QProgressDialog, QMessageBox
from PyQt6.QtCore import Qt  # Asegúrate de tener esta importación

import configparser
import paramiko
import os
import sys

class SFTPUploader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Subir archivos por SFTP")
        self.setGeometry(200, 200, 300, 100)

        layout = QVBoxLayout()
        self.boton_subir = QPushButton("Subir archivos")
        self.boton_subir.clicked.connect(self.subir_archivos)
        layout.addWidget(self.boton_subir)

        self.setLayout(layout)

    def subir_archivos(self):
        config = configparser.ConfigParser()
        config.read('sftp_credenciales.ini')

        host = config['SFTP']['host']
        port = int(config['SFTP']['port'])
        username = config['SFTP']['username']
        password = config['SFTP']['password']
        remote_path = config['SFTP']['remote_path']
        archivos_locales = []
        archivos_2 = [1,2,3,4,5,6,7,8,9,10]  # Lista de archivos a subir

        for i in os.listdir("./PNG/pruebas_fotos"):
            if i.endswith(".png"):
                archivos_locales.append(i)
        # Subir archivos de ambas listas
        for archivo_local in archivos_locales:
            if not os.path.exists(f"./PNG/pruebas_fotos/{archivo_local}"):
                print("Archivo no encontrado", f"No existe: {archivo_local}")
                continue
        archivos_locales = ['103698_satellite_icon.png', '11783899_laser_sword_saber_science_fiction_icon.png', '23010_laser_icon.png', 'Captura de pantalla 2025-07-15 111600.png', 'espadas.png']
        total = len(archivos_locales) + len(archivos_2)
        print(f"Total de archivos a subir: {total}")
        # Barra de progreso emergente
        progreso = QProgressDialog("Subiendo archivos...", "Cancelar", 0, total, self)
        progreso.setWindowTitle("Progreso de subida")
        progreso.setWindowModality(Qt.WindowModality.ApplicationModal)
        progreso.setAutoClose(True)

        try:
            transport = paramiko.Transport((host, port))
            transport.connect(username=username, password=password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            i = 0
            for archivo_local in archivos_locales:
                if progreso.wasCanceled():
                    break
                
                nombre_archivo = os.path.basename(archivo_local)
                ruta_remota = os.path.join(remote_path, nombre_archivo)

                sftp.put(f"./PNG/pruebas_fotos/{archivo_local}", ruta_remota)
                i += 1
                progreso.setValue(i)
                progreso.setLabelText(f"Subiendo: {nombre_archivo}, {i} de {total}")

            sftp.close()
            transport.close()
        except Exception as e:
            print(f"Error general: {e}")
        progreso.close()
        QMessageBox.information(self, "Éxito", "Todos los archivos fueron subidos correctamente")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = SFTPUploader()
    ventana.show()
    sys.exit(app.exec())
