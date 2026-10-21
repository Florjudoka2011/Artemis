"""
Receta paramétrica: prisma rectangular.
Recibe PrismaRectangularParams validado → devuelve cq.Workplane.
Función pura; sin efectos secundarios.
"""

import cadquery as cq

from src.schemas.figuras import PrismaRectangularParams


def construir(params: PrismaRectangularParams) -> cq.Workplane:
    """Construye el prisma rectangular a partir de parámetros validados.

    Agujero: pendiente (tests T-04..T-09, Fase 1A).
    """
    if params.agujero is not None:
        raise NotImplementedError("Agujero en prisma: pendiente (Fase 1A, tests T-04..T-09)")

    return cq.Workplane("XY").box(params.largo, params.ancho, params.alto)
