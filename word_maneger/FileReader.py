from docx import Document
from docx.text.paragraph import Paragraph
from docx.table import Table

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
        if self.document is None:
            raise ValueError("No hay documento cargado")
    
        data = self.document.iter_inner_content()
        for elem in data:
            if isinstance(elem, Paragraph):
                if elem.text:
                    print(f"Paragraph: {elem.text}")
            elif isinstance(elem, Table):
                for row in elem.rows:
                    print(f"Table: {row.cells[0].text} -> {row.cells[1].text}")
                   
                        

