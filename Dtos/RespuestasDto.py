from pydantic import BaseModel
from typing import Dict
from typing import Any

class OpcionDeRespuestaDto(BaseModel):
    txt: str | dict[str, str]
    retro: str
    ok: bool
    img: dict[str, str] | None


class RespuestaDto(BaseModel):
    respuestas: Dict[str, OpcionDeRespuestaDto]


    @classmethod
    def from_dict(cls, data: dict):
        respuestas = {}
        for key, value in data.items():
            respuestas[key] = OpcionDeRespuestaDto(
                txt=value.get("moodle"),
                retro=value.get("retro", ""),
                ok=value.get("ok", False),
                img=value.get("img", None)
            )

        return cls(respuestas=respuestas)
        