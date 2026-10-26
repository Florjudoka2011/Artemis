"""
Tests de posición real del agujero en 3D — usa isInside() para verificar
que el centro del agujero queda exactamente donde corresponde.

Convención actual (centro de cara): u y v son desplazamientos desde el
centro geométrico de la cara. Se asume que v>0 en caras verticales mueve
el agujero hacia arriba (+Z).

T-209..T-215
"""

import cadquery as cq
import pytest

from src.recipes.prisma_rectangular import construir
from src.schemas.figuras import AgujeroParams, CaraAgujero, PrismaRectangularParams


def _params(cara, u, v, largo=200, ancho=67, alto=200, diam=10):
    return PrismaRectangularParams(
        largo=largo,
        ancho=ancho,
        alto=alto,
        agujero=AgujeroParams(diametro=diam, cara=cara, u=u, v=v),
    )


# ── T-209: cara frontal — v positivo debe mover el agujero hacia +Z ─────────


@pytest.mark.mvp
def test_frontal_v_positivo_mueve_hacia_z_positivo():
    """T-209 | 001/FR-010 — En cara frontal, v=90 coloca agujero en z=alto/2+90=190, no en z=90.

    Prueba: src/recipes/prisma_rectangular.py::construir
    """
    # largo=200 ancho=67 alto=200, cara frontal, Ø10, u=0 (centro), v=90
    # Cara frontal: Y=+33.5, cara se extiende en X y Z.
    # Centro geométrico de la cara = (0, 33.5, 100).
    # Con v=90 (desde el centro), el agujero debe quedar en z=190.
    p = _params(CaraAgujero.frontal, u=0, v=90)
    solido = construir(p)

    # Punto en el eje del agujero en z=190 (dentro de la pieza, y=0)
    # debe estar EN el agujero → NOT isInside
    punto_en_agujero = cq.Vector(0, 0, 190)
    assert not solido.val().isInside(punto_en_agujero), (
        "El agujero debe estar en z=190 (centro de cara + v=90), "
        "pero el punto (0,0,190) está dentro del sólido — agujero mal ubicado"
    )

    # Punto adyacente al agujero (a 7mm del eje, radio=5) en z=190 debe estar en el sólido
    punto_en_solido = cq.Vector(7, 0, 190)
    assert solido.val().isInside(
        punto_en_solido
    ), "El punto (7,0,190) debe estar en el sólido (fuera del agujero de radio 5)"


# ── T-210: cara frontal — u positivo debe desplazar hacia +X ────────────────


@pytest.mark.mvp
def test_frontal_u_positivo_desplaza_hacia_x_positivo():
    """T-210 | 001/FR-010 — En cara frontal, u=40 coloca agujero en x=+40 (no x=-40).

    Prueba: src/recipes/prisma_rectangular.py::construir
    """
    # u=40 desde el centro → agujero en x=+40, z=alto/2=100
    p = _params(CaraAgujero.frontal, u=40, v=0)
    solido = construir(p)

    # El agujero debe estar en x=+40, y dentro del sólido (y=0), z=100
    punto_agujero_correcto = cq.Vector(40, 0, 100)
    assert not solido.val().isInside(
        punto_agujero_correcto
    ), "El agujero debe estar en x=+40 (u=+40), pero (40,0,100) está en el sólido"

    # En x=-40 no debe haber agujero
    punto_sin_agujero = cq.Vector(-40, 0, 100)
    assert solido.val().isInside(
        punto_sin_agujero
    ), "No debe haber agujero en x=-40: u=+40 desplaza hacia +X, no hacia -X"


# ── T-211: cara trasera — v positivo mueve hacia +Z ────────────────────────


@pytest.mark.mvp
def test_trasera_v_positivo_mueve_hacia_z_positivo():
    """T-211 | 001/FR-010 — En cara trasera, v=90 coloca agujero en z=alto/2+90=190.

    Prueba: src/recipes/prisma_rectangular.py::construir
    """
    p = _params(CaraAgujero.trasera, u=0, v=90)
    solido = construir(p)

    punto_en_agujero = cq.Vector(0, 0, 190)
    assert not solido.val().isInside(
        punto_en_agujero
    ), "El agujero debe estar en z=190 en cara trasera con v=90"

    punto_en_solido = cq.Vector(7, 0, 190)
    assert solido.val().isInside(punto_en_solido)


# ── T-212: cara lateral_izq — v positivo mueve hacia +Z ────────────────────


@pytest.mark.mvp
def test_lateral_izq_v_positivo_mueve_hacia_z_positivo():
    """T-212 | 001/FR-010 — En cara lateral_izq, v=90 coloca agujero en z=190.

    Prueba: src/recipes/prisma_rectangular.py::construir
    """
    p = _params(CaraAgujero.lateral_izq, u=0, v=90)
    solido = construir(p)

    punto_en_agujero = cq.Vector(0, 0, 190)
    assert not solido.val().isInside(
        punto_en_agujero
    ), "El agujero debe estar en z=190 en cara lateral_izq con v=90"

    punto_en_solido = cq.Vector(0, 7, 190)
    assert solido.val().isInside(punto_en_solido)


# ── T-213: cara lateral_der — v positivo mueve hacia +Z ────────────────────


@pytest.mark.mvp
def test_lateral_der_v_positivo_mueve_hacia_z_positivo():
    """T-213 | 001/FR-010 — En cara lateral_der, v=90 coloca agujero en z=190.

    Prueba: src/recipes/prisma_rectangular.py::construir
    """
    p = _params(CaraAgujero.lateral_der, u=0, v=90)
    solido = construir(p)

    punto_en_agujero = cq.Vector(0, 0, 190)
    assert not solido.val().isInside(
        punto_en_agujero
    ), "El agujero debe estar en z=190 en cara lateral_der con v=90"

    punto_en_solido = cq.Vector(0, 7, 190)
    assert solido.val().isInside(punto_en_solido)


# ── T-214: cara superior — u/v centrados funcionan correctamente ─────────────


@pytest.mark.mvp
def test_superior_u_v_colocan_agujero_correctamente():
    """T-214 | 001/FR-010 — En cara superior, u=40 v=20 coloca agujero en (40,20,alto).

    Prueba: src/recipes/prisma_rectangular.py::construir
    """
    p = _params(CaraAgujero.superior, u=40, v=20)
    solido = construir(p)

    # Agujero en (40, 20, z) a lo largo del eje Z (baja desde la cara superior)
    punto_en_agujero = cq.Vector(40, 20, 100)  # mitad de la altura, en el eje del agujero
    assert not solido.val().isInside(punto_en_agujero), "Agujero superior debe estar en x=40, y=20"

    punto_en_solido = cq.Vector(47, 20, 100)  # radio=5, a 7mm del eje
    assert solido.val().isInside(punto_en_solido)
