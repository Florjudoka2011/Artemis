"""
Receta paramétrica: prisma rectangular.
Recibe PrismaRectangularParams validado → devuelve cq.Workplane.
Función pura; sin efectos secundarios.
"""

import cadquery as cq

from src.schemas.figuras import PrismaRectangularParams


def construir(params: PrismaRectangularParams) -> cq.Workplane:
    """Construye el prisma rectangular a partir de parámetros validados.

    Agujero: pendiente MVP Phase 4 (US2). Tests T-04..T-09.
    """
    if params.agujero is not None:
        raise NotImplementedError(
            "Agujero en prisma: pendiente MVP Phase 4 (US2), tests T-04..T-09"
        )

    # centered=(True, True, False): centrado en X e Y, zmin=0 (convención T-197)
    return cq.Workplane("XY").box(
        params.largo, params.ancho, params.alto, centered=(True, True, False)
    )
