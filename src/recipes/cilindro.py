"""
Receta paramétrica: cilindro.
Recibe CilindroParams validado → devuelve cq.Workplane.
Función pura; sin efectos secundarios.
"""

import cadquery as cq

from src.schemas.figuras import CilindroParams


def construir(params: CilindroParams) -> cq.Workplane:
    """Construye el cilindro a partir de parámetros validados.

    Lanza ValueError si el agujero es geométricamente inválido (capa 2).
    """
    diametro = params.diametro
    alto = params.alto

    if params.agujero is not None:
        agujero = params.agujero
        cara = agujero.cara.value

        if cara not in ("superior", "inferior"):
            raise ValueError(
                f"Cara no válida para cilindro: '{cara}'. Solo se admiten 'superior' e 'inferior'."
            )
        if agujero.diametro >= diametro:
            raise ValueError(
                f"Agujero igual o mayor que el cilindro: diámetro agujero {agujero.diametro} "
                f">= diámetro cilindro {diametro}"
            )

    solido = cq.Workplane("XY").cylinder(alto, diametro / 2)

    if params.agujero is not None:
        agujero = params.agujero
        solido = solido.faces(">Z").workplane().hole(agujero.diametro, alto)

    return solido
