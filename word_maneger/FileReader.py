import zipfile
import re as _re
import os
import json
from lxml import etree

from docx import Document
from docx.table import Table, _Cell
from docx.text.paragraph import Paragraph
from docx.document import Document as DocxDocument

# Namespaces
W   = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
WPS = "http://schemas.microsoft.com/office/word/2010/wordprocessingShape"

W_P      = f"{{{W}}}p"
W_TBL    = f"{{{W}}}tbl"
W_TC     = f"{{{W}}}tc"
W_T      = f"{{{W}}}t"
W_SECT   = f"{{{W}}}sectPr"
W_NUMPR  = f"{{{W}}}numPr"
W_ILVL   = f"{{{W}}}ilvl"
W_NUMID  = f"{{{W}}}numId"
W_VAL    = f"{{{W}}}val"
W_HREF   = f"{{{W}}}headerReference"
W_TYPE   = f"{{{W}}}type"
R_ID     = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
TXBX_TAG = f"{{{WPS}}}txbx"
TXBC_TAG = f"{{{W}}}txbxContent"


class _RawPara:
    """
    Wrapper minimo para parrafos de text-boxes en headers (arboles lxml externos).
    Expone .text y ._element para que read_paragraphs pueda tratarlo igual
    que un Paragraph de python-docx.
    """
    def __init__(self, elem):
        self._element = elem
        self.text = "".join(t.text or "" for t in elem.iter(W_T))


class FileReader:
    def __init__(self, doc_path: os.PathLike):
        self.doc_path = doc_path
        self.document = None
        self._hdr_map = {}      # rId -> [_RawPara, ...]

        if doc_path:
            self.load(doc_path)

    def load(self, doc_path):
        self.doc_path  = doc_path
        self.document  = Document(doc_path)
        self._hdr_map  = self._build_header_map()

    # ------------------------------------------------------------------
    # _build_header_map
    # Lee todos los headerN.xml del ZIP y extrae el texto de los
    # text-boxes flotantes (wps:txbx).  Devuelve  rId -> [_RawPara]
    # ------------------------------------------------------------------
    def _build_header_map(self):
        hdr_map = {}
        with zipfile.ZipFile(self.doc_path) as z:
            rels_raw = z.read("word/_rels/document.xml.rels").decode("utf-8")
            rid_to_file = {}
            for m in _re.finditer(
                r'Id="(rId\d+)"[^>]*Target="(header\d+\.xml)"', rels_raw
            ):
                rid_to_file[m.group(1)] = m.group(2)

            for rid, fname in rid_to_file.items():
                root  = etree.fromstring(z.read(f"word/{fname}"))
                paras = []
                for txbx in root.iter(TXBX_TAG):
                    for txbc in txbx.iter(TXBC_TAG):
                        for child in txbc:
                            if child.tag == W_P:
                                paras.append(_RawPara(child))
                            elif child.tag == W_TBL:
                                for tc in child.iter(W_TC):
                                    for p in tc.iter(W_P):
                                        paras.append(_RawPara(p))
                if paras:
                    hdr_map[rid] = paras
        return hdr_map

    # ------------------------------------------------------------------
    # read_paragraphs
    # ------------------------------------------------------------------
    def read_paragraphs(self):
        data = {}
        idx  = 0

        for elem, origen in self.iter_all_blocks(self.document):
            if isinstance(elem, Table):
                text = ""
                for row in elem.rows:
                    text = row.cells[0].text
                numPr = elem._element.xpath("./w:pPr/w:numPr")
                self.setData(numPr, data, idx, text, origen or "tabla")
                idx += 1

            elif isinstance(elem, _RawPara):
                text = elem.text.strip()
                if not text:
                    continue
                numPr_nodes = elem._element.findall(f".//{W_NUMPR}")
                self._setData_raw(numPr_nodes, data, idx, text, origen or "parrafo")
                idx += 1

            else:  # Paragraph
                text = (elem.text or "").strip()
                if not text:
                    continue
                numPr = elem._element.xpath("./w:pPr/w:numPr")
                self.setData(numPr, data, idx, text, origen or "parrafo")
                idx += 1

        return data

    # ------------------------------------------------------------------
    # parse_to_json
    # ------------------------------------------------------------------
    def parse_to_json(self):
        data = self.read_paragraphs()

        resultado       = {}
        num_pregunta    = 0
        pregunta_actual = None
        pregunta_lista  = None
        opcion_actual   = None

        for _, item in data.items():
            texto    = item["texto"]
            nivel    = item["nivel"]
            lista_id = item.get("lista_id")
            origen   = item.get("origen", "parrafo")

            # FIX 1: opcion que llego por header
            # Caso A: tiene nivel=0 en header  → opcion
            # Caso B: nivel=None pero texto empieza con "a) b) c)..." hardcodeado
            if origen.startswith("header") and pregunta_actual is not None:
                if nivel == 0:
                    nivel = 1
                elif nivel is None and _re.match(r'^[a-dA-D]\)', texto.strip()):
                    nivel = 1

            # FIX 2: nivel=0 con lista_id diferente al de la pregunta activa
            #        (Word rompio numeracion al cruzar pagina)
            if (nivel == 0
                    and pregunta_actual is not None
                    and lista_id is not None
                    and pregunta_lista is not None
                    and lista_id != pregunta_lista):
                nivel = 1

            # Nueva pregunta
            if nivel == 0:
                num_pregunta += 1
                resultado[num_pregunta] = {
                    "preg":  texto,
                    "val":   None,
                    "multi": False,
                    "tipo":  None,
                    "ops":   {}
                }
                pregunta_actual = resultado[num_pregunta]
                pregunta_lista  = lista_id
                opcion_actual   = None
                continue

            # Opcion
            if nivel == 1 and pregunta_actual is not None:
                letra          = chr(ord("a") + len(pregunta_actual["ops"]))
                # Limpiar prefijo hardcodeado "a)" / "b)" que Word mete en text-boxes
                texto_sin_pref = _re.sub(r'^[a-dA-D]\)\s*', '', texto).strip()
                ok_val, limpio = self._parse_inline_feedback(texto_sin_pref)
                pregunta_actual["ops"][letra] = {"txt": limpio, "ok": ok_val}
                opcion_actual = None if ok_val is not None else letra
                continue

            # Feedback en parrafo separado
            if nivel is None and pregunta_actual is not None and opcion_actual is not None:
                t = texto.rstrip(".")
                if t in ("CORRECTA", "VERDADERA"):
                    pregunta_actual["ops"][opcion_actual]["ok"] = True
                elif t in ("INCORRECTA", "FALSA"):
                    pregunta_actual["ops"][opcion_actual]["ok"] = False

        for bloque in resultado.values():
            correctas = sum(1 for op in bloque["ops"].values() if op["ok"] is True)
            bloque["multi"] = correctas > 1 if bloque["ops"] else False

        print(json.dumps(resultado, indent=4, ensure_ascii=False))
        return resultado

    # ------------------------------------------------------------------
    # _parse_inline_feedback
    # ------------------------------------------------------------------
    @staticmethod
    def _parse_inline_feedback(texto: str):
        OK  = {"CORRECTA", "VERDADERA"}
        NOK = {"INCORRECTA", "FALSA"}
        tokens = texto.rstrip().rstrip(".").split()
        if not tokens:
            return None, texto
        ultima = tokens[-1].upper()
        if ultima in OK | NOK:
            limpio = " ".join(tokens[:-1]).rstrip(" .") + "."
            return (True if ultima in OK else False), limpio
        return None, texto

    # ------------------------------------------------------------------
    # iter_block_items  (body / celdas)
    # ------------------------------------------------------------------
    def iter_block_items(self, parent, origen="parrafo"):
        if isinstance(parent, DocxDocument):
            parent_elm = parent._element.body
        elif isinstance(parent, _Cell):
            parent_elm = parent._tc
        else:
            return

        for child in parent_elm.iterchildren():
            if child.tag.endswith("}p"):
                yield Paragraph(child, parent), origen # type: ignore[arg-type]
            elif child.tag.endswith("}tbl"):
                table = Table(child, parent) # type: ignore[arg-type]
                yield table, origen
                for row in table.rows:
                    for cell in row.cells:
                        yield from self.iter_block_items(cell, origen)

    # ------------------------------------------------------------------
    # iter_all_blocks
    # Itera el body e inyecta el header de cada sección inmediatamente
    # después del sectPr que abre esa sección (no el que la cierra).
    #
    # En OOXML el sectPr dentro de un párrafo define las propiedades de
    # la sección que TERMINA ahí.  Por eso, para encontrar qué header
    # usa la sección que empieza en child[N+1], hay que mirar el sectPr
    # de child[N+?] (el siguiente que declara hrefs).
    # ------------------------------------------------------------------
    def iter_all_blocks(self, document):
        body = document.element.body
        children = list(body.iterchildren())

        W_HREF_EL = W_HREF
        RID_ATTR  = R_ID
        TYPE_ATTR = W_TYPE

        # ── Pre-escanear: para cada posición i de sectPr vacío (page break),
        #    encontrar el rId del SIGUIENTE sectPr con hrefs.
        # ── Resultado: inject_at[i] = rId a inyectar DESPUÉS de children[i]
        inject_after = {}   # child_index → rId

        def _get_hrefs(child):
            sect = child.find(f".//{W_SECT}")
            if sect is None and child.tag == W_SECT:
                sect = child
            if sect is None:
                return []
            return [
                (h.get(TYPE_ATTR, "default"), h.get(RID_ATTR))
                for h in sect.findall(W_HREF_EL)
            ]

        # Para cada sectPr con hrefs explícitos, el header aplica a la
        # sección que va desde el sectPr ANTERIOR (vacío o con hrefs) + 1
        # hasta este sectPr.  Inyectamos el header justo después del
        # sectPr anterior.
        last_sectpr_idx = -1
        for i, child in enumerate(children):
            hrefs = _get_hrefs(child)
            is_sectpr = (child.find(f".//{W_SECT}") is not None
                         or child.tag == W_SECT)
            if is_sectpr:
                default_rids = [rid for htype, rid in hrefs if htype == "default"]
                if default_rids:
                    # Inyectar justo después del sectPr anterior
                    inject_after[last_sectpr_idx] = default_rids[0]
                last_sectpr_idx = i

        # ── Iterar emitiendo body + headers en el momento correcto ──
        for i, child in enumerate(children):
            # Emitir el elemento del body
            if child.tag == W_P:
                yield Paragraph(child, document), "parrafo"
            elif child.tag == W_TBL:
                table = Table(child, document)
                yield table, "parrafo"
                for row in table.rows:
                    for cell in row.cells:
                        yield from self.iter_block_items(cell, "parrafo")

            # ¿Hay un header que inyectar después de este índice?
            if i in inject_after:
                rid    = inject_after[i]
                origen = f"header_inline_{rid}"
                for raw_para in self._hdr_map.get(rid, []):
                    yield raw_para, origen

    # ------------------------------------------------------------------
    # setData  (python-docx / .xpath)
    # ------------------------------------------------------------------
    def setData(self, numPr, data, idx, text, origen):
        if numPr:
            ilvl  = numPr[0].xpath("./w:ilvl")
            numid = numPr[0].xpath("./w:numId")
            nivel    = int(ilvl[0].get(f"{{{W}}}val"))
            lista_id = int(numid[0].get(f"{{{W}}}val"))
        else:
            nivel = lista_id = None

        data[idx] = {
            "texto":    text,
            "nivel":    nivel,
            "lista_id": lista_id,
            "origen":   origen
        }

    # ------------------------------------------------------------------
    # _setData_raw  (lxml puro, para _RawPara)
    # ------------------------------------------------------------------
    def _setData_raw(self, numPr_nodes, data, idx, text, origen):
        nivel = lista_id = None
        if numPr_nodes:
            np    = numPr_nodes[0]
            ilvl  = np.find(W_ILVL)
            numid = np.find(W_NUMID)
            if ilvl  is not None: nivel    = int(ilvl.get(W_VAL))
            if numid is not None: lista_id = int(numid.get(W_VAL))

        data[idx] = {
            "texto":    text,
            "nivel":    nivel,
            "lista_id": lista_id,
            "origen":   origen
        }
    
    