"""
Receta paramétrica: prisma rectangular.
Recibe PrismaRectangularParams validado → devuelve cq.Workplane.
Función pura; sin efectos secundarios.
"""

import cadquery as cq

from src.schemas.figuras import CaraAgujero, PrismaRectangularParams

# Dimensiones mínimas de la cara para cada cara del prisma
_CARA_DIMENSIONES = {
    CaraAgujero.superior: lambda p: min(p.largo, p.ancho),
    CaraAgujero.inferior: lambda p: min(p.largo, p.ancho),
    CaraAgujero.frontal: lambda p: min(p.ancho, p.alto),
    CaraAgujero.trasera: lambda p: min(p.ancho, p.alto),
    CaraAgujero.lateral_izq: lambda p: min(p.largo, p.alto),
    CaraAgujero.lateral_der: lambda p: min(p.largo, p.alto),
}


def construir(params: PrismaRectangularParams) -> cq.Workplane:
    """Construye el prisma rectangular a partir de parámetros validados.

    Convención: zmin=0, centrado en X e Y (T-197).
    Agujero pasante: valida diámetro < lado menor de la cara (T-05/T-07).
    """
    # centered=(True, True, False): centrado en X e Y, zmin=0 (convención T-197)
    solido = cq.Workplane("XY").box(
        params.largo, params.ancho, params.alto, centered=(True, True, False)
    )

    if params.agujero is not None:
        agujero = params.agujero
        lado_menor = _CARA_DIMENSIONES[agujero.cara](params)
        if agujero.diametro >= lado_menor:
            raise ValueError(
                f"Diámetro del agujero ({agujero.diametro}) debe ser < "
                f"lado menor de la cara '{agujero.cara.value}' ({lado_menor})"
            )

        radio = agujero.diametro / 2
        cara = agujero.cara
        ox, oy = agujero.offset_x, agujero.offset_y

        if cara in (CaraAgujero.superior, CaraAgujero.inferior):
            # Taladro vertical (eje Z): desde la cara superior
            solido = solido.faces(">Z").workplane().center(ox, oy).circle(radio).cutThruAll()
        elif cara in (CaraAgujero.frontal, CaraAgujero.trasera):
            # Taladro en Y
            direction = ">Y" if cara == CaraAgujero.frontal else "<Y"
            solido = solido.faces(direction).workplane().center(ox, oy).circle(radio).cutThruAll()
        else:
            # Taladro en X (lateral_izq / lateral_der)
            direction = "<X" if cara == CaraAgujero.lateral_izq else ">X"
            solido = solido.faces(direction).workplane().center(ox, oy).circle(radio).cutThruAll()

    return solido
