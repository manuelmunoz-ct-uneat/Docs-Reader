from dataclasses import dataclass
from typing import Dict
from typing import Any

@dataclass
class OpcionDeRespuestaDto:
    txt: str
    retro: str
    ok: bool
    img: dict[str, str] | None


@dataclass
class RespuestaDto:
    respuestas: Dict[str, OpcionDeRespuestaDto]

    def __init__(self, data: dict[str, Any]):
        self.respuestas = {}

        for key, value in data.items():
            self.respuestas[key] = OpcionDeRespuestaDto(
                value.get("txt", ""),
                value.get("retro", ""),
                value.get("ok", False),
                value.get("img", None)
            )

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data)
        