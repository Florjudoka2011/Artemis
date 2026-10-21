"""
Verifica el comportamiento REAL de Pydantic v2 con NaN e infinito en campos float
SIN restricciones explícitas.

Resultado esperado: Pydantic v2 acepta NaN e inf por defecto (NO los rechaza).
Por eso se necesita el validator explícito con math.isfinite().

T-109 | 001/FR-005
"""

import math

import pytest
from pydantic import BaseModel


class ModeloSinRestriccion(BaseModel):
    valor: float


@pytest.mark.mvp
@pytest.mark.parametrize(
    "valor,check",
    [
        (math.nan, math.isnan),
        (math.inf, math.isinf),
        (-math.inf, lambda v: math.isinf(v) and v < 0),
    ],
)
def test_pydantic_v2_acepta_valor_especial_sin_validator(valor, check):
    """T-109 | 001/FR-005 — Pydantic v2 acepta NaN/inf/-inf en float sin validator explícito.

    Prueba: src/schemas/figuras.py::PrismaRectangularParams
    """
    m = ModeloSinRestriccion(valor=valor)
    assert check(
        m.valor
    ), "Pydantic v2 NO rechaza estos valores por defecto — se requiere math.isfinite() explícito"
