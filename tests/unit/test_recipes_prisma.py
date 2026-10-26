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


# ---------------------------------------------------------------------------
# T-09..T-22: posición y tipo de agujero (US2 ampliación)
# ---------------------------------------------------------------------------


@pytest.mark.mvp
def test_prisma_agujero_posicion_fuera_de_cara_es_rechazado():
    """T-09 | 001/FR-002 — Agujero desplazado que sale de la cara → rechazado con cuánto excede.

    Prueba: src/recipes/prisma_rectangular.py::construir

    Prisma 100×60×40, cara superior (half_u=50, half_v=30), Ø20 (r=10), u=41.
    |41| + 10 = 51 > 50 → excede 1 mm en eje u.
    """
    from src.schemas.figuras import AgujeroParams, CaraAgujero, TipoAgujero

    params = PrismaRectangularParams(
        largo=100,
        ancho=60,
        alto=40,
        agujero=AgujeroParams(
            diametro=20,
            cara=CaraAgujero.superior,
            tipo=TipoAgujero.pasante,
            u=41.0,
            v=0.0,
        ),
    )
    with pytest.raises(ValueError, match="[Ff]uera|[Ee]xcede|[Ll][íi]mite"):
        construir(params)


@pytest.mark.mvp
def test_prisma_agujero_volumen_no_depende_de_posicion():
    """T-15 | 001/FR-002 — Agujero Ø20 desplazado u=20 tiene el mismo volumen que centrado.

    Prueba: src/recipes/prisma_rectangular.py::construir

    Valor esperado: 240000 − π × 10² × 40 = 227433.629 mm³
    """
    from src.schemas.figuras import AgujeroParams, CaraAgujero, TipoAgujero

    params = PrismaRectangularParams(
        largo=100,
        ancho=60,
        alto=40,
        agujero=AgujeroParams(
            diametro=20,
            cara=CaraAgujero.superior,
            tipo=TipoAgujero.pasante,
            u=20.0,
            v=0.0,
        ),
    )
    solido = construir(params)
    volumen = solido.val().Volume()
    esperado = 240000 - math.pi * 10**2 * 40
    assert math.isclose(
        volumen, esperado, rel_tol=1e-6
    ), f"Volumen esperado {esperado:.3f} mm³, obtenido {volumen}"


@pytest.mark.mvp
def test_prisma_agujero_centro_no_esta_dentro_del_solido():
    """T-16 | 001/FR-002 — El punto en el eje del agujero NO está dentro del sólido.

    Prueba: src/recipes/prisma_rectangular.py::construir

    Agujero coaxial centrado (u=0, v=0): el eje es (0, 0, z).
    El punto (0, 0, 20) queda dentro del vaciado → isInside = False.
    """
    import cadquery as cq

    from src.schemas.figuras import AgujeroParams, CaraAgujero, TipoAgujero

    params = PrismaRectangularParams(
        largo=100,
        ancho=60,
        alto=40,
        agujero=AgujeroParams(
            diametro=20,
            cara=CaraAgujero.superior,
            tipo=TipoAgujero.pasante,
            u=0.0,
            v=0.0,
        ),
    )
    solido = construir(params)
    punto_eje = cq.Vector(0, 0, 20)
    assert not solido.val().isInside(
        punto_eje
    ), "El eje del agujero NO debe estar dentro del sólido"


@pytest.mark.mvp
def test_prisma_punto_junto_al_agujero_esta_dentro_del_solido():
    """T-17 | 001/FR-002 — Un punto a 1 mm del borde del agujero SÍ está dentro del sólido.

    Prueba: src/recipes/prisma_rectangular.py::construir

    Agujero Ø20 centrado (r=10). Punto en (11, 0, 20): r=11 > 10 → dentro del material.
    """
    import cadquery as cq

    from src.schemas.figuras import AgujeroParams, CaraAgujero, TipoAgujero

    params = PrismaRectangularParams(
        largo=100,
        ancho=60,
        alto=40,
        agujero=AgujeroParams(
            diametro=20,
            cara=CaraAgujero.superior,
            tipo=TipoAgujero.pasante,
            u=0.0,
            v=0.0,
        ),
    )
    solido = construir(params)
    punto_material = cq.Vector(11, 0, 20)
    assert solido.val().isInside(
        punto_material
    ), "Un punto a 1 mm del borde del agujero SÍ debe estar dentro del sólido"


@pytest.mark.mvp
def test_prisma_agujero_cerca_de_esquina_dentro_del_limite_es_aceptado():
    """T-18 | 001/FR-002 — Agujero cerca de una esquina dentro del límite → aceptado.

    Prueba: src/recipes/prisma_rectangular.py::construir

    Prisma 100×60×40, superior (half_u=50, half_v=30), Ø20 (r=10), u=35, v=19.
    |35|+10=45 < 50 ✓  |19|+10=29 < 30 ✓ → debe pasar.
    """
    from src.schemas.figuras import AgujeroParams, CaraAgujero, TipoAgujero

    params = PrismaRectangularParams(
        largo=100,
        ancho=60,
        alto=40,
        agujero=AgujeroParams(
            diametro=20,
            cara=CaraAgujero.superior,
            tipo=TipoAgujero.pasante,
            u=35.0,
            v=19.0,
        ),
    )
    solido = construir(params)
    assert solido is not None


@pytest.mark.mvp
def test_prisma_agujero_un_milimetro_fuera_del_limite_es_rechazado():
    """T-19 | 001/FR-002 — Agujero 1 mm más allá del límite → rechazado.

    Prueba: src/recipes/prisma_rectangular.py::construir

    Prisma 100×60×40, superior, Ø20 (r=10), u=35, v=20.
    |20|+10=30, condición |v|+r < 30 → NO cumple (30 no es < 30) → rechazado.
    """
    from src.schemas.figuras import AgujeroParams, CaraAgujero, TipoAgujero

    params = PrismaRectangularParams(
        largo=100,
        ancho=60,
        alto=40,
        agujero=AgujeroParams(
            diametro=20,
            cara=CaraAgujero.superior,
            tipo=TipoAgujero.pasante,
            u=35.0,
            v=20.0,
        ),
    )
    with pytest.raises(ValueError, match="[Ff]uera|[Ee]xcede|[Ll][íi]mite"):
        construir(params)


@pytest.mark.mvp
def test_prisma_agujero_ciego_volumen():
    """T-20 | 001/FR-002 — Agujero ciego Ø20, profundidad=15 → volumen correcto.

    Prueba: src/recipes/prisma_rectangular.py::construir

    Valor esperado: 240000 − π × 10² × 15 = 235287.611 mm³
    """
    from src.schemas.figuras import AgujeroParams, CaraAgujero, TipoAgujero

    params = PrismaRectangularParams(
        largo=100,
        ancho=60,
        alto=40,
        agujero=AgujeroParams(
            diametro=20,
            cara=CaraAgujero.superior,
            tipo=TipoAgujero.ciego,
            profundidad=15.0,
            u=0.0,
            v=0.0,
        ),
    )
    solido = construir(params)
    volumen = solido.val().Volume()
    esperado = 240000 - math.pi * 10**2 * 15
    assert math.isclose(
        volumen, esperado, rel_tol=1e-6
    ), f"Volumen esperado {esperado:.3f} mm³, obtenido {volumen}"


@pytest.mark.mvp
def test_prisma_agujero_ciego_profundidad_mayor_que_espesor_es_rechazado():
    """T-21 | 001/FR-002 — Agujero ciego con profundidad > alto → rechazado.

    Prueba: src/recipes/prisma_rectangular.py::construir
    """
    from src.schemas.figuras import AgujeroParams, CaraAgujero, TipoAgujero

    params = PrismaRectangularParams(
        largo=100,
        ancho=60,
        alto=40,
        agujero=AgujeroParams(
            diametro=20,
            cara=CaraAgujero.superior,
            tipo=TipoAgujero.ciego,
            profundidad=41.0,
            u=0.0,
            v=0.0,
        ),
    )
    with pytest.raises(ValueError, match="[Pp]rofundidad|[Ee]spesor"):
        construir(params)


@pytest.mark.mvp
def test_prisma_agujero_ciego_profundidad_cero_es_rechazado():
    """T-22 | 001/FR-002 — Agujero ciego con profundidad=0 → rechazado por schema.

    Prueba: src/schemas/figuras.py::AgujeroParams
    """
    from pydantic import ValidationError

    from src.schemas.figuras import AgujeroParams, CaraAgujero, TipoAgujero

    with pytest.raises(ValidationError):
        AgujeroParams(
            diametro=20,
            cara=CaraAgujero.superior,
            tipo=TipoAgujero.ciego,
            profundidad=0.0,
        )
