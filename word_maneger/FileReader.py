import zipfile
import re as _re
from lxml import etree
import json

from docx import Document
from docx.table import Table, _Cell
from docx.text.paragraph import Paragraph
from docx.document import Document as DocxDocument

# ── Namespaces ──────────────────────────────────────────────────────────
W   = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
WPS = "http://schemas.microsoft.com/office/word/2010/wordprocessingShape"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

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
R_ID     = f"{{{R_NS}}}id"
TXBX_TAG = f"{{{WPS}}}txbx"
TXBC_TAG = f"{{{W}}}txbxContent"


# ── _RawPara ─────────────────────────────────────────────────────────────
class _RawPara:
    """
    Wrapper mínimo para párrafos extraídos de text-boxes en headers
    (árboles lxml externos a python-docx).
    Expone  .text  y  ._element  con la misma interfaz que Paragraph.
    """
    def __init__(self, elem):
        self._element = elem
        self.text = "".join(t.text or "" for t in elem.iter(W_T))


# ── FileReader ────────────────────────────────────────────────────────────
class FileReader:

    # Prefijos para clasificar feedback — independiente de idioma.
    #
    # POSITIVOS:
    #   CORREC… → CORRECTA, CORRECTE, CORRECT, CORRECTO …
    #   CORRET… → CORRETA (portugués)
    #   VERD…   → VERDADERA, VERDADEIRO, VERDADE …
    #   TRUE, RICHTIG, JUSTE, JUSTO, CIERTO
    #
    # NEGATIVOS:
    #   INCORRE… → INCORRECTA, INCORRETA, INCORRECT …
    #   FALS…    → FALSA, FALSO, FALSE …
    #   WRONG, FALSCH, FAUX
    #
    # NOTA: se usa "CORREC"/"CORRET" en lugar de "CORRE" para evitar
    # falsos positivos con palabras como "correlação" (CORRELA…).
    _PREFIJOS_OK  = ("CORREC", "CORRET", "VERD", "TRUE",
                     "RICHTIG", "JUSTE", "JUSTO", "CIERTO")
    _PREFIJOS_NOK = ("INCORRE", "FALS", "WRONG", "FALSCH", "FAUX")

    # ------------------------------------------------------------------ #
    def __init__(self, doc_path=None):
        self.doc_path  = doc_path
        self.document  = None
        self._hdr_map  = {}     # rId → [_RawPara, …]

        if doc_path:
            self.load(doc_path)

    def load(self, doc_path):
        self.doc_path = doc_path
        self.document = Document(doc_path)
        self._hdr_map = self._build_header_map()

    # ══════════════════════════════════════════════════════════════════════
    # Construcción del mapa de headers
    # ══════════════════════════════════════════════════════════════════════
    def _build_header_map(self):
        """
        Lee todos los headerN.xml del ZIP y extrae párrafos de los
        text-boxes flotantes (wps:txbx).
        Devuelve  rId → [_RawPara, …]
        """
        hdr_map = {}
        with zipfile.ZipFile(self.doc_path) as z:  # type: ignore[attr-defined]
            rels_raw = z.read("word/_rels/document.xml.rels").decode("utf-8")
            rid_to_file = {
                m.group(1): m.group(2)
                for m in _re.finditer(
                    r'Id="(rId\d+)"[^>]*Target="(header\d+\.xml)"', rels_raw
                )
            }
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

    # ══════════════════════════════════════════════════════════════════════
    # Clasificación de feedback — basada en patrones, no en texto exacto
    # ══════════════════════════════════════════════════════════════════════
    @classmethod
    def _classify_feedback(cls, texto: str):
        """
        Devuelve True/False/None analizando SOLO la primera palabra.
        True  → respuesta correcta
        False → respuesta incorrecta
        None  → no es un párrafo de feedback
        """
        if not texto:
            return None
        primera = texto.split()[0].rstrip(".,;:").upper()
        if any(primera.startswith(p) for p in cls._PREFIJOS_NOK):
            return False
        if any(primera.startswith(p) for p in cls._PREFIJOS_OK):
            return True
        return None

    @classmethod
    def _split_feedback(cls, texto: str):
        """
        Detecta feedback embebido en el texto de una opción.
        Maneja tres patrones:
          A) Párrafo de puro feedback: "CORRETA. Explicación."
             → devuelve (ok, None, full_text)
          B) Feedback al final: "Option text. CORRECTA."
             → devuelve (ok, "Option text.", "CORRECTA.")
          C) Feedback en medio: "Option text. INCORRECTA. Explicación."
             → devuelve (ok, "Option text.", "INCORRECTA. Explicación.")
          D) Sin feedback → devuelve (None, texto, None)

        Retorno: (ok_bool_o_None, texto_opcion_o_None, texto_retro_o_None)
        """
        if not texto:
            return None, texto, None

        # Dividir en frases separadas por ". " o ". \n"
        partes = _re.split(r'\.\s+', texto.rstrip("."))

        for i, parte in enumerate(partes):
            primera_palabra = parte.strip().split()[0] if parte.strip() else ""
            ok = cls._classify_feedback(primera_palabra)
            if ok is None:
                continue

            texto_opcion = ". ".join(partes[:i]).strip()
            texto_retro  = ". ".join(partes[i:]).strip() + "."

            if not texto_opcion:
                # El feedback empieza desde el principio → párrafo de retro puro,
                # no inline. Lo señalamos con texto_opcion=None.
                return ok, None, texto_retro

            return ok, texto_opcion.rstrip(".") + ".", texto_retro

        return None, texto, None

    # ══════════════════════════════════════════════════════════════════════
    # Lectura de bloques del documento
    # ══════════════════════════════════════════════════════════════════════
    def read_paragraphs(self):
        """
        Devuelve un dict  idx → bloque  donde cada bloque tiene:
          texto, nivel, lista_id, origen, [matriz]
        """
        data: dict[int, dict] = {}
        idx  = 0

        for elem, origen in self.iter_all_blocks(self.document):

            # ── Tabla ──────────────────────────────────────────────────
            if isinstance(elem, Table):
                matriz: dict[int, dict[int, str]] = {}
                for i, row in enumerate(elem.rows):
                    matriz[i] = {j: cell.text.strip()
                                 for j, cell in enumerate(row.cells)}

                if not any(t for fila in matriz.values() for t in fila.values()):
                    continue  # tabla vacía

                data[idx] = {
                    "texto":    "",
                    "nivel":    None,
                    "lista_id": None,
                    "origen":   origen or "tabla",
                    "matriz":   matriz,
                }
                idx += 1

            # ── _RawPara (text-box de header) ──────────────────────────
            elif isinstance(elem, _RawPara):
                texto = elem.text.strip()
                if not texto:
                    continue
                numPr = elem._element.findall(f".//{W_NUMPR}")
                self._setData_raw(numPr, data, idx, texto, origen or "parrafo")
                idx += 1

            # ── Paragraph normal ───────────────────────────────────────
            else:
                texto = (elem.text or "").strip()
                if not texto:
                    continue
                numPr = elem._element.xpath("./w:pPr/w:numPr")
                self.setData(numPr, data, idx, texto, origen or "parrafo")
                idx += 1

        return data

    # ══════════════════════════════════════════════════════════════════════
    # Conversión al JSON de preguntas
    # ══════════════════════════════════════════════════════════════════════
    def parse_to_json(self):
        """
        Convierte los bloques crudos en un dict estructurado:
          { num_pregunta: { preg, val, multi, tipo, ops: { letra: { txt, ok, retro } } } }
        """
        data = self.read_paragraphs()

        resultado:       dict = {}
        num_pregunta:    int  = 0
        pregunta_actual: dict | None = None
        pregunta_lista:  int  | None = None
        opcion_actual:   str  | None = None   # letra de la opción esperando retro

        for _, item in data.items():
            texto    = item["texto"]
            nivel    = item["nivel"]
            lista_id = item.get("lista_id")
            origen   = item.get("origen", "parrafo")
            matriz   = item.get("matriz")

            # ── Tabla → filas como opciones ────────────────────────────
            if matriz is not None:
                if pregunta_actual is None:
                    continue
                # Si ya hay filas (fN) de una tabla anterior de esta misma
                # pregunta (tabla discontinua por salto de página), continuar
                # numerando desde el último índice en lugar de empezar en 0.
                start_row = len(pregunta_actual["ops"])
                for i, fila in enumerate(matriz.values(), start=start_row):
                    pregunta_actual["ops"][f"f{i}"] = {}
                    for j, columna in enumerate(fila.values()):
                        pregunta_actual["ops"][f"f{i}"][f"c{j}"] = {
                            "txt": columna
                        }
                continue

            # ── FIX A: opción en header con nivel=0 ó prefijo "a) b)"──
            if origen.startswith("header") and pregunta_actual is not None:
                if nivel == 0:
                    nivel = 1
                elif nivel is None and _re.match(r'^[a-dA-D]\)', texto.strip()):
                    nivel = 1

            # ── FIX B: nivel=0 con lista_id diferente (Word rompió ────
            #           numeración al cruzar página)
            if (nivel == 0
                    and pregunta_actual is not None
                    and lista_id is not None
                    and pregunta_lista is not None
                    and lista_id != pregunta_lista):
                nivel = 1

            # ── Nueva pregunta ─────────────────────────────────────────
            if nivel == 0:
                num_pregunta += 1
                resultado[num_pregunta] = {
                    "preg":  texto,
                    "val":   None,
                    "multi": False,
                    "tipo":  None,
                    "ops":   {},
                }
                pregunta_actual = resultado[num_pregunta]
                pregunta_lista  = lista_id
                opcion_actual   = None
                continue

            # ── Opción ────────────────────────────────────────────────
            if nivel == 1 and pregunta_actual is not None:
                letra  = chr(ord("a") + len(pregunta_actual["ops"]))
                # Limpiar prefijo "a) / b)" hardcodeado (text-boxes de header)
                texto_limpio = _re.sub(r'^[a-dA-D]\)\s*', '', texto).strip()
                ok_val, txt_op, retro_inline = self._split_feedback(texto_limpio)

                # Cuando txt_op es None significa que el texto completo era una
                # sola "palabra de feedback" (ej. "Verdadeiro."). En un nivel=1
                # eso es el texto de la opción, no feedback inline → resetear.
                if txt_op is None:
                    txt_op, ok_val, retro_inline = texto_limpio, None, None

                pregunta_actual["ops"][letra] = {
                    "txt":   txt_op,
                    "ok":    ok_val,
                    "retro": retro_inline,
                }
                # Siempre dejamos opcion_actual activo para que el párrafo
                # siguiente pueda completar ok y/o retro si son None o breves.
                opcion_actual = letra
                continue

            # ── Párrafo de feedback / retro (nivel=None) ───────────────
            if nivel is None and pregunta_actual is not None and opcion_actual is not None:
                ok_val, _, retro_texto = self._split_feedback(texto)

                if ok_val is not None:
                    # Párrafo que empieza con CORREC/INCORRE/etc.
                    op = pregunta_actual["ops"][opcion_actual]
                    if op["ok"] is None:
                        op["ok"] = ok_val
                    # Guardar retro (sin el prefijo CORRETA./INCORRECTA. si es breve)
                    if retro_texto and retro_texto.strip():
                        op["retro"] = retro_texto
                    opcion_actual = None   # feedback consumido

                elif pregunta_actual["ops"][opcion_actual]["ok"] is not None:
                    # ok ya fue fijado (inline); este párrafo es continuación de retro
                    op = pregunta_actual["ops"][opcion_actual]
                    if op["retro"]:
                        op["retro"] = (op["retro"] + " " + texto).strip()
                    else:
                        op["retro"] = texto
                    opcion_actual = None

        # ── Inferir multi-respuesta ────────────────────────────────────
        for bloque in resultado.values():
            if "f0" in bloque["ops"]:
                break
            correctas = sum(1 for op in bloque["ops"].values() if op.get("ok") is True)
            bloque["multi"] = correctas > 1

        resultado = self.asignar_tipo(resultado)
        with open("datos.json", "w", encoding="utf-8") as file:
            json.dump(resultado, file, indent=4, ensure_ascii=False)
        return resultado

    # ══════════════════════════════════════════════════════════════════════
    # Iteradores de bloques
    # ══════════════════════════════════════════════════════════════════════
    def iter_block_items(self, parent, origen="parrafo"):
        """Itera párrafos y tablas de body o de una celda."""
        if isinstance(parent, DocxDocument):
            parent_elm = parent.element.body  # type: ignore[attr-defined]
        elif isinstance(parent, _Cell):
            parent_elm = parent._tc
        else:
            return

        for child in parent_elm.iterchildren():
            if child.tag.endswith("}p"):
                yield Paragraph(child, parent), origen  # type: ignore[arg-type]
            elif child.tag.endswith("}tbl"):
                table = Table(child, parent)             # type: ignore[arg-type]
                yield table, origen
                for row in table.rows:
                    for cell in row.cells:
                        yield from self.iter_block_items(cell, origen)

    def iter_all_blocks(self, document):
        """
        Itera el body e inyecta headers de text-box en el punto correcto
        del flujo de lectura.

        PROBLEMA DE OOXML:
        El sectPr dentro de un párrafo define las propiedades de la sección
        que TERMINA ahí.  Hay dos candidatos para inyectar el header:
          A) El sectPr ANTERIOR (page break que inicia la página donde
             visualmente aparece el text-box).
          B) El sectPr DECLARATORIO (el que contiene el headerReference).

        HEURÍSTICA para elegir el punto correcto:
        El text-box de header contiene una opción de respuesta; su párrafo
        de retroalimentación está en el body inmediatamente después del
        salto de sección correcto.  Comprobamos cuál de los dos candidatos
        tiene un párrafo de FEEDBACK (CORREC…/INCORRE…) como primer
        contenido no vacío posterior.  Si lo tiene el sectPr anterior,
        inyectamos ahí; si lo tiene el declaratorio, inyectamos ahí.
        Si ninguno, usamos el declaratorio como fallback.
        """
        body     = document.element.body
        children = list(body.iterchildren())

        # ── Helpers ────────────────────────────────────────────────────
        def _hrefs(child):
            sect = child.find(f".//{W_SECT}")
            if sect is None and child.tag == W_SECT:
                sect = child
            if sect is None:
                return []
            return [(h.get(W_TYPE, "default"), h.get(R_ID))
                    for h in sect.findall(W_HREF)]

        def _first_nonempty_text(start_idx):
            """Devuelve el texto del primer párrafo no vacío tras start_idx."""
            for j in range(start_idx + 1, len(children)):
                txt = "".join(t.text or "" for t in children[j].iter(W_T)).strip()
                if txt:
                    return txt
            return ""

        # ── Pre-escanear sectPr para construir inject_after ──────────
        # inject_after[i] = rId  →  emitir header justo después de children[i]
        inject_after: dict[int, str] = {}
        last_sectpr_idx = -1

        for i, child in enumerate(children):
            hrefs   = _hrefs(child)
            is_sect = (child.find(f".//{W_SECT}") is not None
                       or child.tag == W_SECT)
            if is_sect:
                def_rids = [rid for htype, rid in hrefs if htype == "default"]
                if def_rids:
                    rid = def_rids[0]
                    # Candidato A: sectPr anterior (last_sectpr_idx)
                    # Candidato B: sectPr declaratorio (i)
                    txt_after_prev = _first_nonempty_text(last_sectpr_idx)
                    txt_after_decl = _first_nonempty_text(i)
                    fb_prev = self._classify_feedback(txt_after_prev)
                    fb_decl = self._classify_feedback(txt_after_decl)

                    if fb_prev is not None:
                        # El feedback del header está justo después del sectPr anterior
                        inject_after[last_sectpr_idx] = rid
                    elif fb_decl is not None:
                        # El feedback está justo después del sectPr declaratorio
                        inject_after[i] = rid
                    else:
                        # Fallback: inyectar en el sectPr declaratorio
                        inject_after[i] = rid

                last_sectpr_idx = i

        # ── Iterar emitiendo body + headers en orden correcto ─────────
        for i, child in enumerate(children):
            if child.tag == W_P:
                yield Paragraph(child, document), "parrafo"
            elif child.tag == W_TBL:
                table = Table(child, document)
                yield table, "parrafo"
                for row in table.rows:
                    for cell in row.cells:
                        yield from self.iter_block_items(cell, "parrafo")

            if i in inject_after:
                rid    = inject_after[i]
                origen = f"header_inline_{rid}"
                for raw_para in self._hdr_map.get(rid, []):
                    yield raw_para, origen

    # ══════════════════════════════════════════════════════════════════════
    # setData helpers
    # ══════════════════════════════════════════════════════════════════════
    def setData(self, numPr, data, idx, texto, origen):
        """Para Paragraph / python-docx (usa .xpath)."""
        nivel = lista_id = None
        if numPr:
            ilvl  = numPr[0].xpath("./w:ilvl")
            numid = numPr[0].xpath("./w:numId")
            nivel    = int(ilvl[0].get(f"{{{W}}}val"))
            lista_id = int(numid[0].get(f"{{{W}}}val"))
        data[idx] = {
            "texto":    texto,
            "nivel":    nivel,
            "lista_id": lista_id,
            "origen":   origen,
        }

    def _setData_raw(self, numPr_nodes, data, idx, texto, origen):
        """Para _RawPara (usa lxml puro)."""
        nivel = lista_id = None
        if numPr_nodes:
            np    = numPr_nodes[0]
            ilvl  = np.find(W_ILVL)
            numid = np.find(W_NUMID)
            if ilvl  is not None: nivel    = int(ilvl.get(W_VAL))
            if numid is not None: lista_id = int(numid.get(W_VAL))
        data[idx] = {
            "texto":    texto,
            "nivel":    nivel,
            "lista_id": lista_id,
            "origen":   origen,
        }

    def asignar_tipo(self, datos):
        if "tipo" in datos is not None:
            return datos
        for pregunta in datos.values():
            ops = pregunta.get("ops", {})
            num_ops = len(ops)

            if "f0" in ops:
                for fila in ops.values():
                    num_columnas = len(fila)
                    if num_columnas > 2:
                        pregunta["tipo"] = "Ensayo"
                        break
                pregunta["tipo"] = "Emparejamiento"
            elif num_ops == 2:
                pregunta["tipo"] = "V/F"
            elif num_ops >= 4:
                pregunta["tipo"] = "multi"
            else:
                pregunta["tipo"] = "Ensayo"

        return datos