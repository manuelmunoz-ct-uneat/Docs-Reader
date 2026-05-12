from dataclasses import dataclass
from typing import Dict
from typing import Any


@dataclass
class RespuestaEmparejamientoDto:
    respuestas: Dict[str, dict[str, str]]

    def __init__(self, data: dict[str, Any]):
        self.respuestas = {}

        for key, value in data.items():
            print(value)
            self.respuestas[key] = value
    
    

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data)
    


        