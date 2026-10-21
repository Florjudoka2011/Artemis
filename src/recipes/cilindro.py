"""
Receta paramétrica: cilindro.
Recibe CilindroParams validado → devuelve cq.Workplane.
Función pura; sin efectos secundarios.
"""

import cadquery as cq

from src.schemas.figuras import CilindroParams


def construir(params: CilindroParams) -> cq.Workplane:
    """Construye el cilindro a partir de parámetros validados.

    Agujero: pendiente (tests T-11..T-14, Fase 1A).
    """
    if params.agujero is not None:
        raise NotImplementedError("Agujero en cilindro: pendiente (Fase 1A, tests T-11..T-14)")

    return cq.Workplane("XY").cylinder(params.alto, params.diametro / 2)
