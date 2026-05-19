from .PreguntasDto import PreguntaDto
from .RespuestasDto import RespuestaDto

class PreguntaVerdaderoFalsoDto(PreguntaDto):
    respuestas: RespuestaDto


    @classmethod
    def from_dict(cls, data, id_pregunta, datosActividad):
        pregunta_base = PreguntaDto.from_dict(
            data,
            id_pregunta,
            datosActividad
        )

        respuestas = RespuestaDto.from_dict(
            data.get("ops")
        )

        return cls(
            **pregunta_base.model_dump(),
            respuestas=respuestas
        )
    

        


