"""
Receta paramétrica: cilindro.
Recibe CilindroParams validado → devuelve cq.Workplane.
Función pura; sin efectos secundarios.
"""

import cadquery as cq

from src.schemas.figuras import CilindroParams


def construir(params: CilindroParams) -> cq.Workplane:
    """Construye el cilindro a partir de parámetros validados.

    Convención: zmin=0 (T-198). Agujero coaxial pasante (T-11..T-14).
    """
    if params.agujero is not None and params.agujero.diametro >= params.diametro:
        raise ValueError(
            f"Diámetro del agujero ({params.agujero.diametro}) debe ser < "
            f"diámetro del cilindro ({params.diametro})"
        )

    # cylinder() centra en Z por defecto; translate sube la pieza zmin=0 (convención T-198)
    solido = (
        cq.Workplane("XY")
        .cylinder(params.alto, params.diametro / 2)
        .translate((0, 0, params.alto / 2))
    )

    if params.agujero is not None:
        radio = params.agujero.diametro / 2
        # Agujero coaxial: taladro vertical desde cara superior
        solido = solido.faces(">Z").workplane().circle(radio).cutThruAll()

    return solido
