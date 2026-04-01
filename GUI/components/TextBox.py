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
                if "resp" in opcion:
                    html_content += (
                        f'<p style="margin-left:20px;">'
                        f'<b>{letra})</b> '
                        f'<span style="color:FloralWhite">{html.escape(str(opcion["txt"]))} -> {html.escape(str(opcion["resp"]))}</span>'
                        f'</p>'
                    )
                else:
                    color = "green" if opcion["ok"] is True else "red" if opcion["ok"] is False else "black"
                    html_content += (
                        f'<p style="margin-left:20px;">'
                        f'<b>{letra})</b> '
                        f'<span style="color:{color}">{html.escape(str(opcion["txt"]))}</span>'
                        f'</p>'
                    )

        self.setHtml(html_content)

    def _is_hex_color(self, value: str):
        if len(value) == 6:
            try:
                int(value, 16)
                return True
            except ValueError:
                return False
        return False