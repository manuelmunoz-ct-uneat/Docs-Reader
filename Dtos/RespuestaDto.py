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

    def __init__(self, data: dict[str, Any]):
        respuestas: Dict[str, OpcionDeRespuestaDto] = {}
        for key in data.keys():
            respuestas.update({
                key: OpcionDeRespuestaDto(
                    data.get("txt", ""),
                    data.get("retro", ""),
                    data.get("ok", ""),
                    data.get("img")
                    )
        })

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data)
        