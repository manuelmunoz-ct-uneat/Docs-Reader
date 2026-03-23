from docx import Document


class FileReader():
    def __init__(self):
        pass

    def setDoc(self, doc):
        self.document = doc

    def read(self):
        f = open(self.document, 'rb')
        print(f.read())
        f.close()
            