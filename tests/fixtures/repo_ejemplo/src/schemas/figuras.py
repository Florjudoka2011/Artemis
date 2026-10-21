"""Schemas de validación para el repo de prueba."""

from pydantic import BaseModel, field_validator
import math


class PrismaParams(BaseModel):
    largo: float
    ancho: float
    alto: float

    @field_validator("largo", "ancho", "alto")
    @classmethod
    def positivos(cls, v: float) -> float:
        if not math.isfinite(v):
            raise ValueError("debe ser finito")
        if v <= 0:
            raise ValueError("debe ser > 0")
        return v
