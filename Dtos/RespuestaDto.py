from dataclasses import dataclass

@dataclass
class RespuestaDto(dict):
    respuesta: str
    retroalimentacion: str
    img: str | None

    def __post_init__(self):
        self["respuesta"] = self.respuesta
        self["retroalimentacion"] = self.retroalimentacion