from pydantic import BaseModel
from typing import Dict

class OpcionDeRespuestaEnsayoDto(BaseModel):
    txt: str | dict[str, str]
    tabla: dict[str, dict] | None
    img: dict[str, str] | None = None


class RespuestaEnsayoDto(BaseModel):
    respuestas: Dict[str, OpcionDeRespuestaEnsayoDto]

    @classmethod
    def from_dict(cls, data: dict):

        respuestas = {}

        for key, value in data.items():

            respuestas[key] = OpcionDeRespuestaEnsayoDto(
                txt=value.get("txt"),
                tabla=value.get("tablas"),
                img=value.get("img", None)
            )

        return cls(respuestas=respuestas)