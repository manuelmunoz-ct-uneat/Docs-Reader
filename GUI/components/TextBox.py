from PySide6.QtWidgets import QTextBrowser
import html

class JsonFormater(QTextBrowser):
    def __init__(self, parent=None):
            super().__init__(parent)
            self.setReadOnly(True)

    def setJson(self, data: dict):
        html_content = ''

        for num_pregunta, bloque in data.items():
            html_content += f'<p><b>Pregunta {num_pregunta}</b>: {html.escape(str(bloque.get('preg', '')))}</p>'

            for letra, opcion in bloque['ops'].items():
                if bloque['tipo'] == 'match':
                    html_content += '<table border="1">'

                    for fila in bloque['ops'].values():
                        html_content += '<tr>'

                        for columna in fila.values():
                            if isinstance(columna, dict):
                                html_content += f'<td>{html.escape(str(columna['txt']))}</td>'
                            elif isinstance(columna, str):
                                html_content += f'<td>{html.escape(str(columna))}</td>'

                        html_content += '</tr>'
                    html_content += '</table>'
                    break
                elif bloque['tipo'] == 'Ensayo':
                    for tipo in opcion.keys():
                        if tipo == 'txt':
                            html_content += (
                                f'<p style="margin-left:20px;">'
                                f'<b>{letra})</b> '
                                f'<span style="color:fuchsia">{html.escape(str(opcion.get('txt')))}</span><br>'
                                f'</p>'
                            )
                        elif tipo == 'tablas':
                            html_content += '<table border="1">'

                            for fila in opcion.get('tablas').values():
                                html_content += '<tr>'

                                for contenido in fila.values():
                                    if "img" in contenido:
                                        html_content += (
                                            f'<td>{html.escape(str(contenido.get("txt")))}</td>'
                                            f'<br>'
                                            f'<img src="data:image/{contenido['img'].get('fmt')};base64, {contenido['img'].get('b64')}"/>'
                                            )
                                        continue
                                    else:                                        
                                        html_content += f'<td>{html.escape(str(contenido))}</td>'
                                        continue

                                html_content += '</tr>'

                            html_content += '</table>'
                        elif tipo == 'imagenes':
                            html_content += f'<img src="data:image/{opcion['imagenes'].get('fmt')};base64, {opcion['imagenes'].get('b64')}"/>'
                else:
                    color = 'green' if opcion['ok'] is True else 'red' if opcion['ok'] is False else 'FloralWhite'
                    html_content += (
                        f'<p style="margin-left:20px;">'
                        f'<b>{letra})</b> '
                        f'<span style="color:{color}">{html.escape(str(opcion.get('txt')))}</span><br>'
                        f'<span style="color:fuchsia">{html.escape(str(opcion.get('retro')))}</span>'
                        f'</p>'
                    )

        self.setHtml(html_content)
        font = self.font()
        font.setPointSize(12)
        self.setFont(font)

    def _is_hex_color(self, value: str):
        if len(value) == 6:
            try:
                int(value, 16)
                return True
            except ValueError:
                return False
        return False