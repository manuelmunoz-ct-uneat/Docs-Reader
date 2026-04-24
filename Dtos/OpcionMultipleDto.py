from dataclasses import dataclass
from PreguntasDto import Pregunta
from Dtos.RespuestaConValor import RespuestaConValorDto

@dataclass(kw_only=True)
class OpcionMultipleDto(Pregunta):
    respuestas: RespuestaConValorDto

