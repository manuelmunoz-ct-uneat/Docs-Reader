from widget.ButtonWidget import QuestionButtons, AnswerButtons
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QDockWidget, QPushButton
from PySide6.QtCore import Qt

# Necesita una (y solo una) instancia de QApplication por aplicación.
# Pase sys.argv para permitir argumentos de línea de comandos para su aplicación.
# Si sabe que no usará argumentos de línea de comandos, QApplication([]) también funciona.
app = QApplication([])

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")
        self.resize(750, 500)
        
        mainScreen = QWidget()
        sideBar = QVBoxLayout()
        dockArea = QDockWidget("Controls")

        questionWidget = QuestionButtons()
        answerWidget = AnswerButtons()

        sideBar.addWidget(questionWidget)
        sideBar.addWidget(answerWidget)

        mainScreen.setLayout(sideBar)

        dockArea.setWidget(mainScreen)
        dockArea.setFloating(False)

        self.setCentralWidget(QPushButton("Test"))
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dockArea)

window = MainWindow()
window.show()

# Empieza el ciclo de eventos de Qt
app.exec()