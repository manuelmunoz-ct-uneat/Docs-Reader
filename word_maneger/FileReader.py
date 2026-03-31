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

        # iter_all_blocks ahora devuelve (elem, origen)
        for elem, origen in self.iter_all_blocks(self.document):

            if isinstance(elem, Table):
                for row in elem.rows:
                    text = row.cells[0].text

                numPr = elem._element.xpath("./w:pPr/w:numPr")
                self.setData(numPr, data, idx, text, origen if origen else "tabla")
                idx += 1
            else:
                text = elem.text.strip()
                if not text:
                    continue

                numPr = elem._element.xpath("./w:pPr/w:numPr")
                self.setData(numPr, data, idx, text, origen if origen else "parrafo")
                idx += 1

        return data

    def parse_to_json(self):
        data = self.read_paragraphs()

        resultado = {}
        num_pregunta = 0
        pregunta_actual = None
        pregunta_lista_id = None   # lista_id de la pregunta actual
        opcion_actual = None

        for _, item in data.items():
            texto    = item["texto"]
            nivel    = item["nivel"]
            lista_id = item.get("lista_id")
            origen   = item.get("origen", "parrafo")

            # ── FIX 1: items de header/footer con nivel=0 son opciones,
            #           no preguntas nuevas, si ya hay una pregunta activa.
            es_de_cabecera = origen.startswith("header") or origen.startswith("footer")
            if es_de_cabecera and nivel == 0 and pregunta_actual is not None:
                nivel = 1

            # ── FIX 2: item con nivel=0 pero lista_id distinto al de la pregunta
            #           actual → Word rompió el formato al cruzar de página;
            #           reinterpretarlo como opción (nivel=1).
            if (nivel == 0
                    and pregunta_actual is not None
                    and lista_id is not None
                    and pregunta_lista_id is not None
                    and lista_id != pregunta_lista_id):
                nivel = 1

            # Nivel 0 → nueva pregunta
            if nivel == 0:
                num_pregunta += 1
                resultado[num_pregunta] = {
                    "preg":  texto,
                    "val":   None,
                    "multi": False,
                    "tipo":  None,
                    "ops":   {}
                }
                pregunta_actual  = resultado[num_pregunta]
                pregunta_lista_id = lista_id   # guardar lista_id de esta pregunta
                opcion_actual    = None
                continue

            # Nivel 1 → opción
            if nivel == 1 and pregunta_actual is not None:
                n = len(pregunta_actual["ops"])
                letra = chr(ord("a") + n)

                # ── Detectar feedback inline: "Texto de opción. CORRECTA."
                ok_val, texto_limpio = self.parse_inline_feedback(texto)

                pregunta_actual["ops"][letra] = {
                    "txt": texto_limpio,
                    "ok":  ok_val
                }
                # Solo actualizar opcion_actual si no tiene ya feedback inline
                if ok_val is None:
                    opcion_actual = letra
                else:
                    opcion_actual = None  # feedback ya consumido, no esperar párrafo siguiente
                continue

            # Sin nivel → retroalimentación (CORRECTA / INCORRECTA / VERDADERA / FALSA)
            if nivel is None and pregunta_actual is not None and opcion_actual is not None:
                t = texto.rstrip(".")
                if t in ("CORRECTA", "VERDADERA"):
                    pregunta_actual["ops"][opcion_actual]["ok"] = True
                elif t in ("INCORRECTA", "FALSA"):
                    pregunta_actual["ops"][opcion_actual]["ok"] = False

        # Inferencia de multi-respuesta
        for bloque in resultado.values():
            correctas = sum(1 for op in bloque["ops"].values() if op["ok"] is True)
            bloque["multi"] = correctas > 1 if bloque["ops"] else False

        return resultado


    def parse_inline_feedback(self, texto: str):
        PALABRAS_OK    = {"CORRECTA", "VERDADERA"}
        PALABRAS_NOK   = {"INCORRECTA", "FALSA"}
        TODAS          = PALABRAS_OK | PALABRAS_NOK

        # Separar la última "palabra" del texto (ignorando puntos finales)
        partes = texto.rstrip().rstrip(".")
        tokens = partes.split()
        if not tokens:
            return None, texto

        ultima = tokens[-1].upper()
        if ultima in TODAS:
            texto_limpio = " ".join(tokens[:-1]).rstrip(" .") + "."
            ok = True if ultima in PALABRAS_OK else False
            return ok, texto_limpio

        return None, texto

    # ──────────────────────────────────────────────────────────────────────
    # iter_block_items: ahora recibe y propaga el origen
    # ──────────────────────────────────────────────────────────────────────
    def iter_block_items(self, parent, origen="parrafo"):

        # DOCUMENTO (body)
        if isinstance(parent, DocxDocument):
            parent_elm = parent.element.body

        # CELDA DE TABLA
        elif isinstance(parent, _Cell):
            parent_elm = parent._tc

        # HEADER / FOOTER
        elif isinstance(parent, (_Header, _Footer)):
            # Si está vinculado a la sección anterior, su XML está vacío
            if parent.is_linked_to_previous:
                return

            parent_elm = parent._element
            for child in parent_elm.iterchildren():
                if child.tag.endswith('}p'):
                    yield Paragraph(child, parent), origen
                elif child.tag.endswith('}tbl'):
                    table = Table(child, parent)
                    yield table, origen
                    for row in table.rows:
                        for cell in row.cells:
                            yield from self.iter_block_items(cell, origen)
            return

        else:
            return

        # BODY / CELDA: párrafos y tablas en orden de documento
        for child in parent_elm.iterchildren():
            if child.tag.endswith('}p'):
                yield Paragraph(child, parent), origen

            elif child.tag.endswith('}tbl'):
                table = Table(child, parent)
                yield table, origen

                for row in table.rows:
                    for cell in row.cells:
                        yield from self.iter_block_items(cell, origen)

    # ──────────────────────────────────────────────────────────────────────
    # iter_all_blocks: propaga origen diferenciado para header/footer
    # ──────────────────────────────────────────────────────────────────────
    def iter_all_blocks(self, document):
        # BODY
        yield from self.iter_block_items(document, origen="parrafo")

        # HEADERS Y FOOTERS (por sección)
        for i, section in enumerate(document.sections):
            yield from self.iter_block_items(section.header, origen=f"header_{i}")
            yield from self.iter_block_items(section.footer, origen=f"footer_{i}")

            # Primera página diferente (portada, etc.)
            if section.different_first_page_header_footer:
                yield from self.iter_block_items(
                    section.first_page_header, origen=f"header_first_{i}"
                )
                yield from self.iter_block_items(
                    section.first_page_footer, origen=f"footer_first_{i}"
                )

    # ──────────────────────────────────────────────────────────────────────
    # setData: sin cambios de lógica, acepta origen externo
    # ──────────────────────────────────────────────────────────────────────
    def setData(self, numPr: list, data: dict, idx: int, text: str, origen: str):
        if numPr:
            ilvl_nodes  = numPr[0].xpath("./w:ilvl")
            numId_nodes = numPr[0].xpath("./w:numId")

            nivel    = int(ilvl_nodes[0].get(
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val"
            ))
            lista_id = int(numId_nodes[0].get(
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val"
            ))
        else:
            nivel    = None
            lista_id = None

        data[idx] = {
            "texto":    text,
            "nivel":    nivel,
            "lista_id": lista_id,
            "origen":   origen
        }
