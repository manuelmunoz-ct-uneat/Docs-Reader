from dataclasses import dataclass
from Dtos.PreguntasDto import Pregunta
from Dtos.RespuestaDto import RespuestaDto

@dataclass
class OpcionMultipleDto(Pregunta):
    respuestas: RespuestaDto

    def __init__(self, data, id_pregunta):
        super().__init__(data, id_pregunta)
        self.respuestas = RespuestaDto.from_dict(data.get('ops'))

    @classmethod
    def from_dict(cls, data, id_pregunta):
        return OpcionMultipleDto(data, id_pregunta)



