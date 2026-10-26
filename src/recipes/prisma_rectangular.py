"""
Receta paramétrica: prisma rectangular.
Recibe PrismaRectangularParams validado → devuelve cq.Workplane.
Función pura; sin efectos secundarios.
"""

import cadquery as cq

from src.schemas.figuras import CaraAgujero, PrismaRectangularParams, TipoAgujero

# Selector CadQuery para cada cara del prisma.
_CARA_SELECTOR = {
    CaraAgujero.superior: ">Z",
    CaraAgujero.inferior: "<Z",
    CaraAgujero.frontal: "<Y",
    CaraAgujero.trasera: ">Y",
    CaraAgujero.lateral_izq: "<X",
    CaraAgujero.lateral_der: ">X",
}


# Profundidad de perforación (para agujeros pasantes) en cada cara:
# basta con la dimensión completa del prisma en esa dirección.
def _profundidad_pasante(cara: CaraAgujero, params: PrismaRectangularParams) -> float:
    if cara in (CaraAgujero.superior, CaraAgujero.inferior):
        return params.alto
    if cara in (CaraAgujero.frontal, CaraAgujero.trasera):
        return params.ancho
    return params.largo  # lateral_izq / lateral_der


def construir(params: PrismaRectangularParams) -> cq.Workplane:
    """Construye el prisma rectangular con sus operaciones aplicadas.

    Convención de posicionamiento: zmin=0 (pieza sobre el plano XY), centrado en X e Y.
    Las operaciones se aplican en orden de la lista.
    """
    # centered=(True, True, False): centrado en X e Y, zmin=0 (convención T-197)
    solido = cq.Workplane("XY").box(
        params.largo, params.ancho, params.alto, centered=(True, True, False)
    )

    for op in params.operaciones:
        if op.tipo == "agujero":
            selector = _CARA_SELECTOR[op.cara]

            # Dimensiones de la cara para centrar las coordenadas (u,v)
            if op.cara in (CaraAgujero.superior, CaraAgujero.inferior):
                W, H = params.largo, params.ancho
            elif op.cara in (CaraAgujero.frontal, CaraAgujero.trasera):
                W, H = params.largo, params.alto
            else:
                W, H = params.ancho, params.alto

            # Coordenadas en el sistema de referencia del workplane de la cara.
            # El workplane tiene origen en el centro geométrico de la cara.
            # u=0 es el borde izquierdo (→ workplane x = -W/2)
            # v=0 es la base (→ workplane y = -H/2)
            wp_x = op.u - W / 2
            wp_y = op.v - H / 2

            profundidad = (
                _profundidad_pasante(op.cara, params)
                if op.subtipo == TipoAgujero.pasante
                else op.profundidad
            )

            solido = (
                solido.faces(selector)
                .workplane()
                .pushPoints([(wp_x, wp_y)])
                .hole(op.diametro, profundidad)
            )

    return solido
