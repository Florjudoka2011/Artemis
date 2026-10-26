"""
Receta paramétrica: cilindro.
Recibe CilindroParams validado → devuelve cq.Workplane.
Función pura; sin efectos secundarios.
"""

import cadquery as cq

from src.schemas.figuras import CilindroParams


def construir(params: CilindroParams) -> cq.Workplane:
    """Construye el cilindro a partir de parámetros validados.

    Agujero: pendiente MVP Phase 4 (US2). Tests T-11..T-14.
    """
    if params.agujero is not None:
        raise NotImplementedError(
            "Agujero en cilindro: pendiente MVP Phase 4 (US2), tests T-11..T-14"
        )

    # cylinder() centra en Z por defecto; translate sube la pieza zmin=0 (convención T-198)
    return (
        cq.Workplane("XY")
        .cylinder(params.alto, params.diametro / 2)
        .translate((0, 0, params.alto / 2))
    )
