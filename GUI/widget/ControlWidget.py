from .ButtonWidget import QuestionButtons, AnswerButtons
from PySide6.QtWidgets import QWidget, QDockWidget, QVBoxLayout
from PySide6.QtCore import Qt


class ControlWidget(QDockWidget):
    def __init__(self, title: str = ""):
        super().__init__(title)

        controlContainer = QWidget()
        sideBar = QVBoxLayout()
        questionWidget = QuestionButtons()
        answerWidget = AnswerButtons()

        sideBar.addWidget(questionWidget)
        sideBar.addWidget(answerWidget)

        controlContainer.setLayout(sideBar)

        self.setWidget(controlContainer)
        self.setFloating(False)

        



