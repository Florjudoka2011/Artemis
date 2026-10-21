"""
Receta paramétrica: prisma rectangular.
Recibe PrismaRectangularParams validado → devuelve cq.Workplane.
Función pura; sin efectos secundarios.
"""

import cadquery as cq

from src.schemas.figuras import PrismaRectangularParams


def construir(params: PrismaRectangularParams) -> cq.Workplane:
    """Construye el prisma rectangular a partir de parámetros validados.

    Lanza ValueError si el agujero es geométricamente inválido (capa 2).
    """
    largo = params.largo
    ancho = params.ancho
    alto = params.alto

    if params.agujero is not None:
        agujero = params.agujero
        cara = agujero.cara.value
        # Determinar las dimensiones de la cara seleccionada
        if cara in ("superior", "inferior"):
            dim_x, dim_y = largo, ancho
        elif cara in ("frontal", "trasera"):
            dim_x, dim_y = largo, alto
        else:  # lateral_izq, lateral_der
            dim_x, dim_y = ancho, alto

        lado_menor = min(dim_x, dim_y)
        radio = agujero.diametro / 2

        if agujero.diametro >= lado_menor:
            raise ValueError(
                f"Agujero demasiado grande para la cara: diámetro {agujero.diametro} "
                f">= lado menor {lado_menor}"
            )

        # Verificar que el círculo cabe en la cara con los offsets
        ox, oy = agujero.offset_x, agujero.offset_y
        if (abs(ox) + radio > dim_x / 2) or (abs(oy) + radio > dim_y / 2):
            raise ValueError(
                f"Agujero sale fuera de la cara: offset ({ox}, {oy}) con radio {radio}"
            )

    solido = cq.Workplane("XY").box(largo, ancho, alto)

    if params.agujero is not None:
        agujero = params.agujero
        cara = agujero.cara.value
        radio = agujero.diametro / 2
        ox, oy = agujero.offset_x, agujero.offset_y

        if cara == "superior":
            solido = solido.faces(">Z").workplane().center(ox, oy).hole(agujero.diametro, alto)
        elif cara == "inferior":
            solido = solido.faces("<Z").workplane().center(ox, oy).hole(agujero.diametro, alto)
        elif cara == "frontal":
            solido = solido.faces(">Y").workplane().center(ox, oy).hole(agujero.diametro, ancho)
        elif cara == "trasera":
            solido = solido.faces("<Y").workplane().center(ox, oy).hole(agujero.diametro, ancho)
        elif cara == "lateral_der":
            solido = solido.faces(">X").workplane().center(ox, oy).hole(agujero.diametro, largo)
        else:  # lateral_izq
            solido = solido.faces("<X").workplane().center(ox, oy).hole(agujero.diametro, largo)

    return solido
