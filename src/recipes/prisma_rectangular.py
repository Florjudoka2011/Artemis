"""
Receta paramétrica: prisma rectangular.
Recibe PrismaRectangularParams validado → devuelve cq.Workplane.
Función pura; sin efectos secundarios.
"""

import cadquery as cq

from src.schemas.figuras import PrismaRectangularParams


def construir(params: PrismaRectangularParams) -> cq.Workplane:
    """Construye el prisma rectangular a partir de parámetros validados.

    Agujero: T-04/T-05 son US2 (Phase 4); T-06..T-09 son Fase 1A completa.
    """
    if params.agujero is not None:
        raise NotImplementedError("Agujero en prisma: T-04/T-05=US2 Phase4; T-06..T-09=Fase1A")

    return cq.Workplane("XY").box(params.largo, params.ancho, params.alto)
