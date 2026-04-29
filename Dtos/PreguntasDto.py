from dataclasses import dataclass

@dataclass
class Pregunta:
    nombre_pregunta: str
    preg: str
    tipo: str
    img: dict[str, str] | None

    def __init__(self, data, id_pregunta):
        id_pregunta = str(id_pregunta).zfill(3)
        self.nombre_pregunta = f'PRB2547-POr-X01-{id_pregunta}'

        self.preg = data.get('preg')
        self.tipo = data.get('tipo')
        self.img = {
            'b64': data['img'].get('b64'),
            'fmt': data['img'].get('fmt')
            } if 'img' in data else None
    
    @staticmethod
    def from_dict(data, id_pregunta):
        return Pregunta(data, id_pregunta)
        


