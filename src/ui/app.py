"""
Interfaz Gradio de Artemis.
Servidor local (127.0.0.1). Sin IA activa en el MVP.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from pydantic import ValidationError

from src.schemas.figuras import CilindroParams, PrismaRectangularParams

ARTEMIS_VERSION = "1.0.0"

# Columnas de la tabla de operaciones (en orden de visualización)
_TABLA_HEADERS = ["cara", "diámetro", "u", "v", "tipo", "profundidad"]
_TABLA_TYPES = ["str", "number", "number", "number", "str", "number"]
_TABLA_DEFAULTS = ["superior", 10.0, 0.0, 0.0, "pasante", 0.0]


def generar(
    largo: str = "",
    ancho: str = "",
    alto: str = "",
    diametro: str = "",
    figura: str = "prisma_rectangular",
    vistas_iram: bool = False,
    operaciones: list | None = None,
) -> tuple[str, str | None]:
    """Valida los parámetros del formulario y construye el sólido.

    Retorna (mensaje, ruta_stl) donde ruta_stl es None en caso de error.
    ruta_stl apunta al archivo .stl para el visor 3D Three.js.
    operaciones: lista de dicts con campos de OperacionAgujeroParams.
    """
    faltantes: list[str] = []

    if figura == "prisma_rectangular":
        campos = {"largo": largo, "ancho": ancho, "alto": alto}
        for nombre, valor in campos.items():
            if not valor or not valor.strip():
                faltantes.append(nombre)
        if faltantes:
            return f"Faltan campos obligatorios: {', '.join(faltantes)}", None

        try:
            params = PrismaRectangularParams(
                largo=float(largo),
                ancho=float(ancho),
                alto=float(alto),
                operaciones=operaciones or [],
            )
        except (ValidationError, ValueError) as exc:
            return f"Error de validación: {exc}", None

    elif figura == "cilindro":
        campos = {"diametro": diametro, "alto": alto}
        for nombre, valor in campos.items():
            if not valor or not valor.strip():
                faltantes.append(nombre)
        if faltantes:
            return f"Faltan campos obligatorios: {', '.join(faltantes)}", None

        try:
            params = CilindroParams(
                diametro=float(diametro),
                alto=float(alto),
            )
        except (ValidationError, ValueError) as exc:
            return f"Error de validación: {exc}", None
    else:
        return f"Figura desconocida: {figura}", None

    from src.recipes import prisma_rectangular, cilindro
    from src.export.solid import exportar_stl, exportar_step
    from src.ui.workspace import crear_workspace

    ws = crear_workspace(figura=figura)
    if figura == "prisma_rectangular":
        solido = prisma_rectangular.construir(params)
    else:
        solido = cilindro.construir(params)

    ruta_stl = exportar_stl(solido, ws / f"{figura}.stl")
    ruta_step = exportar_step(solido, ws / f"{figura}.step")

    # Guardar proyecto.json junto al STL para reproducibilidad (T-193)
    proyecto_data = {
        "figura": figura,
        "parametros": params.model_dump(exclude={"vistas_iram"}),
        "version_artemis": ARTEMIS_VERSION,
        "fecha": datetime.now().isoformat(),
    }
    ruta_json = ws / "proyecto.json"
    ruta_json.write_text(json.dumps(proyecto_data, indent=2), encoding="utf-8")

    return f"Generado: {ruta_stl}, {ruta_step}", str(ruta_stl)


def cargar_proyecto_json(ruta_json: str) -> dict:
    """Carga un proyecto.json y devuelve un dict con los campos del formulario.

    Retorna dict con claves: figura, largo, ancho, alto, diametro, operaciones.
    Los valores numéricos se convierten a str para rellenar gr.Textbox.
    Campos ausentes quedan como str vacío.

    Compatibilidad: proyectos con formato viejo (campo 'agujero' en parametros,
    sin version_esquema) se convierten automáticamente al formato nuevo.
    """
    data = json.loads(open(ruta_json, encoding="utf-8").read())
    params = data.get("parametros", {})

    # --- Migración de formato viejo (campo 'agujero') al nuevo (campo 'operaciones') ---
    if "agujero" in params and params["agujero"] is not None:
        agujero_viejo = params["agujero"]
        largo_val = float(params.get("largo", 0))
        ancho_val = float(params.get("ancho", 0))
        alto_val = float(params.get("alto", 0))
        cara = agujero_viejo.get("cara", "superior")

        # Convertir offset_x/offset_y (desde centro) a u/v (desde borde)
        if cara in ("superior", "inferior"):
            u = largo_val / 2 + float(agujero_viejo.get("offset_x", 0))
            v = ancho_val / 2 + float(agujero_viejo.get("offset_y", 0))
        elif cara in ("frontal", "trasera"):
            u = largo_val / 2 + float(agujero_viejo.get("offset_x", 0))
            v = alto_val / 2 + float(agujero_viejo.get("offset_y", 0))
        else:  # lateral_izq / lateral_der
            u = ancho_val / 2 + float(agujero_viejo.get("offset_x", 0))
            v = alto_val / 2 + float(agujero_viejo.get("offset_y", 0))

        operaciones = [
            {
                "tipo": "agujero",
                "diametro": float(agujero_viejo.get("diametro", 10)),
                "cara": cara,
                "subtipo": "pasante",
                "u": u,
                "v": v,
                "profundidad": 0.0,
            }
        ]
    else:
        # Formato nuevo: operaciones ya en la lista (o vacía)
        operaciones_raw = params.get("operaciones", [])
        operaciones = [
            {
                "tipo": op.get("tipo", "agujero"),
                "diametro": float(op.get("diametro", 10)),
                "cara": op.get("cara", "superior"),
                "subtipo": op.get("subtipo", "pasante"),
                "u": float(op.get("u", 0)),
                "v": float(op.get("v", 0)),
                "profundidad": float(op.get("profundidad", 0)),
            }
            for op in operaciones_raw
        ]

    return {
        "figura": data.get("figura", "prisma_rectangular"),
        "largo": str(params["largo"]) if "largo" in params else "",
        "ancho": str(params["ancho"]) if "ancho" in params else "",
        "alto": str(params["alto"]) if "alto" in params else "",
        "diametro": str(params["diametro"]) if "diametro" in params else "",
        "operaciones": operaciones,
    }


def crear_interfaz(conector_ia: Any = None) -> Any:
    """Crea la interfaz Gradio.

    conector_ia=None deshabilita la IA; el formulario arranca vacío.
    Devuelve el objeto gr.Blocks.
    """
    import gradio as gr

    from src.ui.visor import make_viewer_html

    def _tabla_a_operaciones(tabla) -> list[dict]:
        """Convierte el valor de gr.Dataframe a lista de dicts de operaciones."""
        if tabla is None:
            return []
        rows = tabla if isinstance(tabla, list) else tabla.values.tolist()
        ops = []
        for row in rows:
            if not row or len(row) < 6:
                continue
            try:
                ops.append(
                    {
                        "tipo": "agujero",
                        "cara": str(row[0]) if row[0] else "superior",
                        "diametro": float(row[1]) if row[1] is not None else 10.0,
                        "u": float(row[2]) if row[2] is not None else 0.0,
                        "v": float(row[3]) if row[3] is not None else 0.0,
                        "subtipo": str(row[4]) if row[4] else "pasante",
                        "profundidad": float(row[5]) if row[5] is not None else 0.0,
                    }
                )
            except (TypeError, ValueError):
                continue
        return ops

    def generar_con_visor(
        largo: str,
        ancho: str,
        alto: str,
        diametro: str,
        figura: str,
        vistas_iram: bool,
        tabla_agujeros,
    ) -> tuple[str, str, Any, Any, Any]:
        ops = _tabla_a_operaciones(tabla_agujeros)
        mensaje, ruta_stl = generar(largo, ancho, alto, diametro, figura, vistas_iram, ops)

        if ruta_stl is not None:
            from pathlib import Path

            ruta_step_path = Path(ruta_stl).with_suffix(".step")
            ruta_step = str(ruta_step_path) if ruta_step_path.exists() else None
            ruta_json_path = str(Path(ruta_stl).parent / "proyecto.json")
            btn_stl_update = gr.update(visible=True, value=ruta_stl)
            btn_step_update = gr.update(visible=True, value=ruta_step)
            btn_json_update = gr.update(visible=True, value=ruta_json_path)
        else:
            btn_stl_update = gr.update(visible=False, value=None)
            btn_step_update = gr.update(visible=False, value=None)
            btn_json_update = gr.update(visible=False, value=None)
        return (
            mensaje,
            make_viewer_html(ruta_stl),
            btn_stl_update,
            btn_step_update,
            btn_json_update,
        )

    with gr.Blocks(title="Artemis") as demo:
        gr.Markdown("## Artemis — Generador de modelos 3D")

        with gr.Row():
            figura = gr.Dropdown(
                choices=["prisma_rectangular", "cilindro"],
                label="Figura",
                value="prisma_rectangular",
            )

        with gr.Row():
            largo = gr.Textbox(label="Largo (mm)", value="", visible=True)
            ancho = gr.Textbox(label="Ancho (mm)", value="", visible=True)
            alto = gr.Textbox(label="Alto (mm)", value="", visible=True)
            diametro = gr.Textbox(label="Diámetro (mm)", value="", visible=False)

        def actualizar_campos(fig: str):
            es_prisma = fig == "prisma_rectangular"
            return (
                gr.update(visible=es_prisma),
                gr.update(visible=es_prisma),
                gr.update(visible=True),
                gr.update(visible=not es_prisma),
            )

        figura.change(
            fn=actualizar_campos,
            inputs=figura,
            outputs=[largo, ancho, alto, diametro],
        )

        with gr.Row():
            vistas_iram = gr.Checkbox(
                label="Vistas IRAM",
                value=False,
                interactive=False,
                info="Disponible en Phase 5 (US3)",
            )

        # --- Tabla de operaciones (agujeros) ---
        gr.Markdown("### Agujeros")
        tabla_agujeros = gr.Dataframe(
            headers=_TABLA_HEADERS,
            datatype=_TABLA_TYPES,
            row_count=(0, "dynamic"),
            col_count=(6, "fixed"),
            label="Operaciones",
            value=[],
            interactive=True,
        )

        with gr.Row():
            btn_agregar = gr.Button("Agregar fila")
            btn_quitar = gr.Button("Quitar última")

        def _agregar_fila(df):
            rows = df if isinstance(df, list) else df.values.tolist()
            return rows + [list(_TABLA_DEFAULTS)]

        def _quitar_ultima(df):
            rows = df if isinstance(df, list) else df.values.tolist()
            return rows[:-1] if rows else []

        btn_agregar.click(
            fn=_agregar_fila,
            inputs=tabla_agujeros,
            outputs=tabla_agujeros,
        )
        btn_quitar.click(
            fn=_quitar_ultima,
            inputs=tabla_agujeros,
            outputs=tabla_agujeros,
        )

        btn = gr.Button("Generar", variant="primary")
        salida = gr.Textbox(label="Resultado", interactive=False)
        visor = gr.HTML(
            value=make_viewer_html(None),
            label="Vista 3D",
            elem_id="visor-3d",
        )

        with gr.Row():
            btn_stl = gr.DownloadButton(label="Descargar STL", value=None, visible=False)
            btn_step = gr.DownloadButton(label="Descargar STEP", value=None, visible=False)
            btn_json = gr.DownloadButton(label="Descargar proyecto", value=None, visible=False)

        btn.click(
            fn=generar_con_visor,
            inputs=[largo, ancho, alto, diametro, figura, vistas_iram, tabla_agujeros],
            outputs=[salida, visor, btn_stl, btn_step, btn_json],
        )

        # Sección "Abrir proyecto"
        gr.Markdown(
            "---\n### Abrir proyecto\n\n"
            "Para editar una pieza, abrí su proyecto.json. "
            "Los archivos STL y STEP son para impresión y programas de CAD."
        )
        archivo_proyecto = gr.File(label="Cargar proyecto.json", file_types=[".json"])

        def abrir_proyecto(archivo):
            if archivo is None:
                return (
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    gr.update(),
                )
            params = cargar_proyecto_json(archivo.name)
            es_prisma = params["figura"] == "prisma_rectangular"
            ops = params.get("operaciones", [])
            ops_rows = [
                [
                    op["cara"],
                    op["diametro"],
                    op["u"],
                    op["v"],
                    op["subtipo"],
                    op["profundidad"],
                ]
                for op in ops
            ]
            return (
                gr.update(value=params["figura"]),
                gr.update(value=params["largo"], visible=es_prisma),
                gr.update(value=params["ancho"], visible=es_prisma),
                gr.update(value=params["alto"]),
                gr.update(value=params["diametro"], visible=not es_prisma),
                gr.update(value=ops_rows),
            )

        archivo_proyecto.change(
            fn=abrir_proyecto,
            inputs=archivo_proyecto,
            outputs=[figura, largo, ancho, alto, diametro, tabla_agujeros],
        )

    return demo


def iniciar() -> None:
    """Lanza la interfaz Gradio en 127.0.0.1:7860 (loopback exclusivo).

    server_name y server_port son fijos por requisito de seguridad (T-173):
    la app nunca escucha en 0.0.0.0 ni en ninguna IP externa.

    gr.set_static_paths registra src/ui/static/ para que Gradio sirva
    los archivos de Three.js via /file=<ruta_absoluta> sin depender de
    allowed_paths (cuya comparacion de rutas falla en Windows por
    backslashes vs forward-slashes en Gradio 6.x).

    allowed_paths autoriza el workspace para los STL generados dinamicamente.
    """
    import gradio as gr
    from pathlib import Path

    from src.ui.workspace import _WORKSPACE_BASE

    _static_dir = Path(__file__).parent / "static"

    # Registrar directorio estatico antes de crear la interfaz
    gr.set_static_paths(paths=[str(_static_dir)])

    demo = crear_interfaz()
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        allowed_paths=[str(_WORKSPACE_BASE)],
    )


if __name__ == "__main__":
    iniciar()
