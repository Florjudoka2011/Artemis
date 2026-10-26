"""
Tests de validación Pydantic — capa 1 del arnés anti-mentiras.
Cada test tiene ID y referencia de requisito en la primera línea del docstring.
"""

import math

import pytest
from pydantic import ValidationError

from src.schemas.figuras import (
    AgujeroParams,
    CaraAgujero,
    CilindroParams,
    FiguraTipo,
    PrismaRectangularParams,
)


# ── T-100a/b: JSON válido completo ───────────────────────────────────────────
# Assertions distintas entre schemas → sufijos de letra en lugar de parametrize.


@pytest.mark.mvp
def test_prisma_valido_completo():
    """T-100a | 001/FR-005 — JSON válido completo de prisma pasa validación.

    Prueba: src/schemas/figuras.py::PrismaRectangularParams
    """
    p = PrismaRectangularParams(largo=100, ancho=60, alto=40)
    assert p.largo == 100.0
    assert p.ancho == 60.0
    assert p.alto == 40.0
    assert p.agujero is None
    assert p.vistas_iram is False


@pytest.mark.mvp
def test_cilindro_valido_completo():
    """T-100b | 001/FR-005 — JSON válido completo de cilindro pasa validación.

    Prueba: src/schemas/figuras.py::CilindroParams
    """
    c = CilindroParams(diametro=50, alto=80)
    assert c.diametro == 50.0
    assert c.alto == 80.0


# ── T-101: campo obligatorio faltante ───────────────────────────────────────


@pytest.mark.mvp
@pytest.mark.parametrize(
    "cls,kwargs,campo_faltante",
    [
        (PrismaRectangularParams, {"largo": 100, "ancho": 60}, "alto"),
        (CilindroParams, {"diametro": 50}, "alto"),
    ],
)
def test_campo_faltante(cls, kwargs, campo_faltante):
    """T-101 | 001/FR-005 — Campo obligatorio faltante es rechazado con campo identificado.

    Prueba: src/schemas/figuras.py::PrismaRectangularParams
    """
    with pytest.raises(ValidationError) as exc_info:
        cls(**kwargs)
    errors = exc_info.value.errors()
    campos = [e["loc"][0] for e in errors]
    assert campo_faltante in campos


# ── T-102: tipo incorrecto ───────────────────────────────────────────────────


@pytest.mark.mvp
def test_tipo_incorrecto_largo():
    """T-102 | 001/FR-005 — Tipo incorrecto (string en campo numérico) es rechazado.

    Prueba: src/schemas/figuras.py::PrismaRectangularParams
    """
    with pytest.raises(ValidationError) as exc_info:
        PrismaRectangularParams(largo="cien", ancho=60, alto=40)
    errors = exc_info.value.errors()
    campos = [e["loc"][0] for e in errors]
    assert "largo" in campos


# ── T-103: valor negativo ────────────────────────────────────────────────────


@pytest.mark.mvp
@pytest.mark.parametrize(
    "cls,kwargs",
    [
        (PrismaRectangularParams, {"largo": -10, "ancho": 60, "alto": 40}),
        (CilindroParams, {"diametro": -5, "alto": 80}),
    ],
)
def test_valor_negativo(cls, kwargs):
    """T-103 | 001/FR-005 — Valor negativo en dimensión es rechazado.

    Prueba: src/schemas/figuras.py::PrismaRectangularParams
    """
    with pytest.raises(ValidationError):
        cls(**kwargs)


# ── T-104: NaN e infinito ────────────────────────────────────────────────────


@pytest.mark.mvp
@pytest.mark.parametrize(
    "cls,kwargs",
    [
        (PrismaRectangularParams, {"largo": math.nan, "ancho": 60, "alto": 40}),
        (PrismaRectangularParams, {"largo": math.inf, "ancho": 60, "alto": 40}),
        (AgujeroParams, {"diametro": math.nan, "cara": CaraAgujero.superior}),
        (CilindroParams, {"diametro": math.nan, "alto": 80}),
    ],
)
def test_nan_infinito_rechazado(cls, kwargs):
    """T-104 | 001/FR-005 — Valor NaN o infinito es rechazado antes de construir.

    Prueba: src/schemas/figuras.py::PrismaRectangularParams
    """
    with pytest.raises(ValidationError):
        cls(**kwargs)


# ── T-105: valor = 0 ─────────────────────────────────────────────────────────


@pytest.mark.mvp
@pytest.mark.parametrize(
    "cls,kwargs",
    [
        (PrismaRectangularParams, {"largo": 100, "ancho": 60, "alto": 0}),
        (AgujeroParams, {"diametro": 0, "cara": CaraAgujero.superior}),
    ],
)
def test_valor_cero_rechazado(cls, kwargs):
    """T-105 | 001/FR-005 — Valor cero en dimensión es rechazado.

    Prueba: src/schemas/figuras.py::PrismaRectangularParams
    """
    with pytest.raises(ValidationError):
        cls(**kwargs)


# ── T-106: campo extra no definido ───────────────────────────────────────────


@pytest.mark.mvp
@pytest.mark.parametrize(
    "cls,kwargs",
    [
        (PrismaRectangularParams, {"largo": 100, "ancho": 60, "alto": 40, "color": "rojo"}),
        (AgujeroParams, {"diametro": 20, "cara": CaraAgujero.superior, "color": "rojo"}),
    ],
)
def test_campo_extra_rechazado(cls, kwargs):
    """T-106 | 001/FR-005 — Campo extra no definido en el esquema es rechazado (extra='forbid').

    Prueba: src/schemas/figuras.py::PrismaRectangularParams
    """
    with pytest.raises(ValidationError):
        cls(**kwargs)


# ── T-107: FiguraTipo desconocido ────────────────────────────────────────────


@pytest.mark.mvp
def test_figura_tipo_desconocida():
    """T-107 | 001/FR-005 — FiguraTipo desconocido es rechazado antes de construir.

    Prueba: src/schemas/figuras.py::FiguraTipo
    """
    with pytest.raises(ValueError):
        FiguraTipo("triangulo")


# ── T-108: CaraAgujero desconocida ───────────────────────────────────────────


@pytest.mark.mvp
def test_cara_agujero_desconocida():
    """T-108 | 001/FR-005 — CaraAgujero desconocida es rechazada antes de construir.

    Prueba: src/schemas/figuras.py::AgujeroParams
    """
    with pytest.raises(ValidationError):
        AgujeroParams(diametro=20, cara="diagonal")
