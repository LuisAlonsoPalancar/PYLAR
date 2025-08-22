import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout

# Clase principal de la ventana
class MiVentana(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mi primera app con PyQt5")
        self.setGeometry(100, 100, 300, 200)

        # Crear widgets
        self.label = QLabel("Hola, PyQt5!", self)
        self.boton = QPushButton("Haz clic", self)
        self.boton.clicked.connect(self.cambiar_texto)

        # Layout (organiza los widgets verticalmente)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.boton)
        self.setLayout(layout)

    def cambiar_texto(self):
        self.label.setText("¡Has hecho clic!")

# Ejecutar la app
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = MiVentana()
    ventana.show()
    sys.exit(app.exec())
