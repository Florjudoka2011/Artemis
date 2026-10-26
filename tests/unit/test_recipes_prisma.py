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


@pytest.mark.mvp
def test_prisma_agujero_pasante_volumen():
    """T-04 | 001/FR-002 — Prisma 100×60×40 con agujero Ø20 centrado → volumen correcto.

    Prueba: src/recipes/prisma_rectangular.py::construir

    Valor esperado: 240000 − π × 10² × 40 = 227433.629 mm³
    """
    from src.schemas.figuras import AgujeroParams, CaraAgujero

    params = PrismaRectangularParams(
        largo=100,
        ancho=60,
        alto=40,
        agujero=AgujeroParams(diametro=20, cara=CaraAgujero.superior),
    )
    solido = construir(params)
    volumen = solido.val().Volume()
    esperado = 240000 - math.pi * 10**2 * 40
    assert math.isclose(
        volumen, esperado, rel_tol=1e-6
    ), f"Volumen esperado {esperado:.3f} mm³, obtenido {volumen}"


@pytest.mark.mvp
def test_prisma_agujero_diametro_mayor_o_igual_lado_menor_es_rechazado():
    """T-05 | 001/FR-002 — Agujero con diámetro ≥ lado menor (ancho=60) → rechazado.

    Prueba: src/recipes/prisma_rectangular.py::construir

    Regla geométrica: diámetro del agujero debe ser < min(largo, ancho) de la cara.
    """
    from src.schemas.figuras import AgujeroParams, CaraAgujero

    params = PrismaRectangularParams(
        largo=100,
        ancho=60,
        alto=40,
        agujero=AgujeroParams(diametro=60, cara=CaraAgujero.superior),
    )
    with pytest.raises(ValueError, match="[Dd]i[aá]metro"):
        construir(params)


@pytest.mark.mvp
def test_prisma_agujero_borde_justo_por_debajo_del_limite_pasa():
    """T-06 | 001/FR-002 — Agujero con diámetro justo por debajo del límite pasa.

    Prueba: src/recipes/prisma_rectangular.py::construir

    Borde: diámetro = lado_menor − ε (debe pasar).
    """
    from src.schemas.figuras import AgujeroParams, CaraAgujero

    lado_menor = 60.0
    diametro_borde = lado_menor - 0.001
    params = PrismaRectangularParams(
        largo=100,
        ancho=60,
        alto=40,
        agujero=AgujeroParams(diametro=diametro_borde, cara=CaraAgujero.superior),
    )
    solido = construir(params)
    assert solido is not None


@pytest.mark.mvp
@pytest.mark.parametrize(
    "cara,lado_menor",
    [
        ("frontal", 40),  # min(ancho=60, alto=40)
        ("trasera", 40),
        ("lateral_izq", 40),  # min(largo=100, alto=40)
        ("lateral_der", 40),
    ],
)
def test_prisma_agujero_otras_caras(cara, lado_menor):
    """T-08 | 001/FR-002 — Agujero en caras no-superior produce sólido válido.

    Prueba: src/recipes/prisma_rectangular.py::construir

    Cubre las ramas elif/else de cara frontal/trasera/lateral.
    """
    from src.schemas.figuras import AgujeroParams, CaraAgujero

    params = PrismaRectangularParams(
        largo=100,
        ancho=60,
        alto=40,
        agujero=AgujeroParams(diametro=lado_menor / 2, cara=CaraAgujero[cara]),
    )
    solido = construir(params)
    assert solido is not None


@pytest.mark.mvp
def test_prisma_agujero_exactamente_en_limite_es_rechazado():
    """T-07 | 001/FR-002 — Agujero con diámetro exactamente igual al lado menor → rechazado.

    Prueba: src/recipes/prisma_rectangular.py::construir
    """
    from src.schemas.figuras import AgujeroParams, CaraAgujero

    params = PrismaRectangularParams(
        largo=100,
        ancho=60,
        alto=40,
        agujero=AgujeroParams(diametro=60.0, cara=CaraAgujero.superior),
    )
    with pytest.raises(ValueError, match="[Dd]i[aá]metro"):
        construir(params)
