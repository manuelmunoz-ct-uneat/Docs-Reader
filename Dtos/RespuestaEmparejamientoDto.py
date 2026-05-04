from .TablaDto import TablaDto
from dataclasses import dataclass
from typing import Dict
from typing import Any


@dataclass
class RespuestaEmparejamientoDto:
    respuestas: Dict[str, TablaDto]

    def __init__(self, data: dict[str, Any]):
        self.respuestas = {}

        for key, value in data.items():
            self.respuestas[key] = TablaDto(value)
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(data)
    


        