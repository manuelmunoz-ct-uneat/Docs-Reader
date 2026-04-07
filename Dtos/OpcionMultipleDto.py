from dataclasses import dataclass
from PreguntasDto import Pregunta
from RespuestaDto import Respuesta

@dataclass(kw_only=True)
class OpcionMultipleDto(Pregunta):
    respuestas: Respuesta




