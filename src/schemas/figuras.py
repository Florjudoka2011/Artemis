"""
Esquemas Pydantic de entrada — capa 1 de validación de Artemis.

Valida estructura y rangos básicos (> 0, tipos correctos, sin campos extra).
Las reglas geométricas de capa 2 (diámetro agujero vs cara, offset, etc.)
son responsabilidad de cada receta.
"""

import math
from collections import defaultdict
from enum import Enum
from typing import Literal, Optional

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
    """Esquema legacy — sigue siendo usado por CilindroParams."""

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


class OperacionAgujeroParams(BaseModel):
    """Parámetros de una operación de agujero en un prisma rectangular.

    tipo: discriminador para futuras operaciones (chaflán, redondeo, etc.)
    cara: qué cara del prisma se perfora
    subtipo: pasante (corta de lado a lado) o ciego (profundidad fija)
    u: distancia desde el borde izquierdo de la cara (mm)
    v: distancia desde la base de la cara (mm)
    profundidad: solo usado cuando subtipo == "ciego" (mm)
    """

    model_config = ConfigDict(extra="forbid")

    tipo: Literal["agujero"] = "agujero"
    diametro: float
    cara: CaraAgujero
    subtipo: TipoAgujero = TipoAgujero.pasante
    u: float = 0.0
    v: float = 0.0
    profundidad: float = 0.0

    @field_validator("diametro")
    @classmethod
    def diametro_positivo(cls, v: float) -> float:
        if not math.isfinite(v):
            raise ValueError("diametro debe ser un número finito")
        if v <= 0:
            raise ValueError("diametro debe ser > 0")
        return v


OperacionParams = OperacionAgujeroParams

# Dimensiones (W, H) de cada cara dado un prisma (largo, ancho, alto).
# W = dimensión horizontal de la cara vista desde el exterior.
# H = dimensión vertical (desde la base hasta el tope de la cara).
_CARA_DIMS = {
    CaraAgujero.superior: lambda lg, an, al: (lg, an),
    CaraAgujero.inferior: lambda lg, an, al: (lg, an),
    CaraAgujero.frontal: lambda lg, an, al: (lg, al),
    CaraAgujero.trasera: lambda lg, an, al: (lg, al),
    CaraAgujero.lateral_izq: lambda lg, an, al: (an, al),
    CaraAgujero.lateral_der: lambda lg, an, al: (an, al),
}


class PrismaRectangularParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    largo: float
    ancho: float
    alto: float
    operaciones: list[OperacionAgujeroParams] = []
    version_esquema: int = 2
    vistas_iram: bool = False

    @field_validator("largo", "ancho", "alto")
    @classmethod
    def dimensiones_positivas(cls, v: float) -> float:
        if not math.isfinite(v):
            raise ValueError("las dimensiones deben ser números finitos")
        if v <= 0:
            raise ValueError("las dimensiones deben ser > 0")
        return v

    @model_validator(mode="after")
    def validar_operaciones(self) -> "PrismaRectangularParams":
        ops = self.operaciones
        if len(ops) > 20:
            raise ValueError(f"Máximo 20 operaciones por pieza; se recibieron {len(ops)}")

        # Agrupar agujeros por cara para validar distancias
        por_cara: dict[CaraAgujero, list[tuple[int, OperacionAgujeroParams]]] = defaultdict(list)
        for idx, op in enumerate(ops):
            if op.tipo == "agujero":
                W, H = _CARA_DIMS[op.cara](self.largo, self.ancho, self.alto)
                r = op.diametro / 2
                # Verificar que el agujero cabe dentro de la cara
                if op.u < r or op.u > W - r:
                    raise ValueError(
                        f"Fila {idx + 1}: agujero Ø{op.diametro} no cabe en cara "
                        f"{op.cara.value} (u={op.u}, cara ancho={W}). "
                        f"Rango válido: [{r:.1f}, {W - r:.1f}]"
                    )
                if op.v < r or op.v > H - r:
                    raise ValueError(
                        f"Fila {idx + 1}: agujero Ø{op.diametro} no cabe en cara "
                        f"{op.cara.value} (v={op.v}, cara alto={H}). "
                        f"Rango válido: [{r:.1f}, {H - r:.1f}]"
                    )
                por_cara[op.cara].append((idx, op))

        # Validar distancia mínima entre agujeros en la misma cara
        for cara, agujeros in por_cara.items():
            for i, (idx1, op1) in enumerate(agujeros):
                for idx2, op2 in agujeros[i + 1 :]:
                    dist = math.sqrt((op2.u - op1.u) ** 2 + (op2.v - op1.v) ** 2)
                    min_dist = op1.diametro / 2 + op2.diametro / 2 + 1.0
                    if dist <= min_dist:
                        raise ValueError(
                            f"Filas {idx1 + 1} y {idx2 + 1}: agujeros superpuestos en "
                            f"cara {cara.value}. "
                            f"Distancia entre centros {dist:.2f} mm < mínimo {min_dist:.2f} mm."
                        )

        return self


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
