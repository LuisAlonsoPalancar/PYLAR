"""
----------------------------------
Nombre del archivo:     ClickableLabel.py
Descripción:            Este script define un QLabel que muestra una imagen
                        y permite hacer clic en ella para ampliarla.

Entrada(s):             
Salida(s):              Muestra la imagen ampliada en un diálogo.
Dependencias:           PyQt6 (V 6.4.2)
Autor:                  Luis Alonso Palancar
Fecha:                  Julio 2025
----------------------------------
"""
from PyQt6.QtWidgets import QLabel, QDialog, QVBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class ClickableLabel(QLabel):
    def __init__(self, ruta_imagen, parent=None):
        super().__init__(parent)
        self.ruta_imagen = ruta_imagen

    def mousePressEvent(self, event): 
        #OBJ: Mostrar imagen ampliada al hacer clic
        self.mostrar_imagen_ampliada()

    def mostrar_imagen_ampliada(self):
        #OBJ: Mostrar imagen ampliada en un diálogo

        dialogo = QDialog(self)
        dialogo.setWindowTitle("Imagen ampliada")
        layout = QVBoxLayout(dialogo)

        label = QLabel()
        pixmap = QPixmap(self.ruta_imagen)

        if not pixmap.isNull():
            label.setPixmap(pixmap.scaledToWidth(800, Qt.TransformationMode.SmoothTransformation))
        else:
            label.setText("Imagen no disponible")

        layout.addWidget(label)
        dialogo.resize(820, 600)
        dialogo.show()
