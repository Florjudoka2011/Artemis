"""
Tests de la receta cilindro — capa 2 del arnés anti-mentiras.
Volumen verificado con math.isclose(rel_tol=1e-6).
"""

import math

import pytest

from src.recipes.cilindro import construir
from src.schemas.figuras import CilindroParams


@pytest.mark.mvp
def test_cilindro_nominal():
    """T-10 | 001/FR-004 — Cilindro nominal produce volumen exacto.

    Prueba: src/recipes/cilindro.py::construir

    Valor esperado: 157079.633 = π × 25² × 80
    """
    params = CilindroParams(diametro=50, alto=80)
    solido = construir(params)
    volumen = solido.val().Volume()
    assert math.isclose(
        volumen, 157079.633, rel_tol=1e-6
    ), f"Volumen esperado 157079.633 mm³, obtenido {volumen}"


@pytest.mark.mvp
def test_cilindro_zmin_es_cero():
    """T-198 | 001/FR-004 — Cilindro tiene zmin=0 (convención: pieza sobre plano XY).

    Prueba: src/recipes/cilindro.py::construir

    Convención de posicionamiento: zmin=0, zmax=alto, centrado en X e Y.
    Garantiza que el visor Three.js muestre la pieza SOBRE la grilla, no
    atravesándola.
    """
    params = CilindroParams(diametro=50, alto=100)
    solido = construir(params)
    bb = solido.val().BoundingBox()
    assert math.isclose(
        bb.zmin, 0.0, abs_tol=1e-6
    ), f"zmin debe ser 0 (pieza sobre el plano XY). Obtenido: {bb.zmin}"
    assert math.isclose(
        bb.zmax, 100.0, rel_tol=1e-6
    ), f"zmax debe ser 100 (= alto). Obtenido: {bb.zmax}"
    # Centrado en X e Y: xmin = -radio, ymin = -radio
    radio = 25.0
    assert math.isclose(bb.xmin, -radio, abs_tol=1e-4), "Debe estar centrado en X"
    assert math.isclose(bb.ymin, -radio, abs_tol=1e-4), "Debe estar centrado en Y"
