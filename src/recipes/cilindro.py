"""
Receta paramétrica: cilindro.
Recibe CilindroParams validado → devuelve cq.Workplane.
Función pura; sin efectos secundarios.
"""

import cadquery as cq

from src.schemas.figuras import CilindroParams


def construir(params: CilindroParams) -> cq.Workplane:
    """Construye el cilindro a partir de parámetros validados.

    Agujero: T-11/T-12 son US2 (Phase 4); T-13/T-14 son Fase 1A completa.
    """
    if params.agujero is not None:
        raise NotImplementedError("Agujero en cilindro: T-11/T-12=US2 Phase4; T-13/T-14=Fase1A")

    return cq.Workplane("XY").cylinder(params.alto, params.diametro / 2)
