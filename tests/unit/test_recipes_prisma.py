"""
Tests de la receta prisma_rectangular — capa 2 del arnés anti-mentiras.
Volumen verificado con math.isclose(rel_tol=1e-6).
"""

import math

import pytest
from pydantic import ValidationError

from src.schemas.figuras import PrismaRectangularParams
from src.recipes.prisma_rectangular import construir


@pytest.mark.mvp
def test_prisma_nominal():
    """T-01 | 001/FR-004 — Prisma nominal produce volumen exacto.

    Prueba: src/recipes/prisma_rectangular.py::construir

    Valor esperado: 240000 = 100 × 60 × 40
    """
    params = PrismaRectangularParams(largo=100, ancho=60, alto=40)
    solido = construir(params)
    volumen = solido.val().Volume()
    assert math.isclose(
        volumen, 240000, rel_tol=1e-6
    ), f"Volumen esperado 240000 mm³, obtenido {volumen}"


@pytest.mark.mvp
def test_prisma_parametro_cero():
    """T-02 | 001/FR-005 — Parámetro cero en prisma es rechazado antes de construir.

    Prueba: src/schemas/figuras.py::PrismaRectangularParams
    """
    with pytest.raises(ValidationError):
        PrismaRectangularParams(largo=0, ancho=60, alto=40)


@pytest.mark.mvp
def test_prisma_parametro_negativo():
    """T-03 | 001/FR-005 — Parámetro negativo en prisma es rechazado antes de construir.

    Prueba: src/schemas/figuras.py::PrismaRectangularParams
    """
    with pytest.raises(ValidationError):
        PrismaRectangularParams(largo=-10, ancho=60, alto=40)


@pytest.mark.mvp
def test_prisma_zmin_es_cero():
    """T-197 | 001/FR-004 — Prisma tiene zmin=0 (convención: pieza sobre plano XY).

    Prueba: src/recipes/prisma_rectangular.py::construir

    Convención de posicionamiento: zmin=0, zmax=alto, centrado en X e Y.
    Garantiza que el visor Three.js muestre la pieza SOBRE la grilla, no
    atravesándola.
    """
    params = PrismaRectangularParams(largo=100, ancho=60, alto=40)
    solido = construir(params)
    bb = solido.val().BoundingBox()
    assert math.isclose(
        bb.zmin, 0.0, abs_tol=1e-6
    ), f"zmin debe ser 0 (pieza sobre el plano XY). Obtenido: {bb.zmin}"
    assert math.isclose(
        bb.zmax, 40.0, rel_tol=1e-6
    ), f"zmax debe ser 40 (= alto). Obtenido: {bb.zmax}"
    assert math.isclose(bb.xmin, -50.0, abs_tol=1e-6), "Debe estar centrado en X"
    assert math.isclose(bb.ymin, -30.0, abs_tol=1e-6), "Debe estar centrado en Y"
