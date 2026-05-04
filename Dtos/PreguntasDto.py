from dataclasses import dataclass
from enum import Enum

@dataclass
class Pregunta:
    nombre_pregunta: str
    preg: str
    tipo: str
    img: dict[str, str] | None

    def __init__(self, data, id_pregunta, datosActividad):
        id_pregunta = str(id_pregunta).zfill(3)
        courseId = datosActividad.get("courseId")
        lang = datosActividad.get("courseLang")
        tipoDeActividad = self.setTipoActividad(datosActividad.get("courseActv"))

        self.nombre_pregunta = f'{courseId}-{lang}-X1-{tipoDeActividad}-{id_pregunta}'

        self.preg = data.get('preg')
        self.tipo = data.get('tipo')
        self.img = {
            'b64': data['img'].get('b64'),
            'fmt': data['img'].get('fmt')
            } if 'img' in data else None
    
    @staticmethod
    def from_dict(data, id_pregunta, datosActividad):
        return Pregunta(data, id_pregunta, datosActividad)
    
    @staticmethod
    def setTipoActividad(tipoActividad):
        if tipoActividad == "CO":
            return "E0"
        elif tipoActividad == "Test":
            return "Auto"
        if tipoActividad == "Tarea":
            return "Reflex"
        if tipoActividad == "Rec01":
            return "R1"
        if tipoActividad == "Rec02":
            return "R2"

        


