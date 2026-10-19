"""
Esquemas Pydantic de entrada — capa 1 de validación de Artemis.

Valida estructura y rangos básicos (> 0, tipos correctos, sin campos extra).
Las reglas geométricas de capa 2 (diámetro agujero vs cara, offset, etc.)
son responsabilidad de cada receta.
"""

import math
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


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


class AgujeroParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    diametro: float
    cara: CaraAgujero
    offset_x: float = 0.0
    offset_y: float = 0.0

    @field_validator("diametro")
    @classmethod
    def diametro_positivo(cls, v: float) -> float:
        if not math.isfinite(v):
            raise ValueError("diametro debe ser un número finito")
        if v <= 0:
            raise ValueError("diametro debe ser > 0")
        return v


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
