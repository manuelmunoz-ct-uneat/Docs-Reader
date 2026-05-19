from .PreguntasDto import PreguntaDto
from .RespuestaEmparejamientoDto import RespuestaEmparejamientoDto

class PreguntaEmparejamientoDto(PreguntaDto):

    respuestas: RespuestaEmparejamientoDto

    @classmethod
    def from_dict(cls, data, id_pregunta, datosActividad):
        pregunta_base = PreguntaDto.from_dict(
            data,
            id_pregunta,
            datosActividad
        )

        respuestas = RespuestaEmparejamientoDto.from_dict(
            data.get("ops")
        )

        return cls(
            **pregunta_base.model_dump(),
            respuestas=respuestas
        )

