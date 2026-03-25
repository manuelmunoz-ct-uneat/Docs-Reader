import os
from PySide6.QtWidgets import (QApplication, QWidget, QPushButton, QTextEdit, QComboBox, QFileDialog, QHBoxLayout, QVBoxLayout)
from word_maneger.FileReader import FileReader

class WordUploadWidget(QWidget):
    FILE_FILTER = 'Word file (*.doc *.docx)'

    def __init__(self):
        super().__init__()
        self.window_width, self.window_height = 400, 100
        self.setMinimumSize(self.window_width, self.window_height)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.options = ('Open file')

        self.combo = QComboBox()
        self.combo.addItems(self.options)
        layout.addWidget(self.combo)

        btn = QPushButton('Launch')
        btn.clicked.connect(self.launchDialog)
        layout.addWidget(btn)

        self.textbox = QTextEdit() # Cambiar a un visualizador del texto de word despues de que se abre
        layout.addWidget(self.textbox)
    

    def launchDialog(self):
            option = self.options.index(self.combo.currentText())

            if option == 0:
                fileLocation = self.getFileName()
                document = FileReader(fileLocation)
                paragraph = document.read_paragraphs()
                response =  paragraph
                self.textbox.append(response)
            else:
                print('Got Nothing')

    def getFileName(self):

        response = QFileDialog.getOpenFileName(
            self,
            'Select a file',
            "",
            filter=self.FILE_FILTER,
        )
        return str(response[0])
