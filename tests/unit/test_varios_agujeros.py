"""
Tests para US2 "varios agujeros por pieza" — capa 1+2 del arnés anti-mentiras.

T-200 | Schema: prisma sin operaciones (lista vacía por defecto)
T-201 | Schema: límite de 21 operaciones rechazado
T-202 | Compatibilidad: proyecto.json viejo con campo 'agujero' se convierte
T-203 | Validación: dos agujeros misma cara sin superposición — pasa
T-204 | Validación: dos agujeros superpuestos misma cara — rechazado indicando filas
T-205 | Validación: dos agujeros caras distintas que se cruzan — aceptado
T-206 | Volumen: prisma 100×60×40 con dos agujeros pasantes Ø20 cara superior
T-207 | isInside: cruce de ejes entre caras distintas NO está dentro del sólido
T-208 | UI: crear_interfaz() incluye tabla de agujeros con botones agregar/quitar
"""

import json
import math

import pytest
from pydantic import ValidationError

from src.schemas.figuras import (
    PrismaRectangularParams,
)
from src.recipes.prisma_rectangular import construir
from src.ui.app import cargar_proyecto_json


# ── T-200: lista vacía por defecto ───────────────────────────────────────────


@pytest.mark.mvp
def test_t200_operaciones_lista_vacia():
    """T-200 | 001/FR-020 — Prisma sin operaciones es válido; version_esquema=2.

    Prueba: src/schemas/figuras.py::PrismaRectangularParams
    """
    params = PrismaRectangularParams(largo=100, ancho=60, alto=40)
    assert params.operaciones == []
    assert params.version_esquema == 2


# ── T-201: límite de 21 operaciones ──────────────────────────────────────────


@pytest.mark.mvp
def test_t201_limite_21_operaciones():
    """T-201 | 001/FR-020 — Lista de 21 operaciones es rechazada por el esquema.

    Prueba: src/schemas/figuras.py::PrismaRectangularParams
    """
    ops = [
        {
            "tipo": "agujero",
            "diametro": 5,
            "cara": "superior",
            "subtipo": "pasante",
            "u": 10 + i * 3,
            "v": 10,
        }
        for i in range(21)
    ]
    with pytest.raises(ValidationError):
        PrismaRectangularParams(largo=200, ancho=200, alto=200, operaciones=ops)


# ── T-202: compatibilidad formato viejo ──────────────────────────────────────


@pytest.mark.mvp
def test_t202_compatibilidad_formato_viejo(tmp_path):
    """T-202 | 001/FR-020 — cargar_proyecto_json convierte formato viejo al nuevo.

    Formato viejo: campo 'agujero' en parametros (sin version_esquema).

    Prueba: src/ui/app.py::cargar_proyecto_json

    Un proyecto.json generado antes de version_esquema=2 tiene 'agujero' (dict único)
    en lugar de 'operaciones' (lista). La carga debe convertirlo sin error.
    """
    viejo = {
        "figura": "prisma_rectangular",
        "parametros": {
            "largo": 100.0,
            "ancho": 60.0,
            "alto": 40.0,
            "agujero": {
                "diametro": 20.0,
                "cara": "superior",
                "offset_x": 0.0,
                "offset_y": 0.0,
            },
        },
        "version_artemis": "1.0.0",
        "fecha": "2026-10-25T00:00:00",
    }
    ruta = tmp_path / "proyecto_viejo.json"
    ruta.write_text(json.dumps(viejo), encoding="utf-8")

    result = cargar_proyecto_json(str(ruta))

    assert "operaciones" in result, "Debe retornar clave 'operaciones'"
    assert isinstance(result["operaciones"], list)
    assert len(result["operaciones"]) == 1
    op = result["operaciones"][0]
    assert op["tipo"] == "agujero"
    assert op["diametro"] == 20.0
    assert op["cara"] == "superior"


# ── T-203: dos agujeros misma cara sin superposición ─────────────────────────


@pytest.mark.mvp
def test_t203_dos_agujeros_sin_superposicion():
    """T-203 | 001/FR-020 — Dos agujeros misma cara a distancia suficiente: validación pasa.

    Prueba: src/schemas/figuras.py::PrismaRectangularParams (model_validator)

    Distancia entre centros = 50mm > r1+r2+1 = 21mm.
    """
    params = PrismaRectangularParams(
        largo=100,
        ancho=60,
        alto=40,
        operaciones=[
            {
                "tipo": "agujero",
                "diametro": 20,
                "cara": "superior",
                "subtipo": "pasante",
                "u": 25,
                "v": 30,
            },
            {
                "tipo": "agujero",
                "diametro": 20,
                "cara": "superior",
                "subtipo": "pasante",
                "u": 75,
                "v": 30,
            },
        ],
    )
    assert len(params.operaciones) == 2


# ── T-204: dos agujeros superpuestos misma cara ───────────────────────────────


@pytest.mark.mvp
def test_t204_dos_agujeros_superpuestos_rechazado():
    """T-204 | 001/FR-020 — Dos agujeros superpuestos misma cara → rechazado indicando filas.

    Prueba: src/schemas/figuras.py::PrismaRectangularParams (model_validator)

    Distancia entre centros = 5mm < r1+r2+1 = 21mm.
    El mensaje de error debe citar los números de fila (base 1).
    """
    with pytest.raises(ValidationError) as exc_info:
        PrismaRectangularParams(
            largo=100,
            ancho=60,
            alto=40,
            operaciones=[
                {
                    "tipo": "agujero",
                    "diametro": 20,
                    "cara": "superior",
                    "subtipo": "pasante",
                    "u": 30,
                    "v": 30,
                },
                {
                    "tipo": "agujero",
                    "diametro": 20,
                    "cara": "superior",
                    "subtipo": "pasante",
                    "u": 35,
                    "v": 30,
                },
            ],
        )
    msg = str(exc_info.value)
    assert (
        "1" in msg and "2" in msg
    ), f"El mensaje de error debe citar las filas 1 y 2. Mensaje: {msg}"


# ── T-205: dos agujeros caras distintas que se cruzan ────────────────────────


@pytest.mark.mvp
def test_t205_agujeros_caras_distintas_aceptado():
    """T-205 | 001/FR-020 — Dos agujeros en caras distintas que se cruzan → aceptado.

    Prueba: src/schemas/figuras.py::PrismaRectangularParams (model_validator)

    La regla de distancia mínima aplica sólo a agujeros en la misma cara.
    Ver docs/ADR/002-agujeros-caras-distintas.md para la justificación.
    """
    params = PrismaRectangularParams(
        largo=100,
        ancho=60,
        alto=40,
        operaciones=[
            {
                "tipo": "agujero",
                "diametro": 20,
                "cara": "superior",
                "subtipo": "pasante",
                "u": 50,
                "v": 30,
            },
            {
                "tipo": "agujero",
                "diametro": 20,
                "cara": "frontal",
                "subtipo": "pasante",
                "u": 50,
                "v": 20,
            },
        ],
    )
    assert len(params.operaciones) == 2


# ── T-206: volumen con dos agujeros pasantes cara superior ───────────────────


@pytest.mark.mvp
def test_t206_volumen_dos_agujeros_pasantes():
    """T-206 | 001/FR-020 — Volumen prisma 100×60×40 con dos agujeros pasantes Ø20 cara superior.

    Prueba: src/recipes/prisma_rectangular.py::construir

    Valor esperado: 240000 − 2×π×10²×40 ≈ 214867.259 mm³ (tolerancia 1 mm³).
    """
    params = PrismaRectangularParams(
        largo=100,
        ancho=60,
        alto=40,
        operaciones=[
            {
                "tipo": "agujero",
                "diametro": 20,
                "cara": "superior",
                "subtipo": "pasante",
                "u": 25,
                "v": 30,
            },
            {
                "tipo": "agujero",
                "diametro": 20,
                "cara": "superior",
                "subtipo": "pasante",
                "u": 75,
                "v": 30,
            },
        ],
    )
    solido = construir(params)
    volumen = solido.val().Volume()
    esperado = 240000 - 2 * math.pi * 10**2 * 40
    assert abs(volumen - esperado) < 1.0, (
        f"Volumen esperado ≈{esperado:.3f} mm³, obtenido {volumen:.3f} mm³. "
        f"Diferencia: {abs(volumen - esperado):.4f} mm³"
    )


# ── T-207: isInside — cruce de ejes caras distintas ─────────────────────────


@pytest.mark.mvp
def test_t207_cruce_ejes_no_dentro_del_solido():
    """T-207 | 001/FR-020 — Agujeros en caras distintas: el punto de cruce de ejes NO está dentro.

    Prueba: src/recipes/prisma_rectangular.py::construir

    Hole 1: cara superior, u=50, v=30  → eje vertical en (0, 0, z)
    Hole 2: cara frontal,  u=50, v=20  → eje horizontal en (0, y, 20)
    Cruce:  (0, 0, 20) — debe estar FUERA del sólido porque ambos cilindros lo eliminan.
    """
    import cadquery as cq

    params = PrismaRectangularParams(
        largo=100,
        ancho=60,
        alto=40,
        operaciones=[
            {
                "tipo": "agujero",
                "diametro": 20,
                "cara": "superior",
                "subtipo": "pasante",
                "u": 50,
                "v": 30,
            },
            {
                "tipo": "agujero",
                "diametro": 20,
                "cara": "frontal",
                "subtipo": "pasante",
                "u": 50,
                "v": 20,
            },
        ],
    )
    solido = construir(params)
    punto_cruce = cq.Vector(0, 0, 20)
    assert not solido.val().isInside(punto_cruce), (
        "El punto de cruce de los ejes (0, 0, 20) debe estar FUERA del sólido. "
        "Ambos agujeros perforados eliminan ese material."
    )


# ── T-208: UI tabla de agujeros con botones ──────────────────────────────────


@pytest.mark.mvp
def test_t208_interfaz_tiene_tabla_agujeros():
    """T-208 | 001/FR-020 — crear_interfaz() incluye tabla de agujeros + botones agregar/quitar.

    Prueba: src/ui/app.py::crear_interfaz

    La interfaz debe tener:
    - Al menos un gr.Dataframe (tabla de operaciones)
    - Un botón con "Agregar" en el label
    - Un botón con "Quitar" en el label
    """
    import gradio as gr
    from src.ui.app import crear_interfaz

    demo = crear_interfaz()

    dataframes = [c for c in demo.blocks.values() if isinstance(c, gr.Dataframe)]
    assert len(dataframes) >= 1, (
        f"crear_interfaz() debe incluir al menos un gr.Dataframe para la tabla de agujeros. "
        f"Componentes: {[type(c).__name__ for c in demo.blocks.values()]}"
    )

    buttons = [c for c in demo.blocks.values() if isinstance(c, gr.Button)]
    button_labels = [getattr(c, "value", "") or "" for c in buttons]
    agregar = any("gregar" in lbl for lbl in button_labels)
    quitar = any("uitar" in lbl for lbl in button_labels)
    assert agregar, f"Debe haber botón con 'Agregar'. Botones encontrados: {button_labels}"
    assert quitar, f"Debe haber botón con 'Quitar'. Botones encontrados: {button_labels}"
