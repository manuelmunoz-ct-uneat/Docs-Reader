from GUI.widget import WordVisualizer
from PySide6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget

# Necesita una (y solo una) instancia de QApplication por aplicación.
# Pase sys.argv para permitir argumentos de línea de comandos para su aplicación.
# Si sabe que no usará argumentos de línea de comandos, QApplication([]) también funciona.
app = QApplication([])

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Lector de documentos Word")
        
        wordVisualizer = WordVisualizer.WordUploadWidget()

        vLayOut = QHBoxLayout()
        vWidgetContainer = QWidget()
        vLayOut.addWidget(wordVisualizer)
        
        vWidgetContainer.setLayout(vLayOut)
        self.setCentralWidget(vWidgetContainer)

window = MainWindow()
window.showMaximized()

app.exec()