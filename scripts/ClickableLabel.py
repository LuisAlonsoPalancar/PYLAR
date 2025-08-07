from PyQt6.QtWidgets import QLabel, QDialog, QVBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class ClickableLabel(QLabel):
    def __init__(self, ruta_imagen, parent=None):
        super().__init__(parent)
        self.ruta_imagen = ruta_imagen

    def mousePressEvent(self, event):
        self.mostrar_imagen_ampliada()

    def mostrar_imagen_ampliada(self):
        # Crear un diálogo sin asignar self como padre
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
