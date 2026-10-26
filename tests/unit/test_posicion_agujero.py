"""
Tests de posicion real del agujero en 3D — usa isInside() para verificar
que el centro del agujero queda exactamente donde corresponde.

Convencion (distancia desde borde, dibujo tecnico):
  u = distancia desde el borde izquierdo de la cara (vista desde afuera)
  v = distancia desde la base (Z=0 para caras verticales; borde -Y para horizontales)

Coordenadas globales resultantes:
  frontal:     global_x = u - largo/2,   global_z = v
  trasera:     global_x = largo/2 - u,   global_z = v
  lateral_izq: global_y = u - ancho/2,   global_z = v
  lateral_der: global_y = ancho/2 - u,   global_z = v
  superior:    global_x = u - largo/2,   global_y = v - ancho/2
  inferior:    global_x = u - largo/2,   global_y = ancho/2 - v

T-209..T-214
"""

import cadquery as cq
import pytest

from src.recipes.prisma_rectangular import construir
from src.schemas.figuras import AgujeroParams, CaraAgujero, PrismaRectangularParams

LARGO, ANCHO, ALTO = 200, 67, 200
DIAM = 10
RADIO = DIAM / 2


def _params(cara, u, v, largo=LARGO, ancho=ANCHO, alto=ALTO, diam=DIAM):
    return PrismaRectangularParams(
        largo=largo,
        ancho=ancho,
        alto=alto,
        agujero=AgujeroParams(diametro=diam, cara=cara, u=u, v=v),
    )


# ── T-209: cara frontal — v=190 coloca agujero en z=190 ─────────────────────


@pytest.mark.mvp
def test_frontal_v_coloca_agujero_en_z_correcto():
    """T-209 | 001/FR-010 — Cara frontal: v=190 (desde base) coloca agujero en z=190.

    Prueba: src/recipes/prisma_rectangular.py::construir
    """
    # u=100 (centro horizontal: x=100-100=0), v=190 (cerca del tope: z=190)
    p = _params(CaraAgujero.frontal, u=100, v=190)
    solido = construir(p)

    # Punto en el eje del agujero (y=0 = dentro de la pieza, z=190)
    punto_en_agujero = cq.Vector(0, 0, 190)
    assert not solido.val().isInside(punto_en_agujero), (
        "El agujero debe estar en z=190 (v=190 desde base), "
        "pero el punto (0,0,190) esta dentro del solido"
    )

    # Punto fuera del agujero pero en el mismo z (a 7mm del eje, radio=5)
    punto_en_solido = cq.Vector(7, 0, 190)
    assert solido.val().isInside(
        punto_en_solido
    ), "El punto (7,0,190) debe estar en el solido (fuera del agujero de radio 5)"


# ── T-210: cara frontal — u positivo desplaza hacia +X ──────────────────────


@pytest.mark.mvp
def test_frontal_u_mayor_desplaza_hacia_x_positivo():
    """T-210 | 001/FR-010 — Cara frontal: u=140 (40mm pasado el centro) → agujero en x=+40.

    Prueba: src/recipes/prisma_rectangular.py::construir
    """
    # u=140: global_x = 140 - 100 = +40. v=100: global_z = 100 (centro de altura)
    p = _params(CaraAgujero.frontal, u=140, v=100)
    solido = construir(p)

    # Agujero debe estar en x=+40, z=100
    punto_agujero = cq.Vector(40, 0, 100)
    assert not solido.val().isInside(
        punto_agujero
    ), "El agujero debe estar en x=+40 (u=140, borde izq en x=-100)"

    # En x=-40 no debe haber agujero
    punto_sin_agujero = cq.Vector(-40, 0, 100)
    assert solido.val().isInside(
        punto_sin_agujero
    ), "No debe haber agujero en x=-40: u mas grande desplaza hacia +X"


# ── T-211: cara trasera — v=190 coloca agujero en z=190 ────────────────────


@pytest.mark.mvp
def test_trasera_v_coloca_agujero_en_z_correcto():
    """T-211 | 001/FR-010 — Cara trasera: v=190 (desde base) coloca agujero en z=190.

    Prueba: src/recipes/prisma_rectangular.py::construir
    """
    # u=100 (centro: global_x=largo/2-100=0), v=190 → global_z=190
    p = _params(CaraAgujero.trasera, u=100, v=190)
    solido = construir(p)

    punto_en_agujero = cq.Vector(0, 0, 190)
    assert not solido.val().isInside(
        punto_en_agujero
    ), "El agujero debe estar en z=190 en cara trasera con v=190"

    punto_en_solido = cq.Vector(7, 0, 190)
    assert solido.val().isInside(punto_en_solido)


# ── T-212: cara lateral_izq — v=190 coloca agujero en z=190 ────────────────


@pytest.mark.mvp
def test_lateral_izq_v_coloca_agujero_en_z_correcto():
    """T-212 | 001/FR-010 — Cara lateral_izq: v=190 coloca agujero en z=190.

    Prueba: src/recipes/prisma_rectangular.py::construir
    """
    # u = ancho/2 = 33.5 (centro: global_y=33.5-33.5=0), v=190 → global_z=190
    u_centro = ANCHO / 2
    p = _params(CaraAgujero.lateral_izq, u=u_centro, v=190)
    solido = construir(p)

    # Hole axis is X, hole at y=0, z=190. Point (0, 0, 190) is on axis inside piece.
    punto_en_agujero = cq.Vector(0, 0, 190)
    assert not solido.val().isInside(
        punto_en_agujero
    ), "El agujero debe estar en z=190 en cara lateral_izq con v=190"

    punto_en_solido = cq.Vector(0, 7, 190)
    assert solido.val().isInside(punto_en_solido)


# ── T-213: cara lateral_der — v=190 coloca agujero en z=190 ────────────────


@pytest.mark.mvp
def test_lateral_der_v_coloca_agujero_en_z_correcto():
    """T-213 | 001/FR-010 — Cara lateral_der: v=190 coloca agujero en z=190.

    Prueba: src/recipes/prisma_rectangular.py::construir
    """
    # u=ancho/2=33.5 → global_y=ancho/2-33.5=0, v=190 → global_z=190
    u_centro = ANCHO / 2
    p = _params(CaraAgujero.lateral_der, u=u_centro, v=190)
    solido = construir(p)

    punto_en_agujero = cq.Vector(0, 0, 190)
    assert not solido.val().isInside(
        punto_en_agujero
    ), "El agujero debe estar en z=190 en cara lateral_der con v=190"

    punto_en_solido = cq.Vector(0, 7, 190)
    assert solido.val().isInside(punto_en_solido)


# ── T-214: cara superior — u/v colocan agujero correctamente ─────────────────


@pytest.mark.mvp
def test_superior_u_v_colocan_agujero_correctamente():
    """T-214 | 001/FR-010 — Cara superior: u=140 v=43.5 → agujero en x=+40, y=+10.

    Prueba: src/recipes/prisma_rectangular.py::construir
    """
    # u=140: global_x=140-100=+40. v=43.5: global_y=43.5-33.5=+10
    p = _params(CaraAgujero.superior, u=140, v=43.5)
    solido = construir(p)

    # Agujero a lo largo de Z, axis en (x=40, y=10)
    punto_en_agujero = cq.Vector(40, 10, 100)
    assert not solido.val().isInside(punto_en_agujero), "Agujero superior debe estar en x=40, y=10"

    punto_en_solido = cq.Vector(47, 10, 100)
    assert solido.val().isInside(punto_en_solido)
