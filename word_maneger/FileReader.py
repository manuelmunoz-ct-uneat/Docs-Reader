from docx import Document
from docx.table import Table, _Cell
from docx.section import _Header, _Footer
from docx.text.paragraph import Paragraph
from docx.document import Document as DocxDocument

class FileReader:
    def __init__(self, doc_path=None):
        self.doc_path = doc_path
        self.document = None

        if doc_path:
            self.load(doc_path)

    def load(self, doc_path):
        self.document = Document(doc_path)
    
    def read_paragraphs(self):

        data = {}
        idx = 0

        for elem in self.iter_all_blocks(self.document):

            if isinstance(elem, Table):
                for row in elem.rows:
                    text = row.cells[0].text

                numPr = elem._element.xpath("./w:pPr/w:numPr")
                self.setData(numPr, data, idx, text, "tabla")
                idx += 1
            else:
                text = elem.text.strip()
                if not text:
                    continue
                print(text)
                seen = set()
                text = elem.text.strip()

                if not text or text in seen:
                    continue

                seen.add(text)

                numPr = elem._element.xpath("./w:pPr/w:numPr")
                
                self.setData(numPr, data, idx, text, "parrafo")

                idx += 1


        return data


    def parse_to_json(self):
        data = self.read_paragraphs()

        resultado = {}
        num_pregunta = 0
        pregunta_actual = None
        opcion_actual = None

        for _, item in data.items():
            texto = item["texto"]
            nivel = item["nivel"]

            # Nivel 0 -> nueva pregunta
            if nivel == 0:
                num_pregunta += 1
                resultado[num_pregunta] = {
                    "preg": texto,      # texto de la pregunta
                    "val": None,        # aquí luego metes el valor si lo extraes
                    "multi": False,      # True/False/None
                    "tipo": None,       # aquí pones tu enum luego
                    "ops": {}           # opciones
                }
                pregunta_actual = resultado[num_pregunta]
                opcion_actual = None
                continue

            # Nivel 1 -> opción
            if nivel == 1 and pregunta_actual is not None:
                letra = chr(ord("a")) if len(pregunta_actual["ops"]) == 0 else chr(ord("a") + len(pregunta_actual["ops"]))

                pregunta_actual["ops"][letra] = {
                    "txt": texto,
                    "ok": None
                }
                opcion_actual = letra
                continue

            # Sin nivel -> retroalimentación
            if nivel is None and pregunta_actual is not None and opcion_actual is not None:
                if texto in ("CORRECTA.", "CORRECTA", "VERDADERA", "VERDADERA."):
                    pregunta_actual["ops"][opcion_actual]["ok"] = True
                elif texto in ("INCORRECTA.", "INCORRECTA", "FALSA", "FALSA."):
                    pregunta_actual["ops"][opcion_actual]["ok"] = False

        # Inferencia opcional de multi
        for bloque in resultado.values():
            correctas = sum(1 for op in bloque["ops"].values() if op["ok"] is True)
            bloque["multi"] = correctas > 1 if bloque["ops"] else False

        # print(resultado)
        return resultado
    
    def iter_block_items(self, parent):
        # DOCUMENTO
        if isinstance(parent, DocxDocument):
            parent_elm = parent.element.body

        # CELDA DE TABLA
        elif isinstance(parent, _Cell):
            parent_elm = parent._tc

        # HEADER / FOOTER -> solo párrafos
        elif isinstance(parent, (_Header, _Footer)):
            for paragraph in parent.paragraphs:
                yield paragraph
            return

        else:
            return

        # BODY / CELDA: párrafos y tablas
        for child in parent_elm.iterchildren():
            if child.tag.endswith('}p'):
                yield Paragraph(child, parent)

            elif child.tag.endswith('}tbl'):
                table = Table(child, parent)
                yield table

                for row in table.rows:
                    for cell in row.cells:
                        yield from self.iter_block_items(cell)


    def iter_all_blocks(self, document):
        # BODY
        yield from self.iter_block_items(document)

        # HEADERS Y FOOTERS
        for section in document.sections:
            yield from self.iter_block_items(section.header)
            yield from self.iter_block_items(section.footer)

    def setData(self, numPr: list, data: dict, idx: int, text: str, origen: str):
        if numPr:
            ilvl_nodes = numPr[0].xpath("./w:ilvl")
            numId_nodes = numPr[0].xpath("./w:numId")

            nivel = int(ilvl_nodes[0].get(
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val"
            ))
            lista_id = int(numId_nodes[0].get(
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val"
            ))
        else:
            nivel = None
            lista_id = None

        data[idx] = {
            "texto": text,
            "nivel": nivel,
            "lista_id": lista_id,
            "origen": origen
        }
                                            

