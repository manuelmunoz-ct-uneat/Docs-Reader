from dataclasses import dataclass
from RespuestaDto import Respuesta

@dataclass(kw_only=True)
class RespuestaConValor(Respuesta):
    valor: str



