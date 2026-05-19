from Dtos.PreguntasDto import PreguntaDto
from Dtos.RespuestasDto import RespuestaDto

class PreguntaOpcionMultipleDto(PreguntaDto):
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



