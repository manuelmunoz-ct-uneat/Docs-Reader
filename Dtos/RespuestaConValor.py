from dataclasses import dataclass
from RespuestaDto import RespuestaDto

@dataclass(kw_only=True)
class RespuestaConValorDto(RespuestaDto):
    valor: str



