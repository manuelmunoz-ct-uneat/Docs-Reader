from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize, Qt, Signal
from styles.Funiber import FuniberColors

class Button(QPushButton):
    def __init__(self, text: str = "", btn_id: str = "", styles: str = FuniberColors.styles, icon_path: str | None = None, parent=None):
        super().__init__(text, parent)
        self._id = btn_id

        # Opciones visuales básicas
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(100, 50)
        self.setIconSize(QSize(100, 50))

        if icon_path:
            self.setIcon(QIcon(icon_path))

        # Estilos: modifica según tu tema
        self.setStyleSheet(styles)

        # Conectar la señal de clicked para reenviarla con información
        self.clicked.connect(self._on_clicked)

    def _on_clicked(self):
        # Emitimos la señal personalizada con el id (puedes enviar cualquier dato)
        print(self._id)
        clicked_with_id = Signal(int)

    # Ejemplo de método auxiliar para cambiar icono después
    def set_icon(self, icon_path: str, size: QSize | None = None):
        self.setIcon(QIcon(icon_path))
        if size:
            self.setIconSize(size)

    # Propiedad lectura para el id
    @property
    def id(self):
        return self._id
