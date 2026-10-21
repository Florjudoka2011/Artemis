"""
Tests de la receta cilindro — capa 2 del arnés anti-mentiras.
Volumen verificado con math.isclose(rel_tol=1e-6).
"""

import math

import pytest

from src.schemas.figuras import CilindroParams
from src.recipes.cilindro import construir


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
