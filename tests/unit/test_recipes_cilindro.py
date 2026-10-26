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


@pytest.mark.mvp
def test_cilindro_agujero_coaxial_volumen():
    """T-11 | 001/FR-002 — Cilindro Ø50×80 con agujero coaxial Ø20 → volumen correcto.

    Prueba: src/recipes/cilindro.py::construir

    Valor esperado: π × (25² − 10²) × 80 = 131946.891 mm³
    """
    from src.schemas.figuras import AgujeroParams, CaraAgujero

    params = CilindroParams(
        diametro=50,
        alto=80,
        agujero=AgujeroParams(diametro=20, cara=CaraAgujero.superior),
    )
    solido = construir(params)
    volumen = solido.val().Volume()
    esperado = math.pi * (25**2 - 10**2) * 80
    assert math.isclose(
        volumen, esperado, rel_tol=1e-6
    ), f"Volumen esperado {esperado:.3f} mm³, obtenido {volumen}"


@pytest.mark.mvp
def test_cilindro_agujero_diametro_mayor_o_igual_diametro_cilindro_es_rechazado():
    """T-12 | 001/FR-002 — Agujero con diámetro ≥ diámetro del cilindro (50) → rechazado.

    Prueba: src/recipes/cilindro.py::construir

    Regla geométrica: diámetro del agujero debe ser < diámetro del cilindro.
    """
    from src.schemas.figuras import AgujeroParams, CaraAgujero

    params = CilindroParams(
        diametro=50,
        alto=80,
        agujero=AgujeroParams(diametro=50, cara=CaraAgujero.superior),
    )
    with pytest.raises(ValueError, match="[Dd]i[aá]metro"):
        construir(params)


@pytest.mark.mvp
def test_cilindro_agujero_borde_justo_por_debajo_del_limite_pasa():
    """T-13 | 001/FR-002 — Agujero con diámetro justo por debajo del límite pasa.

    Prueba: src/recipes/cilindro.py::construir

    Borde: diámetro = diámetro_cilindro − ε (debe pasar).
    """
    from src.schemas.figuras import AgujeroParams, CaraAgujero

    diametro_borde = 50.0 - 0.001
    params = CilindroParams(
        diametro=50,
        alto=80,
        agujero=AgujeroParams(diametro=diametro_borde, cara=CaraAgujero.superior),
    )
    solido = construir(params)
    assert solido is not None


@pytest.mark.mvp
def test_cilindro_agujero_exactamente_en_limite_es_rechazado():
    """T-14 | 001/FR-002 — Agujero con diámetro exactamente igual al del cilindro → rechazado.

    Prueba: src/recipes/cilindro.py::construir
    """
    from src.schemas.figuras import AgujeroParams, CaraAgujero

    params = CilindroParams(
        diametro=50,
        alto=80,
        agujero=AgujeroParams(diametro=50.0, cara=CaraAgujero.superior),
    )
    with pytest.raises(ValueError, match="[Dd]i[aá]metro"):
        construir(params)


@pytest.mark.mvp
def test_cilindro_agujero_ciego_volumen():
    """T-23 | 001/FR-002 — Cilindro Ø50×80 con agujero ciego Ø20, prof=25 → volumen correcto.

    Prueba: src/recipes/cilindro.py::construir

    Valor esperado: π × 25² × 80 − π × 10² × 25
    = π × (625 × 80 − 100 × 25) = π × (50000 − 2500) = π × 47500 = 149225.652 mm³
    """
    from src.schemas.figuras import AgujeroParams, CaraAgujero, TipoAgujero

    params = CilindroParams(
        diametro=50,
        alto=80,
        agujero=AgujeroParams(
            diametro=20,
            cara=CaraAgujero.superior,
            tipo=TipoAgujero.ciego,
            profundidad=25.0,
        ),
    )
    solido = construir(params)
    volumen = solido.val().Volume()
    esperado = math.pi * 25**2 * 80 - math.pi * 10**2 * 25
    assert math.isclose(
        volumen, esperado, rel_tol=1e-6
    ), f"Volumen esperado {esperado:.3f} mm³, obtenido {volumen}"


@pytest.mark.mvp
def test_cilindro_agujero_ciego_profundidad_mayor_que_alto_es_rechazado():
    """T-24 | 001/FR-002 — Cilindro agujero ciego con profundidad > alto → rechazado.

    Prueba: src/recipes/cilindro.py::construir
    """
    from src.schemas.figuras import AgujeroParams, CaraAgujero, TipoAgujero

    params = CilindroParams(
        diametro=50,
        alto=80,
        agujero=AgujeroParams(
            diametro=20,
            cara=CaraAgujero.superior,
            tipo=TipoAgujero.ciego,
            profundidad=81.0,
        ),
    )
    with pytest.raises(ValueError, match="[Pp]rofundidad|[Ee]spesor"):
        construir(params)
