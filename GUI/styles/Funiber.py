class FuniberColors:
    styles = """
            Button {
                border: 1px solid #2c2c2c;
                border-radius: 6px;
                padding: 6px 12px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #f6f6f6, stop:1 #e9e9e9);
                color: #111;
            }
            Button:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #ffffff, stop:1 #f0f0f0);
            }
            Button:pressed {
                background: #dcdcdc;
            }
        """