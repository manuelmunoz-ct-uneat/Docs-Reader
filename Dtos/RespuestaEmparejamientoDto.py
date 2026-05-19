from pydantic import BaseModel

class RespuestaEmparejamientoDto(BaseModel):
    respuestas: dict[str, dict[str, str]]

    @classmethod
    def from_dict(cls, data: dict):

        respuestas = {}

        for key, value in data.items():
            respuestas[key] = value

        return cls(respuestas=respuestas)