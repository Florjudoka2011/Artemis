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


def generar(
    largo: str = "",
    ancho: str = "",
    alto: str = "",
    diametro: str = "",
    figura: str = "prisma_rectangular",
    vistas_iram: bool = False,
) -> tuple[str, str | None]:
    """Valida los parámetros del formulario y construye el sólido.

    Retorna (mensaje, ruta_stl) donde ruta_stl es None en caso de error.
    ruta_stl apunta al archivo .stl para el visor 3D Three.js.
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
        "parametros": params.model_dump(exclude={"agujero", "vistas_iram"}),
        "version_artemis": ARTEMIS_VERSION,
        "fecha": datetime.now().isoformat(),
    }
    ruta_json = ws / "proyecto.json"
    ruta_json.write_text(json.dumps(proyecto_data, indent=2), encoding="utf-8")

    return f"Generado: {ruta_stl}, {ruta_step}", str(ruta_stl)


def cargar_proyecto_json(ruta_json: str) -> dict:
    """Carga un proyecto.json y devuelve un dict con los campos del formulario.

    Retorna dict con claves: figura, largo, ancho, alto, diametro.
    Los valores numéricos se convierten a str para rellenar gr.Textbox.
    Campos ausentes quedan como str vacío.
    """
    data = json.loads(open(ruta_json, encoding="utf-8").read())
    params = data.get("parametros", {})
    return {
        "figura": data.get("figura", "prisma_rectangular"),
        "largo": str(params["largo"]) if "largo" in params else "",
        "ancho": str(params["ancho"]) if "ancho" in params else "",
        "alto": str(params["alto"]) if "alto" in params else "",
        "diametro": str(params["diametro"]) if "diametro" in params else "",
    }


def crear_interfaz(conector_ia: Any = None) -> Any:
    """Crea la interfaz Gradio.

    conector_ia=None deshabilita la IA; el formulario arranca vacío.
    Devuelve el objeto gr.Blocks.
    """
    import gradio as gr

    from src.ui.visor import make_viewer_html

    # Estado interno para rutas de archivos generados
    _ruta_stl_state: list[str | None] = [None]
    _ruta_step_state: list[str | None] = [None]

    def generar_con_visor(
        largo: str,
        ancho: str,
        alto: str,
        diametro: str,
        figura: str,
        vistas_iram: bool,
    ) -> tuple[str, str, str | None, str | None]:
        mensaje, ruta_stl = generar(largo, ancho, alto, diametro, figura, vistas_iram)
        if ruta_stl is not None:
            from pathlib import Path

            ruta_step_path = Path(ruta_stl).with_suffix(".step")
            ruta_step = str(ruta_step_path) if ruta_step_path.exists() else None
        else:
            ruta_step = None
        return mensaje, make_viewer_html(ruta_stl), ruta_stl, ruta_step

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

        btn.click(
            fn=generar_con_visor,
            inputs=[largo, ancho, alto, diametro, figura, vistas_iram],
            outputs=[salida, visor, btn_stl, btn_step],
        )

        # Sección "Abrir proyecto"
        gr.Markdown("---\n### Abrir proyecto")
        archivo_proyecto = gr.File(label="Cargar proyecto.json", file_types=[".json"])

        def abrir_proyecto(archivo):
            if archivo is None:
                return gr.update(), gr.update(), gr.update(), gr.update(), gr.update()
            params = cargar_proyecto_json(archivo.name)
            es_prisma = params["figura"] == "prisma_rectangular"
            return (
                gr.update(value=params["figura"]),
                gr.update(value=params["largo"], visible=es_prisma),
                gr.update(value=params["ancho"], visible=es_prisma),
                gr.update(value=params["alto"]),
                gr.update(value=params["diametro"], visible=not es_prisma),
            )

        archivo_proyecto.change(
            fn=abrir_proyecto,
            inputs=archivo_proyecto,
            outputs=[figura, largo, ancho, alto, diametro],
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
