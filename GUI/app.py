from PySide6.QtWidgets import QApplication, QWidget

# Solamente usado para acceder a comandos de la terminal
# import sys

# Necesita una (y solo una) instancia de QApplication por aplicación.
# Pase sys.argv para permitir argumentos de línea de comandos para su aplicación.
# Si sabe que no usará argumentos de línea de comandos, QApplication([]) también funciona.
app = QApplication([])

# Crea un widget Qt, que será nuestra ventana.
window = QWidget()
window.show()  # Importante usarlo, las ventanas estan ocultas por defecto

# Start the event loop.
app.exec()