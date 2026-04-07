from dataclasses import dataclass
from PreguntasDto import Pregunta
from Dtos.RespuestaConValor import RespuestaConValor

@dataclass(kw_only=True)
class VerdaderoFalsoDto(Pregunta):
    respuestas: RespuestaConValor

