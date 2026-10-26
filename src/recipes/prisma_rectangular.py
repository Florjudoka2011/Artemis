"""
Receta paramétrica: prisma rectangular.
Recibe PrismaRectangularParams validado → devuelve cq.Workplane.
Función pura; sin efectos secundarios.
"""

import cadquery as cq

from src.schemas.figuras import CaraAgujero, PrismaRectangularParams, TipoAgujero

# Dimensiones de la cara: (half_u, half_v, espesor) para cada cara
# u y v son los ejes del plano de la cara; espesor es la profundidad máxima de agujero ciego.
# Para cara superior/inferior: u → X (largo/2), v → Y (ancho/2), espesor = alto
# Para cara frontal/trasera:   u → X (largo/2), v → Z (alto/2),  espesor = ancho
# Para cara lateral_izq/der:   u → Y (ancho/2), v → Z (alto/2),  espesor = largo
_CARA_DIMENSIONES = {
    CaraAgujero.superior: lambda p: (p.largo / 2, p.ancho / 2, p.alto),
    CaraAgujero.inferior: lambda p: (p.largo / 2, p.ancho / 2, p.alto),
    CaraAgujero.frontal: lambda p: (p.largo / 2, p.alto / 2, p.ancho),
    CaraAgujero.trasera: lambda p: (p.largo / 2, p.alto / 2, p.ancho),
    CaraAgujero.lateral_izq: lambda p: (p.ancho / 2, p.alto / 2, p.largo),
    CaraAgujero.lateral_der: lambda p: (p.ancho / 2, p.alto / 2, p.largo),
}

_CARA_SELECTOR = {
    CaraAgujero.superior: ">Z",
    CaraAgujero.inferior: "<Z",
    CaraAgujero.frontal: ">Y",
    CaraAgujero.trasera: "<Y",
    CaraAgujero.lateral_izq: "<X",
    CaraAgujero.lateral_der: ">X",
}


def construir(params: PrismaRectangularParams) -> cq.Workplane:
    """Construye el prisma rectangular a partir de parámetros validados.

    Convención: zmin=0, centrado en X e Y (T-197).
    Agujero pasante/ciego con posición u, v y validación de límites (T-09/T-18/T-19).
    """
    solido = cq.Workplane("XY").box(
        params.largo, params.ancho, params.alto, centered=(True, True, False)
    )

    if params.agujero is None:
        return solido

    ag = params.agujero
    half_u, half_v, espesor = _CARA_DIMENSIONES[ag.cara](params)
    radio = ag.diametro / 2

    # Validación diámetro vs cara (legado T-05/T-07): diámetro < min(2*half_u, 2*half_v)
    lado_menor = min(half_u, half_v) * 2
    if ag.diametro >= lado_menor:
        raise ValueError(
            f"Diámetro del agujero ({ag.diametro}) debe ser < "
            f"lado menor de la cara '{ag.cara.value}' ({lado_menor})"
        )

    # Validación posición: el agujero debe quedar completamente dentro de la cara (T-09)
    exceso_u = abs(ag.u) + radio - half_u
    exceso_v = abs(ag.v) + radio - half_v
    if exceso_u >= 0 or exceso_v >= 0:
        exceso = max(exceso_u, exceso_v)
        eje = "u" if exceso_u >= exceso_v else "v"
        raise ValueError(
            f"Agujero fuera de la cara '{ag.cara.value}': excede {exceso:.3f} mm en eje {eje}"
        )

    # Validación profundidad (agujero ciego, T-21)
    if ag.tipo == TipoAgujero.ciego and ag.profundidad >= espesor:
        raise ValueError(
            f"Profundidad del agujero ciego ({ag.profundidad}) debe ser < "
            f"espesor de la pieza en esa dirección ({espesor})"
        )

    selector = _CARA_SELECTOR[ag.cara]
    wp = solido.faces(selector).workplane().center(ag.u, ag.v).circle(radio)

    if ag.tipo == TipoAgujero.pasante:
        solido = wp.cutThruAll()
    else:
        solido = wp.cutBlind(-ag.profundidad)

    return solido
