from docx import Document


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

        return [p.text for p in self.document.paragraphs]
            