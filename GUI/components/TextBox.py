from PySide6.QtWidgets import QTextBrowser
import html

class JsonFormater(QTextBrowser):
    def __init__(self, parent=None):
            super().__init__(parent)
            self.setReadOnly(True)

    def setJson(self, data: dict):
        html_content = ''

        for num_pregunta, bloque in data.items():
            html_content += (
                f'<p><b>{num_pregunta}</b>: {bloque.get('preg', '')}<br>'
                f'<b>Tipo</b>: {bloque.get('tipo')}</p>'
                )
            if 'img' in bloque:
                html_content += f'<br><img src="data:image/{bloque['img'].get('fmt')};base64, {bloque['img'].get('b64')}"/>'

            for letra, opcion in bloque['ops'].items():
                if bloque['tipo'] == 'match':
                    html_content += '<table border="1">'

                    for fila in bloque['ops'].values():
                        html_content += '<tr>'

                        for columna in fila.values():
                            html_content += f'<td>{(columna)}</td>'

                        html_content += '</tr>'
                    html_content += '</table>'
                    break
                elif bloque['tipo'] == 'ensayo':
                    for tipo in opcion.keys():
                        if tipo == 'txt':
                            html_content += (
                                f'<p style="margin-left:20px;">'
                                f'<b>{letra})</b> '
                                f'<span style="color:fuchsia">{opcion.get('txt')}</span><br>'
                                f'</p>'
                            )
                        elif tipo == 'tablas':
                            html_content += '<table border="1">'

                            for fila in opcion.get('tablas').values():
                                html_content += '<tr>'

                                for contenido in fila.values():
                                    if "img" in contenido:
                                        html_content += (
                                            f'<td>{contenido.get('txt')}</td>'
                                            f'<br>'
                                            f'<img src="data:image/{contenido['img'].get('fmt')};base64, {contenido['img'].get('b64')}"/>'
                                            )
                                        continue
                                    else:                                        
                                        html_content += f'<td>{contenido}</td>'
                                        continue

                                html_content += '</tr>'

                            html_content += '</table>'
                        elif tipo == 'img':
                            html_content += f'<img src="data:image/{opcion['img'].get('fmt')};base64, {opcion['img'].get('b64')}"/>'
                else:
                    color = 'green' if opcion.get("ok") is True else 'red' if opcion.get("ok") is False else 'FloralWhite'
                    html_content += f'<p style="margin-left:20px;">'
                    html_content += f'<b>{letra})</b> '
                    html_content += f'<span style="color:{color}">{opcion.get('txt')}</span><br>'
                    if 'img' in opcion:
                        html_content += f'<img src="data:image/{opcion['img'].get('fmt')};base64, {opcion['img'].get('b64')}"/><br>'
                    html_content += f'<span style="color:fuchsia">{opcion.get('retro')}</span></p>'

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