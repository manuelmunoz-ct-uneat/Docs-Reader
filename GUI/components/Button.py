from PySide6.QtWidgets import QPushButton
from GUI.styles.Funiber import FuniberColors

class Button(QPushButton):
    def __init__(self, text: str = "", styles: str = FuniberColors.styles):
        super().__init__(text)
        
        self.setStyleSheet(styles)

