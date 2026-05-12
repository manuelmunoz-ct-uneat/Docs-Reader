from dataclasses import dataclass
from typing import Dict
from typing import Any

@dataclass
class OpcionDeRespuestaEnsayoDto:
    txt: str
    tabla: dict[str, dict[str, str]]
    img: dict[str, str] | None


@dataclass
class RespuestaEnsayoDto:
    respuestas: Dict[str, OpcionDeRespuestaEnsayoDto]

    def __init__(self, data: dict[str, Any]):
        self.respuestas = {}

        for key, value in data.items():
            self.respuestas[key] = OpcionDeRespuestaEnsayoDto(
                value.get("txt", ""),
                value.get("tablas", ""),
                value.get("img", None)
            )

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data)
        