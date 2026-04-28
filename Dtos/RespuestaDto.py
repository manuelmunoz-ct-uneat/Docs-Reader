from dataclasses import dataclass
from typing import Dict

@dataclass
class OpcionDeRespuestaDto:
    txt: str
    retro: str
    img: str | None


@dataclass
class RespuestaDto:
    respuestas: Dict[str, OpcionDeRespuestaDto]

    @staticmethod
    def from_dict(data: dict) -> "RespuestaDto":
        respuestas = {
            key: OpcionDeRespuestaDto(**value)
            for key, value in data.items()
        }
        return RespuestaDto(respuestas=respuestas)