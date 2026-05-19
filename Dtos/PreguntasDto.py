from pydantic import BaseModel
from .CourseDataDto import CourseDataDto

class PreguntaDto(BaseModel):
    nombre_pregunta: str
    preg: str
    tipo: str
    img: dict[str, str] | None = None

    @classmethod
    def from_dict(cls, jsonData, numeroPregunta, datosActividad: CourseDataDto):

        numeroPregunta = str(numeroPregunta).zfill(3)

        courseId = datosActividad.courseId
        lang = datosActividad.courseLang
        tipoDeActividad = cls.setTipoActividad(datosActividad.courseActv)

        nombre_pregunta = f'{courseId}-{lang}-X1-{tipoDeActividad}-{numeroPregunta}'

        return cls(
            nombre_pregunta=nombre_pregunta,
            preg=jsonData.get('preg'),
            tipo=jsonData.get('tipo'),
            img={
                'b64': jsonData['img'].get('b64'),
                'fmt': jsonData['img'].get('fmt')
            } if 'img' in jsonData else None
        )

    @staticmethod
    def setTipoActividad(tipoActividad):
        if tipoActividad == "CO":
            return "E0"
        elif tipoActividad == "Test":
            return "Auto"
        elif tipoActividad == "Tarea":
            return "Reflex"
        elif tipoActividad == "Rec01":
            return "R1"
        elif tipoActividad == "Rec02":
            return "R2"