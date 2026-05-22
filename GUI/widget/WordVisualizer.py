from pathlib import Path

from PySide6.QtWidgets import (QWidget, QPushButton, QComboBox, QFileDialog, QVBoxLayout)
from word_maneger.FileReader import FileReader
from GUI.components.TextBox import JsonFormater
from Dtos_Mapper.Mapper import Mapper
from xml_parser.XmlParser import XmlParser

class WordUploadWidget(QWidget):
    FILE_FILTER = 'Word file (*.doc *.docx)'
    dtoData = []
    courseInfo = json = ""
    def __init__(self):
        super().__init__()
        self.window_width, self.window_height = 400, 100
        self.setMinimumSize(self.window_width, self.window_height)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.options = ('Open file',  'Save file')

        self.combo = QComboBox()
        self.combo.addItems(self.options)
        layout.addWidget(self.combo)

        btn = QPushButton('Launch')
        btn.clicked.connect(self.launchDialog)
        layout.addWidget(btn)

        self.textbox = JsonFormater()
        layout.addWidget(self.textbox)
    

    def launchDialog(self):
            option = self.options.index(self.combo.currentText())
            if option == 0:
                self.getFileName()
                document = FileReader(self.courseInfo)
                self.json = document.parse_to_json()
                self.textbox.setJson(self.json)
            elif option == 1:
                dtoData = Mapper.tipoPregunta(self.courseInfo, self.json)
                xmlInfo = XmlParser.parse(dtoData)
                self.saveFile(xmlInfo)
            else:
                print('Got Nothing')

    def getFileName(self):

        response, _ = QFileDialog.getOpenFileName(
            self,
            'Select a file',
            "",
            filter=self.FILE_FILTER,
        )

        if response:
            self.courseInfo = response or self.courseInfo
        

    def saveFile(self, infoXml):

        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar",
            "",
            "Xml (*.xml)"
        )

        if ruta:

            with open(ruta, "w", encoding="utf-8") as f:
                f.write(infoXml)
