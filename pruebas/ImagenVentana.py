from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QPixmap

class ImagenVentana(QWidget):
    def __init__(self, ruta_imagen):
        super().__init__()
        self.setWindowTitle("Imagen ampliada")
        self.resize(600, 400)  # Tamaño inicial de la ventana

        layout = QVBoxLayout()
        self.setLayout(layout)

        label = QLabel()
        pixmap = QPixmap(ruta_imagen)

        if not pixmap.isNull():
            pixmap = pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            label.setPixmap(pixmap)
        else:
            label.setText("No se pudo cargar la imagen")

        layout.addWidget(label)
