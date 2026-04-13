from PySide6.QtWidgets import QTextBrowser
import html

class JsonFormater(QTextBrowser):
    def __init__(self, parent=None):
            super().__init__(parent)
            self.setReadOnly(True)

    def setJson(self, data: dict):
        html_content = ""

        for num_pregunta, bloque in data.items():
            html_content += f"<p><b>Pregunta {num_pregunta}</b>: {html.escape(str(bloque['preg']))}</p>"

            for letra, opcion in bloque["ops"].items():
                if "f0" in bloque["ops"]: #TODO cambiar a verificacion por tipo de pregunta
                    html_content += '<table border="1">'

                    for fila_id, fila in bloque["ops"].items():
                        html_content += '<tr>'

                        for columna_id, columna in fila.items():
                            html_content += f'<td>{html.escape(str(columna["txt"]))}</td>'

                        html_content += '</tr>'

                    html_content += '</table>'
                    break
                else:
                    color = "green" if opcion["ok"] is True else "red" if opcion["ok"] is False else "FloralWhite"
                    html_content += (
                        f'<p style="margin-left:20px;">'
                        f'<b>{letra})</b> '
                        f'<span style="color:{color}">{html.escape(str(opcion["txt"]))}</span><br>'
                        f'<span style="color:fuchsia">{html.escape(str(opcion["retro"]))}</span>'
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