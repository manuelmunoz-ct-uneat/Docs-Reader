from PySide6.QtWidgets import QVBoxLayout, QWidget
from buttons.Button import Button

class QuestionButtons(QWidget):
    def __init__(self):
        super().__init__()
        boxLayout = QVBoxLayout()
        button1 = Button("Question button")
        button2 = Button("Question button")
        button3 = Button("Question button")
        button4 = Button("Question button")
        button5 = Button("Question button")
        boxLayout.addWidget(button1)
        boxLayout.addWidget(button2)
        boxLayout.addWidget(button3)
        boxLayout.addWidget(button4)
        boxLayout.addWidget(button5)

        self.setLayout(boxLayout)

class AnswerButtons(QWidget):
    def __init__(self):
        super().__init__()
        boxLayout = QVBoxLayout()
        button1 = Button("Answer button")
        button2 = Button("Answer button")
        button3 = Button("Answer button")
        button4 = Button("Answer button")
        button5 = Button("Answer button")
        boxLayout.addWidget(button1)
        boxLayout.addWidget(button2)
        boxLayout.addWidget(button3)
        boxLayout.addWidget(button4)
        boxLayout.addWidget(button5)

        self.setLayout(boxLayout)
