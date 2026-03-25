from docx import Document
from docx.text.paragraph import Paragraph
from docx.table import Table
import json

class FileReader:
    def __init__(self, doc_path=None):
        self.doc_path = doc_path
        self.document = None

        if doc_path:
            self.load(doc_path)

    def setDoc(self, doc_path):
        self.doc_path = doc_path
        self.load(doc_path)

    def load(self, doc_path):
        self.document = Document(doc_path)

    def getDocument(self):
        return self.document

    def read_paragraphs(self):
        questionSet = {}
        if self.document is None:
            raise ValueError("No hay documento cargado")
    
        data = self.document.iter_inner_content()
        for elem in data:
            if isinstance(elem, Paragraph):
                for run in elem.runs:
                    if elem.text and elem:
                        color = run.font.color.rgb
                        questionSet[f"{elem.text}"] = f"{color}"
            elif isinstance(elem, Table):
                for row in elem.rows:
                    questionSet[f"{row.cells[0].text}"] = f"{row.cells[1].text}"
        
        return json.dumps(questionSet, ensure_ascii=False)
                                         

