import zipfile
import re as re
from lxml import etree
import json
import base64 as _b64

from docx import Document
from docx.table import Table, _Cell
from docx.text.paragraph import Paragraph
from docx import text
from docx.document import Document as DocxDocument

# ── Namespaces ──────────────────────────────────────────────────────────
W   = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
WPS = 'http://schemas.microsoft.com/office/word/2010/wordprocessingShape'
R_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'

W_P      = f'{{{W}}}p'
W_TBL    = f'{{{W}}}tbl'
W_TC     = f'{{{W}}}tc'
W_T      = f'{{{W}}}t'
W_SECT   = f'{{{W}}}sectPr'
W_NUMPR  = f'{{{W}}}numPr'
W_ILVL   = f'{{{W}}}ilvl'
W_NUMID  = f'{{{W}}}numId'
W_VAL    = f'{{{W}}}val'
W_HREF   = f'{{{W}}}headerReference'
W_TYPE   = f'{{{W}}}type'
R_ID     = f'{{{R_NS}}}id'
TXBX_TAG = f'{{{WPS}}}txbx'
TXBC_TAG = f'{{{W}}}txbxContent'
W_R      = f'{{{W}}}r'
W_RPR    = f'{{{W}}}rPr'
W_B      = f'{{{W}}}b'
W_I      = f'{{{W}}}i'
W_U_TAG  = f'{{{W}}}u'
W_STRIKE = f'{{{W}}}strike'
W_COLOR  = f'{{{W}}}color'
W_BR     = f'{{{W}}}br'
A_NS   = 'http://schemas.openxmlformats.org/drawingml/2006/main'
R_EMB  = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed'


# ── _RawPara ─────────────────────────────────────────────────────────────
class _RawPara:
    '''
    Wrapper mínimo para párrafos extraídos de text-boxes en headers
    (árboles lxml externos a python-docx).
    Expone  .text  y  ._element  con la misma interfaz que Paragraph.
    '''
    def __init__(self, elem):
        self._element = elem
        self.text = ''.join(t.text or '' for t in elem.iter(W_T))


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
    # NOTA: se usa 'CORREC'/'CORRET' en lugar de 'CORRE' para evitar
    # falsos positivos con palabras como 'correlação' (CORRELA…).
    _PREFIJOS_OK  = ('CORREC', 'CORRET', 'VERD', 'TRUE',
                     'RICHTIG', 'JUSTE', 'JUSTO', 'CIERTO')
    _PREFIJOS_NOK = ('INCORRE', 'FALS', 'WRONG', 'FALSCH', 'FAUX')

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
        '''
        Lee todos los headerN.xml del ZIP y extrae párrafos de los
        text-boxes flotantes (wps:txbx).
        Devuelve  rId → [_RawPara, …]
        '''
        hdr_map = {}
        with zipfile.ZipFile(self.doc_path) as z:  # type: ignore[attr-defined]
            rels_raw = z.read('word/_rels/document.xml.rels').decode('utf-8')
            rid_to_file = {
                m.group(1): m.group(2)
                for m in re.finditer(
                    r'Id="(rId\d+)"[^>]*Target="(header\d+\.xml)"', rels_raw
                )
            }
            for rid, fname in rid_to_file.items():
                root  = etree.fromstring(z.read(f'word/{fname}'))
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
        '''
        Devuelve True/False/None analizando SOLO la primera palabra.
        True  → respuesta correcta
        False → respuesta incorrecta
        None  → no es un párrafo de feedback
        '''
        if not texto:
            return None
        primera = texto.split()[0].rstrip('.,;:').upper()
        if any(primera.startswith(p) for p in cls._PREFIJOS_NOK):
            return False
        if any(primera.startswith(p) for p in cls._PREFIJOS_OK):
            return True
        return None

    @classmethod
    def _split_feedback(cls, texto: str):
        '''
        Detecta feedback embebido en el texto de una opción.
        Maneja tres patrones:
          A) Párrafo de puro feedback: 'CORRETA. Explicación.'
             → devuelve (ok, None, full_text)
          B) Feedback al final: 'Option text. CORRECTA.'
             → devuelve (ok, 'Option text.', 'CORRECTA.')
          C) Feedback en medio: 'Option text. INCORRECTA. Explicación.'
             → devuelve (ok, 'Option text.', 'INCORRECTA. Explicación.')
          D) Sin feedback → devuelve (None, texto, None)

        Retorno: (ok_bool_o_None, texto_opcion_o_None, texto_retro_o_None)
        '''
        if not texto:
            return None, texto, None

        # Dividir en frases separadas por '. ' o '. \n'
        partes = re.split(r'\.\s+', texto.rstrip('.'))

        for i, parte in enumerate(partes):
            primera_palabra = parte.strip().split()[0] if parte.strip() else ''
            ok = cls._classify_feedback(primera_palabra)
            if ok is None:
                continue

            texto_opcion = '. '.join(partes[:i]).strip()
            texto_retro  = '. '.join(partes[i:]).strip() + '.'

            if not texto_opcion:
                # El feedback empieza desde el principio → párrafo de retro puro,
                # no inline. Lo señalamos con texto_opcion=None.
                return ok, None, texto_retro

            return ok, texto_opcion.rstrip('.') + '.', texto_retro

        return None, texto, None

    # ══════════════════════════════════════════════════════════════════════
    # Lectura de bloques del documento
    # ══════════════════════════════════════════════════════════════════════
    def read_paragraphs(self):

        '''
        Devuelve un dict  idx → bloque  donde cada bloque tiene:
          texto, nivel, lista_id, origen, [matriz]
        '''
        data: dict[int, dict] = {}
        idx  = 0
        origen_bloque_anterior = ''
        estilo_bloque_anterior = ''

        for elem, origen in self.iter_all_blocks(self.document):

            # ── Tabla ──────────────────────────────────────────────────
            if isinstance(elem, Table):
                matriz: dict = {}
                for i, row in enumerate(elem.rows):
                    matriz[f'f{i}'] = {}
                    for j, cell in enumerate(row.cells):
                        img = self.detectar_blip(cell)   # lista o None
                        if img:
                            # Celda con imagen(es): guardar texto + lista de imgs
                            matriz[f'f{i}'][f'c{j}'] = {"txt": cell.text.strip(), "img": img}
                        else:
                            matriz[f'f{i}'][f'c{j}'] = cell.text.strip()

                if not any(t for fila in matriz.values() for t in fila.values()):
                    continue  # tabla vacía
                data[idx] = {
                    'texto':    '',
                    'nivel':    None,
                    'lista_id': None,
                    'origen':   origen or 'tabla',
                    'matriz':   matriz,
                }
                idx += 1

            # ── _RawPara (text-box de header) ──────────────────────────
            elif isinstance(elem, _RawPara):
                texto = elem.text
                if not texto:
                    continue
                numPr = elem._element.findall(f'.//{W_NUMPR}')
                self._setData_raw(numPr, data, idx, texto, origen or 'parrafo')
                idx += 1

            # ── Paragraph normal ───────────────────────────────────────
            else:
                texto_plano, html_inline = self._runs_a_html(elem._element)
                texto = texto_plano.replace('\\t', '__________')
                html = html_inline.replace('\\t', '__________')

                # Extraer estilo del párrafo para detectar preguntas de ensayo
                ppr   = elem._element.find(f'{{{W}}}pPr')
                estilo = ''
                if ppr is not None:
                    ps = ppr.find(f'{{{W}}}pStyle')
                    if ps is not None:
                        estilo = ps.get(f'{{{W}}}val', '')

                if estilo == 'aP-Razon' and estilo_bloque_anterior == 'aP-Razon' and origen == 'parrafo' and origen_bloque_anterior == 'parrafo':
                    lista_html = list(html)
                    lista_html.insert(0, '<br>')
                    html = ''.join(lista_html)

                # Detectar imagen embebida (w:drawing → a:blip)
                blips  = elem._element.findall(f'.//{{{A_NS}}}blip')
                if blips:
                    for blip in blips:
                        rid = blip.get(R_EMB)
                        if rid:
                            img_b64 = self._extract_image_b64(rid)
                            if img_b64:
                                data[idx] = {
                                    'texto':    texto.strip(),
                                    'html':     html.strip(),
                                    'nivel':    None,
                                    'lista_id': None,
                                    'origen':   origen or 'parrafo',
                                    'estilo':   estilo,
                                    'img':   img_b64
                                }
                                idx += 1
                    continue   # párrafo de imagen procesado, no caer en el bloque de texto

                if not texto.strip():
                    continue
                numPr = elem._element.xpath('./w:pPr/w:numPr')
                self.setData(numPr, data, idx, texto, origen or 'parrafo', estilo, html)
                origen_bloque_anterior = origen
                estilo_bloque_anterior = estilo
                idx += 1
                
        with open('datos_crudos.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        return data

    # ══════════════════════════════════════════════════════════════════════
    # Conversión al JSON de preguntas
    # ══════════════════════════════════════════════════════════════════════
    def parse_to_json(self):
        '''
        Convierte los bloques crudos en un dict estructurado:
          { num_pregunta: { preg, val, multi, tipo, ops: { letra: { txt, ok, retro } } } }
        '''
        data = self.read_paragraphs()

        resultado:       dict = {}
        num_pregunta:    int  = 0
        pregunta_actual: dict | None = None
        pregunta_lista:  int  | None = None
        opcion_actual:   str  | None = None   # letra de la opción esperando retro
        en_modo_ensayo:  bool        = False  # True sólo cuando el marcador aP-Respuesta fue visto

        for _, item in data.items():
            texto    = item['texto'] 
            nivel    = item['nivel']
            lista_id = item.get('lista_id')
            origen   = item.get('origen', 'parrafo')
            matriz   = item.get('matriz')

            estilo = item.get('estilo', '')

            # ── Pregunta de Ensayo: estilo aPREGUNTA ───────────────────
            # Los documentos de ensayo usan el estilo 'aPREGUNTA' en lugar
            # de listas numeradas (nivel=0) para marcar el enunciado.
            if estilo == 'aPREGUNTA':
                num_pregunta += 1
                resultado[num_pregunta] = {
                    'preg':  item.get('html', texto),
                    'val':   None,
                    'tipo':  None,
                    'ops':   {},
                }
                pregunta_actual = resultado[num_pregunta]
                pregunta_lista  = lista_id
                opcion_actual   = None
                en_modo_ensayo  = False
                continue

            # ── Marcador 'Respuesta:' (aP-Respuesta-Titulo) ────────────
            # Activa la captura de retroalimentación para preguntas de ensayo.
            # El prefijo 'aP-Respuesta' cubre variantes multiidioma del estilo.
            if estilo.startswith('aP-Respuesta') and pregunta_actual is not None:
                opcion_actual  = 'a'
                en_modo_ensayo = True
                if 'a' not in pregunta_actual['ops']:
                    pregunta_actual['ops']['a'] = {'txt': ''}
                continue

            # ── Imagen: tres destinos posibles ───────────────────────────
            # A) Modo ensayo con ops['a'] activo → retroalimentación del ensayo
            # B) opcion_actual activo            → imagen de una opción concreta
            # C) opcion_actual es None           → imagen del enunciado
            imagen = item.get('img')
            if imagen is not None and pregunta_actual is not None:
                if (en_modo_ensayo
                        and 'a' in pregunta_actual['ops']
                        and list(pregunta_actual['ops'].keys()) == ['a']):
                    # A) ensayo: acumular en ops['a']['img']
                    pregunta_actual["ops"]["a"].update({'img': imagen})
                elif opcion_actual is not None and opcion_actual in pregunta_actual['ops']:
                    # B) imagen asociada a la opción activa (ej. después de la letra)
                    pregunta_actual["ops"][opcion_actual].update({"img": imagen})
                else:
                    # C) imagen tras el enunciado → se adjunta a la pregunta
                    pregunta_actual.update({"img": imagen})
                continue

            # ── Párrafos de retroalimentación de ensayo ─────────────────
            # Estilos aP-Razon, aP-Razon-Bolitas, Listas-2N, etc.
            # Se acumulan en ops['a']['txt'] SÓLO si el marcador aP-Respuesta
            # fue visto en esta pregunta (en_modo_ensayo=True). Esto evita
            # que preguntas de opción múltiple se absorban erróneamente.
            # Los bloques de imagen se manejan antes — no entran aquí.
            if (imagen is None                              # no es imagen
                    and matriz is None                         # no es tabla
                    and en_modo_ensayo
                    and opcion_actual == 'a'
                    and pregunta_actual is not None
                    and 'a' in pregunta_actual['ops']
                    and list(pregunta_actual['ops'].keys()) == ['a']
                    and pregunta_actual['ops']['a'].get('ok') is None
                    and not any(k.startswith('f') for k in pregunta_actual['ops'])
                    and estilo not in ('aPREGUNTA', 'ListParagraph')):
                op = pregunta_actual['ops']['a']
                prefijo   = self._prefijo_viñeta(estilo, nivel)
                html_p = item.get('html', texto)
                separador = '\n' if op['txt'] else ''
                op['txt'] = op['txt'] + separador + prefijo + html_p
                op['html'] = f'<p>{html_p}</p>'
                continue

            # ── Tabla → filas como opciones ────────────────────────────
            if matriz is not None:
                if pregunta_actual is None:
                    continue

                # Si estamos en modo ensayo, la tabla es parte de la
                # retroalimentación → añadirla a ops['a']['tablas']
                if (en_modo_ensayo
                        and 'a' in pregunta_actual['ops']
                        and list(pregunta_actual['ops'].keys()) == ['a']):
                    op = pregunta_actual['ops']['a']
                    op.update({"tablas": matriz})
                    continue

                # Si ya hay filas (fN) de una tabla anterior de esta misma
                # pregunta (tabla discontinua por salto de página), continuar
                # numerando desde el último índice en lugar de empezar en 0.
                start_row = len(pregunta_actual['ops'])
                for i, fila in enumerate(matriz.values(), start=start_row):
                    pregunta_actual['ops'][f'f{i}'] = {}
                    for j, columna in enumerate(fila.values()):
                        # Si la celda ya tiene estructura dict (ej. celda con
                        # imagen: {"txt": "...", "imgs": [...]}), usarla tal cual.
                        # Si es un string plano, envolverlo en {'txt': ...}.
                        if isinstance(columna, dict):
                            pregunta_actual['ops'][f'f{i}'][f'c{j}'] = columna
                        else:
                            pregunta_actual['ops'][f'f{i}'].update({f'c{j}': columna})
                continue

            # ── FIX A: opción en header con nivel=0 ó prefijo 'a) b)'──
            if origen.startswith('header') and pregunta_actual is not None:
                if nivel == 0:
                    nivel = 1
                elif nivel is None and re.match(r'^[a-dA-D]\)', texto.strip()):
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
                # Si la pregunta actual es de ensayo, los párrafos con
                # nivel=0 pero estilo de lista (Listas-2N, ListParagraph...)
                # son retroalimentación, no nuevas preguntas.
                ops_actuales = pregunta_actual['ops'] if pregunta_actual else {}
                es_retro_ensayo = (
                    imagen is None
                    and matriz is None
                    and en_modo_ensayo
                    and pregunta_actual is not None
                    and opcion_actual == 'a'
                    and list(ops_actuales.keys()) == ['a']
                    and ops_actuales['a'].get('ok') is None
                    and not any(k.startswith('f') for k in ops_actuales)
                    and estilo not in ('aPREGUNTA', 'ListParagraph')
                )
                if es_retro_ensayo:
                    op = pregunta_actual['ops']['a'] # type: ignore[attr-defined]
                    prefijo   = self._prefijo_viñeta(estilo, nivel)
                    html_p = item.get('html', texto)
                    separador = '\n' if op['json'] else ''
                    op['json'] = op['json'] + separador + prefijo + html_p
                    op['html'] = f'<p>{html_p}</p>'
                    continue

                num_pregunta += 1
                resultado[num_pregunta] = {
                    'preg':  item.get('html', texto),
                    'val':   None,
                    'tipo':  None,
                    'ops':   {},
                }
                pregunta_actual = resultado[num_pregunta]
                pregunta_lista  = lista_id
                opcion_actual   = None
                en_modo_ensayo  = False
                continue

            # ── Opción ────────────────────────────────────────────────
            if nivel == 1 and pregunta_actual is not None:
                letra  = chr(ord('a') + len(pregunta_actual['ops']))
                # Limpiar prefijo 'a) / b)' hardcodeado (text-boxes de header)
                texto_limpio = re.sub(r'^[a-dA-D]\)\s*', '', texto).strip()
                html_limpio = re.sub(r'^[a-dA-D]\)\s*', '', item.get('html', texto)).strip()
                ok_val, txt_op, retro_inline = self._split_feedback(texto_limpio)

                # Cuando txt_op es None significa que el texto completo era una
                # sola 'palabra de feedback' (ej. 'Verdadeiro.'). En un nivel=1
                # eso es el texto de la opción, no feedback inline → resetear.
                if txt_op is None:
                    txt_op, ok_val, retro_inline = html_limpio, None, None

                pregunta_actual['ops'][letra] = {
                    'json':   txt_op,
                    'html':   '',
                    'ok':    ok_val,
                    'retro': retro_inline,
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
                    op = pregunta_actual['ops'][opcion_actual]
                    if op['ok'] is None:
                        op['ok'] = ok_val
                    # Guardar retro (sin el prefijo CORRETA./INCORRECTA. si es breve)
                    if retro_texto and retro_texto.strip():
                        op['retro'] = retro_texto
                    opcion_actual = None   # feedback consumido

                elif pregunta_actual['ops'][opcion_actual]['ok'] is not None:
                    # ok ya fue fijado (inline); este párrafo es continuación de retro
                    op = pregunta_actual['ops'][opcion_actual]
                    if op['retro']:
                        op['retro'] = (op['retro'] + ' ' + texto).strip()
                    else:
                        op['retro'] = texto
                    opcion_actual = None

        resultado = self.asignar_tipo(resultado)

        with open('datos.json', 'w', encoding='utf-8') as file:
            json.dump(resultado, file, indent=4, ensure_ascii=False)
        return resultado

    # ══════════════════════════════════════════════════════════════════════
    # Iteradores de bloques
    # ══════════════════════════════════════════════════════════════════════
    def iter_block_items(self, parent, origen='parrafo'):
        '''Itera párrafos y tablas de body o de una celda.'''
        if isinstance(parent, DocxDocument):
            parent_elm = parent.element.body  # type: ignore[attr-defined]
        elif isinstance(parent, _Cell):
            parent_elm = parent._tc
        else:
            return

        for child in parent_elm.iterchildren():
            if child.tag.endswith('}p'):
                yield Paragraph(child, parent), origen  # type: ignore[arg-type]
            elif child.tag.endswith('}tbl'):
                table = Table(child, parent)             # type: ignore[arg-type]
                yield table, origen
                for row in table.rows:
                    for cell in row.cells:
                        yield from self.iter_block_items(cell, origen)

    def iter_all_blocks(self, document):
        '''
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
        '''
        body     = document.element.body
        children = list(body.iterchildren())

        # ── Helpers ────────────────────────────────────────────────────
        def _hrefs(child):
            sect = child.find(f'.//{W_SECT}')
            if sect is None and child.tag == W_SECT:
                sect = child
            if sect is None:
                return []
            return [(h.get(W_TYPE, 'default'), h.get(R_ID))
                    for h in sect.findall(W_HREF)]

        def _first_nonempty_text(start_idx):
            '''Devuelve el texto del primer párrafo no vacío tras start_idx.'''
            for j in range(start_idx + 1, len(children)):
                txt = ''.join(t.text or '' for t in children[j].iter(W_T)).strip()
                if txt:
                    return txt
            return ''

        # ── Pre-escanear sectPr para construir inject_after ──────────
        # inject_after[i] = rId  →  emitir header justo después de children[i]
        inject_after: dict[int, str] = {}
        last_sectpr_idx = -1

        for i, child in enumerate(children):
            hrefs   = _hrefs(child)
            is_sect = (child.find(f'.//{W_SECT}') is not None
                       or child.tag == W_SECT)
            if is_sect:
                def_rids = [rid for htype, rid in hrefs if htype == 'default']
                if def_rids:
                    rid = def_rids[0]
                    # Candidato A: sectPr anterior (last_sectpr_idx)
                    # Candidato B: sectPr declaratorio (i)
                    txt_after_prev = _first_nonempty_text(last_sectpr_idx)
                    txt_after_decl = _first_nonempty_text(i)
                    # _split_feedback detecta feedback en cualquier posición del
                    # párrafo (no solo la primera palabra), lo que cubre el caso
                    # de feedback inline: "Opción texto. INCORRECTA. Explicación."
                    fb_prev = self._split_feedback(txt_after_prev)[0]
                    fb_decl = self._split_feedback(txt_after_decl)[0]

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
                yield Paragraph(child, document), 'parrafo'
            elif child.tag == W_TBL:
                # Emitir la tabla completa como un único bloque estructurado.
                # NO emitir las celdas individualmente: ya están capturadas
                # en la matriz bidimensional del bloque tabla, y emitirlas
                # además como párrafos sueltos produce duplicados.
                table = Table(child, document)               # type: ignore[arg-type]
                yield table, 'parrafo' 

            if i in inject_after:
                rid    = inject_after[i]
                origen = f'header_inline_{rid}'
                for raw_para in self._hdr_map.get(rid, []):
                    yield raw_para, origen

    # ══════════════════════════════════════════════════════════════════════
    # setData helpers
    # ══════════════════════════════════════════════════════════════════════
    def setData(self, numPr, data, idx, texto, origen, estilo='', html=''):
        '''Para Paragraph / python-docx (usa .xpath).'''
        nivel = lista_id = None
        if numPr:
            ilvl  = numPr[0].xpath('./w:ilvl')
            numid = numPr[0].xpath('./w:numId')
            nivel    = int(ilvl[0].get(f'{{{W}}}val'))
            lista_id = int(numid[0].get(f'{{{W}}}val'))
        data[idx] = {
            'texto':    texto,
            'html': html or '',
            'nivel':    nivel,
            'lista_id': lista_id,
            'origen':   origen,
            'estilo':   estilo,
        }

    def _setData_raw(self, numPr_nodes, data, idx, texto, origen):
        '''Para _RawPara (usa lxml puro).'''
        nivel = lista_id = None
        if numPr_nodes:
            np    = numPr_nodes[0]
            ilvl  = np.find(W_ILVL)
            numid = np.find(W_NUMID)
            if ilvl  is not None: nivel    = int(ilvl.get(W_VAL))
            if numid is not None: lista_id = int(numid.get(W_VAL))
        data[idx] = {
            'texto':    texto,
            'nivel':    nivel,
            'lista_id': lista_id,
            'origen':   origen,
        }

    def _extract_image_b64(self, rid: str) -> dict | None:
        '''
        Dado un rId de relación, extrae la imagen del ZIP y la devuelve
        como {'b64': str_base64, 'fmt': 'png'|'jpg'|...} o None si falla.
        '''
        try:
            with zipfile.ZipFile(self.doc_path) as z:  # type: ignore[attr-defined]
                rels_raw = z.read('word/_rels/document.xml.rels').decode('utf-8')
                m = re.search(
                    r'Id="' + re.escape(rid) + r'"[^>]*Target="(media/[^"]+)"', rels_raw
                )
                if not m:
                    return None
                media_path = f'word/{m.group(1)}'
                img_bytes  = z.read(media_path)
                fmt = media_path.rsplit('.', 1)[-1].lower()
                # Moodle acepta jpg como 'jpeg'
                if fmt == 'jpg':
                    fmt = 'jpeg'
                return {'b64': _b64.b64encode(img_bytes).decode('ascii'), 'fmt': fmt}
        except Exception:
            return None
        
    def detectar_blip(self, cell: _Cell) -> dict | None:
        """
        Extrae la primera imagen embebida en una celda de tabla.
        Devuelve  {'b64': ..., 'fmt': ...}  o  None si no hay imagen.
        """
        for blip in cell._element.findall(f'.//{{{A_NS}}}blip'):
            rid = blip.get(R_EMB)
            if rid:
                img = self._extract_image_b64(rid)
                if img:
                    return img
        return None

    # ── Mapa de estilos de Word → prefijo de viñeta ─────────────────────
    # Preserva la estructura visual de la retroalimentación de ensayo.
    _PREFIJOS_ESTILO: dict[str, str] = {
        'aP-Razon-Bolitas': '•    ',
        'Bolitas':          '•    ',
        'Listas-3N':        '  •    ',
        'Listas-2N':        '  •    ',
        'Listas-A3':        '    •    ',
        'Listas-A1':        '      •    ',
    }

    @classmethod
    def _prefijo_viñeta(cls, estilo: str, nivel) -> str:
        """
        Devuelve el prefijo de viñeta según el estilo del párrafo.
        Se usa al acumular la retroalimentación de preguntas de ensayo
        para preservar la distinción entre párrafos y puntos de lista.
        """
        if estilo in cls._PREFIJOS_ESTILO:
            return cls._PREFIJOS_ESTILO[estilo]
        if nivel == 1:
            return '• '
        return ''

    def asignar_tipo(self, datos):
        for pregunta in datos.values():
            if pregunta.get('tipo') is not None:
                continue   # ya asignado previamente
            ops     = pregunta.get('ops', {})
            num_ops = len(ops)

            if 'a' in ops and list(ops.keys()) == ['a']:
                # Solo la clave 'a' → respuesta de ensayo
                pregunta['tipo'] = 'ensayo'

            elif 'f0' in ops:
                # Filas de tabla → emparejamiento o V/F tabular
                pregunta['tipo'] = 'match'

            elif num_ops == 2:
                pregunta['tipo'] = 'V/F'

            elif num_ops >= 3:
                pregunta['tipo'] = 'multi'

        return datos
    
    @staticmethod
    def _runs_a_html(p_elem) -> tuple[str, str]:
        '''
        Recorre los runs (<w:r>) de un elemento párrafo y devuelve:
          texto_plano : str  — texto concatenado sin formato
          html_inline : str  — texto con marcado HTML inline

        Formatos soportados:
          <w:b/>      → <strong>…</strong>
          <w:i/>      → <em>…</em>
          <w:u/>      → <u>…</u>
          <w:strike/> → <s>…</s>
          <w:color/>  → <span style="color:#RRGGBB">…</span>
          <w:br/>     → <br>   (salto de línea dentro del párrafo)

        Nota: <w:b w:val="0"/> significa "sin negrita" (override de estilo),
        por lo que se comprueba el atributo val antes de activar el formato.
        '''

        partes_plano: list[str] = []
        partes_html:  list[str] = []

        for run in p_elem:
            if run.tag != W_R:
                continue

            rpr   = run.find(W_RPR)
            bold  = FileReader._activo(rpr, W_B)
            ital  = FileReader._activo(rpr, W_I)
            uline = FileReader._activo(rpr, W_U_TAG)
            strk  = FileReader._activo(rpr, W_STRIKE)

            # Color personalizado (ignorar automático / "none" / "auto")
          
            for child in run:
                if child.tag == W_T:
                    t = child.text or ''
                    partes_plano.append(t)

                    # Aplicar formato
                    if strk:  t = f'<s>{t}</s>'
                    if uline: t = f'<u>{t}</u>'
                    if ital:  t = f'<em>{t}</em>'
                    if bold:  t = f'<strong>{t}</strong>'
                    partes_html.append(t)

                elif child.tag == W_BR:
                    partes_plano.append('\\n')
                    partes_html.append('<br>')

        return ''.join(partes_plano), ''.join(partes_html)

    @staticmethod
    def _activo(rpr, tag):
            '''True si el elemento de formato está presente y no desactivado.'''
            el = rpr.find(tag) if rpr is not None else None
            if el is None:
                return False
            val = el.get(W_VAL, '1')
            return val not in ('0', 'false', 'off')

    