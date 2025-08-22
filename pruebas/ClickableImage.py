from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import pyqtSignal

class ClickableImage(QLabel):
    clicked = pyqtSignal(str)  # Emitirá la ruta de la imagen

    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path

    def mousePressEvent(self, event):
        self.clicked.emit(self.image_path)
