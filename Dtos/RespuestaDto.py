from dataclasses import dataclass

@dataclass
class RespuestaDto(dict):
    respuesta: str
    retroalimentacion: str

    def __post_init__(self):
        self["respuesta"] = self.respuesta
        self["retroalimentacion"] = self.retroalimentacion