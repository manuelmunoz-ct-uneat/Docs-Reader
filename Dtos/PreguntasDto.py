from dataclasses import dataclass
from .CourseDataDto import CourseDataDto

@dataclass
class PreguntaDto:
    nombre_pregunta: str
    preg: str
    tipo: str
    img: dict[str, str] | None

    def __init__(self, jsonData, numeroPregunta, datosActividad: CourseDataDto):
        numeroPregunta = str(numeroPregunta).zfill(3)
        courseId = datosActividad.courseId
        lang = datosActividad.courseLang
        tipoDeActividad = self.setTipoActividad(datosActividad.courseActv)

        self.nombre_pregunta = f'{courseId}-{lang}-X1-{tipoDeActividad}-{numeroPregunta}'

        self.preg = jsonData.get('preg')
        self.tipo = jsonData.get('tipo')
        self.img = {
            'b64': jsonData['img'].get('b64'),
            'fmt': jsonData['img'].get('fmt')
            } if 'img' in jsonData else None
    
    @classmethod
    def from_dict(cls, jsonData, id_pregunta, datosActividad):
        return cls(jsonData, id_pregunta, datosActividad)
    
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

        


