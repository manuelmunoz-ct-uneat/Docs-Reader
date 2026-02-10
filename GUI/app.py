from widget.ButtonWidget import QuestionButtons, AnswerButtons
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QDockWidget, QPushButton
from PySide6.QtCore import Qt
from widget.ControlWidget import ControlWidget

# Necesita una (y solo una) instancia de QApplication por aplicación.
# Pase sys.argv para permitir argumentos de línea de comandos para su aplicación.
# Si sabe que no usará argumentos de línea de comandos, QApplication([]) también funciona.
app = QApplication([])

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Lector de documentos Word")
        
        controlPanel = ControlWidget()

        self.setCentralWidget(QPushButton("Test"))
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, controlPanel)

window = MainWindow()
window.showMaximized()

# Empieza el ciclo de eventos de Qt
app.exec()