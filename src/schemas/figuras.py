"""
Esquemas Pydantic de entrada — capa 1 de validación de Artemis.

Valida estructura y rangos básicos (> 0, tipos correctos, sin campos extra).
Las reglas geométricas de capa 2 (diámetro agujero vs cara, offset, etc.)
son responsabilidad de cada receta.
"""

import math
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class FiguraTipo(str, Enum):
    prisma_rectangular = "prisma_rectangular"
    cilindro = "cilindro"


class CaraAgujero(str, Enum):
    superior = "superior"
    inferior = "inferior"
    frontal = "frontal"
    trasera = "trasera"
    lateral_izq = "lateral_izq"
    lateral_der = "lateral_der"


class TipoAgujero(str, Enum):
    pasante = "pasante"
    ciego = "ciego"


class AgujeroParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    diametro: float
    cara: CaraAgujero
    tipo: TipoAgujero = TipoAgujero.pasante
    # u, v en coordenadas de borde (dibujo técnico):
    #   u = distancia desde el borde izquierdo de la cara (vista desde afuera)
    #   v = distancia desde la base (Z=0 para caras verticales; borde -Y para horizontales)
    # Rango válido: (radio, face_dim - radio) — validado en la receta.
    u: float = 0.0
    v: float = 0.0
    profundidad: Optional[float] = None

    @field_validator("diametro")
    @classmethod
    def diametro_positivo(cls, v: float) -> float:
        if not math.isfinite(v):
            raise ValueError("diametro debe ser un número finito")
        if v <= 0:
            raise ValueError("diametro debe ser > 0")
        return v

    @field_validator("profundidad")
    @classmethod
    def profundidad_positiva(cls, v: Optional[float]) -> Optional[float]:
        if v is not None:
            if not math.isfinite(v):
                raise ValueError("profundidad debe ser un número finito")
            if v <= 0:
                raise ValueError("profundidad debe ser > 0")
        return v

    @model_validator(mode="after")
    def validar_ciego_requiere_profundidad(self) -> "AgujeroParams":
        if self.tipo == TipoAgujero.ciego and self.profundidad is None:
            raise ValueError("tipo 'ciego' requiere profundidad > 0")
        if self.tipo == TipoAgujero.pasante and self.profundidad is not None:
            raise ValueError("tipo 'pasante' no debe tener profundidad")
        return self


class PrismaRectangularParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    largo: float
    ancho: float
    alto: float
    agujero: Optional[AgujeroParams] = None
    vistas_iram: bool = False

    @field_validator("largo", "ancho", "alto")
    @classmethod
    def dimensiones_positivas(cls, v: float) -> float:
        if not math.isfinite(v):
            raise ValueError("las dimensiones deben ser números finitos")
        if v <= 0:
            raise ValueError("las dimensiones deben ser > 0")
        return v


class CilindroParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    diametro: float
    alto: float
    agujero: Optional[AgujeroParams] = None
    vistas_iram: bool = False

    @field_validator("diametro", "alto")
    @classmethod
    def dimensiones_positivas(cls, v: float) -> float:
        if not math.isfinite(v):
            raise ValueError("las dimensiones deben ser números finitos")
        if v <= 0:
            raise ValueError("las dimensiones deben ser > 0")
        return v
