"""
Receta paramétrica: prisma rectangular.
Recibe PrismaRectangularParams validado → devuelve cq.Workplane.
Función pura; sin efectos secundarios.
"""

import cadquery as cq

from src.schemas.figuras import CaraAgujero, PrismaRectangularParams, TipoAgujero

# Dimensiones de la cara: (face_width, face_height, espesor) para cada cara.
# u y v son distancias desde el borde izquierdo y base (vista desde afuera, dibujo técnico).
# face_width y face_height son las dimensiones TOTALES de la cara (no mitades).
#   superior/inferior: width=largo, height=ancho, espesor=alto
#   frontal/trasera:   width=largo, height=alto,  espesor=ancho
#   lateral_izq/der:   width=ancho, height=alto,  espesor=largo
_CARA_DIMENSIONES = {
    CaraAgujero.superior: lambda p: (p.largo, p.ancho, p.alto),
    CaraAgujero.inferior: lambda p: (p.largo, p.ancho, p.alto),
    CaraAgujero.frontal: lambda p: (p.largo, p.alto, p.ancho),
    CaraAgujero.trasera: lambda p: (p.largo, p.alto, p.ancho),
    CaraAgujero.lateral_izq: lambda p: (p.ancho, p.alto, p.largo),
    CaraAgujero.lateral_der: lambda p: (p.ancho, p.alto, p.largo),
}

_CARA_SELECTOR = {
    CaraAgujero.superior: ">Z",
    CaraAgujero.inferior: "<Z",
    CaraAgujero.frontal: ">Y",
    CaraAgujero.trasera: "<Y",
    CaraAgujero.lateral_izq: "<X",
    CaraAgujero.lateral_der: ">X",
}

# Conversión de coordenadas borde→CadQuery workplane para cada cara.
# u_borde = distancia desde el borde izquierdo (vista desde afuera).
# v_borde = distancia desde la base (Z=0 para caras verticales; borde -Y para horiz.).
# Derivado del diagnóstico de origins/xDir/yDir en caja centered=(T,T,F):
#   superior: origin=(0,0,H), xDir=+X, yDir=+Y → cq_u=u-W/2, cq_v=v-H2/2
#   inferior: origin=(0,0,0), xDir=+X, yDir=-Y → cq_u=u-W/2, cq_v=H2/2-v
#   frontal:  origin=(0,A/2,0), xDir=-X, yDir=+Z → cq_u=W/2-u, cq_v=v
#   trasera:  origin=(0,-A/2,0),xDir=+X, yDir=+Z → cq_u=W/2-u, cq_v=v
#   lat_izq:  origin=(-L/2,0,0),xDir=-Y, yDir=+Z → cq_u=W/2-u, cq_v=v
#   lat_der:  origin=(+L/2,0,0),xDir=+Y, yDir=+Z → cq_u=W/2-u, cq_v=v


def _borde_a_cq(cara: CaraAgujero, u_borde: float, v_borde: float, face_w: float, face_h: float):
    """Convierte posición en coordenadas de borde a coordenadas del workplane CadQuery."""
    half_w = face_w / 2
    half_h = face_h / 2
    if cara == CaraAgujero.superior:
        return u_borde - half_w, v_borde - half_h
    if cara == CaraAgujero.inferior:
        return u_borde - half_w, half_h - v_borde
    # Caras verticales: cq_u = half_w - u_borde; cq_v = v_borde (base en z=0)
    return half_w - u_borde, v_borde


def construir(params: PrismaRectangularParams) -> cq.Workplane:
    """Construye el prisma rectangular a partir de parámetros validados.

    Convención: zmin=0, centrado en X e Y (T-197).
    u/v son distancias desde el borde (dibujo técnico): u desde el borde izquierdo,
    v desde la base (Z=0 en caras verticales, borde -Y en horizontales).
    Agujero pasante/ciego (T-09/T-15..T-24, T-209..T-213).
    """
    solido = cq.Workplane("XY").box(
        params.largo, params.ancho, params.alto, centered=(True, True, False)
    )

    if params.agujero is None:
        return solido

    ag = params.agujero
    face_w, face_h, espesor = _CARA_DIMENSIONES[ag.cara](params)
    radio = ag.diametro / 2

    # Validación diámetro vs cara (T-05/T-07): diámetro < min(face_w, face_h)
    lado_menor = min(face_w, face_h)
    if ag.diametro >= lado_menor:
        raise ValueError(
            f"Diámetro del agujero ({ag.diametro}) debe ser < "
            f"lado menor de la cara '{ag.cara.value}' ({lado_menor})"
        )

    # Validación posición en coordenadas de borde (T-09, T-15..T-24)
    # u_borde ∈ (radio, face_w - radio), v_borde ∈ (radio, face_h - radio)
    # Los extremos exactos se rechazan (el borde del agujero toca la arista de la cara).
    u_min, u_max = radio, face_w - radio
    v_min, v_max = radio, face_h - radio

    error_u = ag.u <= u_min or ag.u >= u_max
    error_v = ag.v <= v_min or ag.v >= v_max

    if error_u or error_v:
        if error_u and error_v:
            detalle = (
                f"u={ag.u:.3f} fuera de ({u_min:.1f}, {u_max:.1f}), "
                f"v={ag.v:.3f} fuera de ({v_min:.1f}, {v_max:.1f})"
            )
        elif error_u:
            detalle = f"u={ag.u:.3f} fuera del rango ({u_min:.1f}, {u_max:.1f}) mm"
        else:
            detalle = f"v={ag.v:.3f} fuera del rango ({v_min:.1f}, {v_max:.1f}) mm"
        raise ValueError(f"Agujero fuera de la cara '{ag.cara.value}': {detalle}")

    # Validación profundidad (agujero ciego, T-21)
    if ag.tipo == TipoAgujero.ciego and ag.profundidad >= espesor:
        raise ValueError(
            f"Profundidad del agujero ciego ({ag.profundidad}) debe ser < "
            f"espesor de la pieza en esa dirección ({espesor})"
        )

    cq_u, cq_v = _borde_a_cq(ag.cara, ag.u, ag.v, face_w, face_h)
    selector = _CARA_SELECTOR[ag.cara]
    wp = solido.faces(selector).workplane().center(cq_u, cq_v).circle(radio)

    if ag.tipo == TipoAgujero.pasante:
        solido = wp.cutThruAll()
    else:
        solido = wp.cutBlind(-ag.profundidad)

    return solido
