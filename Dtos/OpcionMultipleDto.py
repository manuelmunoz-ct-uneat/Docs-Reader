from dataclasses import dataclass
from PreguntasDto import Pregunta

@dataclass(kw_only=True)
class OpcionMultipleDto(Pregunta):
    unica_respuesta: bool
    barajear_respuestas: bool
    respuestas: RespuestaMultiple

@dataclass
class RespuestaMultiple(dict):
    pregunta: str
    valor: str
    retroalimentacion: str


