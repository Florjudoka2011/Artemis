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
def test_pydantic_v2_acepta_nan_sin_validator():
    """T-109 | 001/FR-005 — Pydantic v2 acepta NaN en float sin validator explícito.

    Prueba: src/schemas/figuras.py::PrismaRectangularParams
    """
    m = ModeloSinRestriccion(valor=math.nan)
    assert math.isnan(
        m.valor
    ), "Pydantic v2 NO rechaza NaN por defecto — se requiere math.isfinite() explícito"


@pytest.mark.mvp
def test_pydantic_v2_acepta_inf_sin_validator():
    """T-109 | 001/FR-005 — Pydantic v2 acepta infinito en float sin validator explícito.

    Prueba: src/schemas/figuras.py::PrismaRectangularParams
    """
    m = ModeloSinRestriccion(valor=math.inf)
    assert math.isinf(
        m.valor
    ), "Pydantic v2 NO rechaza inf por defecto — se requiere math.isfinite() explícito"


@pytest.mark.mvp
def test_pydantic_v2_acepta_neg_inf_sin_validator():
    """T-109 | 001/FR-005 — Pydantic v2 acepta -inf en float sin validator explícito.

    Prueba: src/schemas/figuras.py::PrismaRectangularParams
    """
    m = ModeloSinRestriccion(valor=-math.inf)
    assert (
        math.isinf(m.valor) and m.valor < 0
    ), "Pydantic v2 NO rechaza -inf por defecto — se requiere math.isfinite() explícito"
