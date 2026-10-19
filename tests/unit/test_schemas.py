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


# ── T-100: JSON válido completo ──────────────────────────────────────────────


@pytest.mark.mvp
def test_prisma_valido_completo():
    """T-100 | 001/FR-005 — JSON válido completo pasa validación."""
    p = PrismaRectangularParams(largo=100, ancho=60, alto=40)
    assert p.largo == 100.0
    assert p.ancho == 60.0
    assert p.alto == 40.0
    assert p.agujero is None
    assert p.vistas_iram is False


@pytest.mark.mvp
def test_cilindro_valido_completo():
    """T-100 | 001/FR-005 — JSON válido de cilindro pasa validación."""
    c = CilindroParams(diametro=50, alto=80)
    assert c.diametro == 50.0
    assert c.alto == 80.0


# ── T-101: campo obligatorio faltante ───────────────────────────────────────


@pytest.mark.mvp
def test_campo_faltante_prisma():
    """T-101 | 001/FR-005 — Campo obligatorio faltante es rechazado con campo identificado."""
    with pytest.raises(ValidationError) as exc_info:
        PrismaRectangularParams(largo=100, ancho=60)  # falta alto
    errors = exc_info.value.errors()
    campos = [e["loc"][0] for e in errors]
    assert "alto" in campos


@pytest.mark.mvp
def test_campo_faltante_cilindro():
    """T-101 | 001/FR-005 — Campo obligatorio faltante en cilindro es rechazado."""
    with pytest.raises(ValidationError) as exc_info:
        CilindroParams(diametro=50)  # falta alto
    errors = exc_info.value.errors()
    campos = [e["loc"][0] for e in errors]
    assert "alto" in campos


# ── T-102: tipo incorrecto ───────────────────────────────────────────────────


@pytest.mark.mvp
def test_tipo_incorrecto_largo():
    """T-102 | 001/FR-005 — Tipo incorrecto (string en campo numérico) es rechazado."""
    with pytest.raises(ValidationError) as exc_info:
        PrismaRectangularParams(largo="cien", ancho=60, alto=40)
    errors = exc_info.value.errors()
    campos = [e["loc"][0] for e in errors]
    assert "largo" in campos


# ── T-103: valor negativo ────────────────────────────────────────────────────


@pytest.mark.mvp
def test_valor_negativo_largo():
    """T-103 | 001/FR-005 — Valor negativo en dimensión es rechazado."""
    with pytest.raises(ValidationError) as exc_info:
        PrismaRectangularParams(largo=-10, ancho=60, alto=40)
    errors = exc_info.value.errors()
    campos = [e["loc"][0] for e in errors]
    assert "largo" in campos


@pytest.mark.mvp
def test_valor_negativo_diametro():
    """T-103 | 001/FR-005 — Valor negativo en diámetro de cilindro es rechazado."""
    with pytest.raises(ValidationError):
        CilindroParams(diametro=-5, alto=80)


# ── T-104: NaN e infinito ────────────────────────────────────────────────────


@pytest.mark.mvp
def test_valor_nan():
    """T-104 | 001/FR-005 — Valor NaN es rechazado antes de construir."""
    with pytest.raises(ValidationError):
        PrismaRectangularParams(largo=math.nan, ancho=60, alto=40)


@pytest.mark.mvp
def test_valor_infinito():
    """T-104 | 001/FR-005 — Valor infinito es rechazado antes de construir."""
    with pytest.raises(ValidationError):
        PrismaRectangularParams(largo=math.inf, ancho=60, alto=40)


@pytest.mark.mvp
def test_valor_nan_agujero_diametro():
    """T-104 | 001/FR-005 — NaN en diametro de AgujeroParams es rechazado."""
    with pytest.raises(ValidationError):
        AgujeroParams(diametro=math.nan, cara=CaraAgujero.superior)


@pytest.mark.mvp
def test_valor_nan_cilindro():
    """T-104 | 001/FR-005 — NaN en CilindroParams es rechazado."""
    with pytest.raises(ValidationError):
        CilindroParams(diametro=math.nan, alto=80)


# ── T-105: valor = 0 ─────────────────────────────────────────────────────────


@pytest.mark.mvp
def test_valor_cero_alto():
    """T-105 | 001/FR-005 — Valor cero en dimensión es rechazado."""
    with pytest.raises(ValidationError) as exc_info:
        PrismaRectangularParams(largo=100, ancho=60, alto=0)
    errors = exc_info.value.errors()
    campos = [e["loc"][0] for e in errors]
    assert "alto" in campos


@pytest.mark.mvp
def test_valor_cero_diametro_agujero():
    """T-105 | 001/FR-005 — Diámetro de agujero = 0 es rechazado."""
    with pytest.raises(ValidationError):
        AgujeroParams(diametro=0, cara=CaraAgujero.superior)


# ── T-106: campo extra no definido ───────────────────────────────────────────


@pytest.mark.mvp
def test_campo_extra_prisma():
    """T-106 | 001/FR-005 — Campo extra no definido en el esquema es rechazado (extra='forbid')."""
    with pytest.raises(ValidationError) as exc_info:
        PrismaRectangularParams(largo=100, ancho=60, alto=40, color="rojo")
    errors = exc_info.value.errors()
    tipos = [e["type"] for e in errors]
    assert any("extra" in t for t in tipos)


@pytest.mark.mvp
def test_campo_extra_agujero():
    """T-106 | 001/FR-005 — Campo extra en AgujeroParams es rechazado."""
    with pytest.raises(ValidationError):
        AgujeroParams(diametro=20, cara=CaraAgujero.superior, profundidad=50)


# ── T-107: FiguraTipo desconocido ────────────────────────────────────────────


@pytest.mark.mvp
def test_figura_tipo_desconocida():
    """T-107 | 001/FR-005 — FiguraTipo desconocido es rechazado antes de construir."""
    with pytest.raises(ValueError):
        FiguraTipo("triangulo")


# ── T-108: CaraAgujero desconocida ───────────────────────────────────────────


@pytest.mark.mvp
def test_cara_agujero_desconocida():
    """T-108 | 001/FR-005 — CaraAgujero desconocida es rechazada antes de construir."""
    with pytest.raises(ValidationError):
        AgujeroParams(diametro=20, cara="diagonal")
