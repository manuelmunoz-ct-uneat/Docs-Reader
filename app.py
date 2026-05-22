from GUI.widget import ControlWidget, WordVisualizer
from PySide6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget

# Necesita una (y solo una) instancia de QApplication por aplicación.
# Pase sys.argv para permitir argumentos de línea de comandos para su aplicación.
# Si sabe que no usará argumentos de línea de comandos, QApplication([]) también funciona.
app = QApplication([])

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Lector de documentos Word")
        
        # controlPanel1 = ControlWidget.ControlWidget("Controles")
        # controlPanel2 = ControlWidget.ControlWidget("Visualizador")
        wordVisualizer = WordVisualizer.WordUploadWidget()

        vLayOut = QHBoxLayout()
        vWidgetContainer = QWidget()
        vLayOut.addWidget(wordVisualizer)
        
        vWidgetContainer.setLayout(vLayOut)
        self.setCentralWidget(vWidgetContainer)
        # self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, controlPanel1)
        # self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, controlPanel2)

window = MainWindow()
window.showMaximized()

# Empieza el ciclo de eventos de Qt
app.exec()