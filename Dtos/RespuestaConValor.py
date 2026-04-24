from dataclasses import dataclass
from RespuestaDto import RespuestaDto

@dataclass(kw_only=True)
class RespuestaConValorDto(RespuestaDto):
    valor: str

    def __post_init__(self):
        super().__post_init__()
        self["valor"] = self.valor
