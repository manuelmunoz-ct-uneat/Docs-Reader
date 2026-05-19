from .PreguntasDto import PreguntaDto
from .RespuestaEnsayoDto import RespuestaEnsayoDto

class PreguntaEnsayoDto(PreguntaDto):
    respuestas: RespuestaEnsayoDto

    @classmethod
    def from_dict(cls, data, id_pregunta, datosActividad):
        pregunta_base = PreguntaDto.from_dict(
            data,
            id_pregunta,
            datosActividad
        )

        respuestas = RespuestaEnsayoDto.from_dict(
            data.get("ops")
        )

        return cls(
            **pregunta_base.model_dump(),
            respuestas=respuestas
        )
