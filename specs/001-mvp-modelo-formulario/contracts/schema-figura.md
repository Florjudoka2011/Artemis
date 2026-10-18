# Contract: Schema de entrada — Solicitud de Generación

**Module**: `src/schemas/figuras.py`
**Date**: 2026-10-18

Este schema es el contrato entre la interfaz (formulario Gradio o conector de IA futuro)
y el motor de recetas. Todo lo que pase esta validación puede llegar a una receta.

---

## Esquema Pydantic (referencia normativa)

```python
from enum import Enum
from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional

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
    def diametro_positivo(cls, v):
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
    def dimensiones_positivas(cls, v):
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
    def dimensiones_positivas(cls, v):
        if v <= 0:
            raise ValueError("las dimensiones deben ser > 0")
        return v
```

---

## Reglas de validación Pydantic (capa 1)

| Test | Condición | Resultado |
|---|---|---|
| T-100 | JSON válido completo | Pasa; llega a la receta |
| T-101 | Campo obligatorio faltante | Rechazado: campo identificado |
| T-102 | Tipo incorrecto (string en numérico) | Rechazado |
| T-103 | Valor negativo | Rechazado |
| T-104 | NaN o infinito | Rechazado |
| T-105 | Valor = 0 | Rechazado |
| T-106 | Campo extra no definido | Rechazado (`extra="forbid"`) |
| T-107 | FiguraTipo desconocido | Rechazado |
| T-108 | CaraAgujero desconocida | Rechazado |

---

## Lo que Pydantic NO valida (capa 2 — receta)

- Diámetro de agujero ≥ lado menor de la cara
- Posición del agujero que sale fuera de la cara
- Diámetro de agujero ≥ diámetro del cilindro
- Cara no compatible con la figura (ej. cara `frontal` en cilindro)

Estas reglas se verifican dentro de cada receta y generan errores descriptivos antes de
invocar CadQuery.
