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

_CARAS_PRISMA = ["superior", "inferior", "frontal", "trasera", "lateral_izq", "lateral_der"]
_CARAS_CILINDRO = ["superior", "inferior"]


def generar(
    largo: str = "",
    ancho: str = "",
    alto: str = "",
    diametro: str = "",
    figura: str = "prisma_rectangular",
    vistas_iram: bool = False,
    tiene_agujero: bool = False,
    diametro_agujero: str = "",
    cara_agujero: str = "superior",
    u_agujero: str = "0",
    v_agujero: str = "0",
    tipo_agujero: str = "pasante",
    profundidad_agujero: str = "",
) -> tuple[str, str | None]:
    """Valida los parámetros del formulario y construye el sólido.

    Retorna (mensaje, ruta_stl) donde ruta_stl es None en caso de error.
    ruta_stl apunta al archivo .stl para el visor 3D Three.js.
    """
    from src.schemas.figuras import AgujeroParams, CaraAgujero, TipoAgujero

    agujero_params = None
    if tiene_agujero:
        if not diametro_agujero or not diametro_agujero.strip():
            return "Faltan campos obligatorios: diametro_agujero", None
        try:
            prof = (
                float(profundidad_agujero)
                if profundidad_agujero and profundidad_agujero.strip()
                else None
            )
            agujero_params = AgujeroParams(
                diametro=float(diametro_agujero),
                cara=CaraAgujero(cara_agujero),
                tipo=TipoAgujero(tipo_agujero),
                u=float(u_agujero) if u_agujero and u_agujero.strip() else 0.0,
                v=float(v_agujero) if v_agujero and v_agujero.strip() else 0.0,
                profundidad=prof,
            )
        except (ValidationError, ValueError) as exc:
            return f"Error de validación del agujero: {exc}", None

    faltantes: list[str] = []

    if figura == "prisma_rectangular":
        for nombre, valor in [("largo", largo), ("ancho", ancho), ("alto", alto)]:
            if not valor or not valor.strip():
                faltantes.append(nombre)
        if faltantes:
            return f"Faltan campos obligatorios: {', '.join(faltantes)}", None

        try:
            params = PrismaRectangularParams(
                largo=float(largo),
                ancho=float(ancho),
                alto=float(alto),
                agujero=agujero_params,
            )
        except (ValidationError, ValueError) as exc:
            return f"Error de validación: {exc}", None

    elif figura == "cilindro":
        for nombre, valor in [("diametro", diametro), ("alto", alto)]:
            if not valor or not valor.strip():
                faltantes.append(nombre)
        if faltantes:
            return f"Faltan campos obligatorios: {', '.join(faltantes)}", None

        try:
            params = CilindroParams(
                diametro=float(diametro),
                alto=float(alto),
                agujero=agujero_params,
            )
        except (ValidationError, ValueError) as exc:
            return f"Error de validación: {exc}", None
    else:
        return f"Figura desconocida: {figura}", None

    from src.export.solid import exportar_stl, exportar_step
    from src.recipes import cilindro, prisma_rectangular
    from src.ui.workspace import crear_workspace

    ws = crear_workspace(figura=figura)
    try:
        if figura == "prisma_rectangular":
            solido = prisma_rectangular.construir(params)
        else:
            solido = cilindro.construir(params)
    except ValueError as exc:
        return f"Error geométrico: {exc}", None

    ruta_stl = exportar_stl(solido, ws / f"{figura}.stl")
    ruta_step = exportar_step(solido, ws / f"{figura}.step")

    parametros_dict = params.model_dump(mode="json", exclude={"vistas_iram"})
    proyecto_data = {
        "figura": figura,
        "parametros": parametros_dict,
        "version_artemis": ARTEMIS_VERSION,
        "fecha": datetime.now().isoformat(),
    }
    ruta_json = ws / "proyecto.json"
    ruta_json.write_text(json.dumps(proyecto_data, indent=2), encoding="utf-8")

    return f"Generado: {ruta_stl}, {ruta_step}", str(ruta_stl)


def cargar_proyecto_json(ruta_json: str) -> dict:
    """Carga un proyecto.json y devuelve un dict con los campos del formulario.

    Retorna dict con claves: figura, largo, ancho, alto, diametro,
    tiene_agujero, diametro_agujero, cara_agujero, u_agujero, v_agujero,
    tipo_agujero, profundidad_agujero.
    Los valores numéricos se convierten a str para rellenar gr.Textbox.
    """
    data = json.loads(open(ruta_json, encoding="utf-8").read())
    params = data.get("parametros", {})
    agujero = params.get("agujero")
    return {
        "figura": data.get("figura", "prisma_rectangular"),
        "largo": str(params["largo"]) if "largo" in params else "",
        "ancho": str(params["ancho"]) if "ancho" in params else "",
        "alto": str(params["alto"]) if "alto" in params else "",
        "diametro": str(params["diametro"]) if "diametro" in params else "",
        "tiene_agujero": agujero is not None,
        "diametro_agujero": str(agujero["diametro"]) if agujero else "",
        "cara_agujero": agujero.get("cara", "superior") if agujero else "superior",
        "u_agujero": str(agujero.get("u", 0.0)) if agujero else "0.0",
        "v_agujero": str(agujero.get("v", 0.0)) if agujero else "0.0",
        "tipo_agujero": agujero.get("tipo", "pasante") if agujero else "pasante",
        "profundidad_agujero": (
            str(agujero["profundidad"])
            if agujero and agujero.get("profundidad") is not None
            else ""
        ),
    }


def crear_interfaz(conector_ia: Any = None) -> Any:
    """Crea la interfaz Gradio.

    conector_ia=None deshabilita la IA; el formulario arranca vacío.
    Devuelve el objeto gr.Blocks.
    """
    import gradio as gr

    from src.ui.visor import make_viewer_html

    def generar_con_visor(
        largo,
        ancho,
        alto,
        diametro,
        figura,
        vistas_iram,
        tiene_agujero,
        diametro_agujero,
        cara_agujero,
        u_agujero,
        v_agujero,
        tipo_agujero,
        profundidad_agujero,
    ):
        mensaje, ruta_stl = generar(
            largo,
            ancho,
            alto,
            diametro,
            figura,
            vistas_iram,
            tiene_agujero,
            diametro_agujero,
            cara_agujero,
            u_agujero,
            v_agujero,
            tipo_agujero,
            profundidad_agujero,
        )
        if ruta_stl is not None:
            from pathlib import Path

            ruta_step_path = Path(ruta_stl).with_suffix(".step")
            ruta_step = str(ruta_step_path) if ruta_step_path.exists() else None
            ruta_json = str(Path(ruta_stl).parent / "proyecto.json")
            btn_stl_update = gr.update(visible=True, value=ruta_stl)
            btn_step_update = gr.update(visible=True, value=ruta_step)
            btn_json_update = gr.update(visible=True, value=ruta_json)
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

        with gr.Row():
            tiene_agujero = gr.Checkbox(label="Agregar agujero", value=False)
            diametro_agujero = gr.Textbox(
                label="Diámetro del agujero (mm)", value="", visible=False
            )

        with gr.Row():
            cara_agujero = gr.Dropdown(
                choices=_CARAS_PRISMA,
                label="Cara",
                value="superior",
                visible=False,
            )
            tipo_agujero = gr.Radio(
                choices=["pasante", "ciego"],
                label="Tipo",
                value="pasante",
                visible=False,
            )

        with gr.Row():
            u_agujero = gr.Textbox(label="Desplazamiento u (mm)", value="0", visible=False)
            v_agujero = gr.Textbox(label="Desplazamiento v (mm)", value="0", visible=False)
            profundidad_agujero = gr.Textbox(label="Profundidad (mm)", value="", visible=False)

        def _actualizar_figura(fig, chk):
            es_prisma = fig == "prisma_rectangular"
            caras = _CARAS_PRISMA if es_prisma else _CARAS_CILINDRO
            return (
                gr.update(visible=es_prisma),
                gr.update(visible=es_prisma),
                gr.update(visible=True),
                gr.update(visible=not es_prisma),
                gr.update(choices=caras, value=caras[0]),
                gr.update(visible=chk and es_prisma),
                gr.update(visible=chk and es_prisma),
            )

        figura.change(
            fn=_actualizar_figura,
            inputs=[figura, tiene_agujero],
            outputs=[largo, ancho, alto, diametro, cara_agujero, u_agujero, v_agujero],
        )

        def _toggle_agujero(chk, fig):
            es_prisma = fig == "prisma_rectangular"
            return (
                gr.update(visible=chk),
                gr.update(visible=chk),
                gr.update(visible=chk),
                gr.update(visible=chk and es_prisma),
                gr.update(visible=chk and es_prisma),
                gr.update(visible=False),
            )

        tiene_agujero.change(
            fn=_toggle_agujero,
            inputs=[tiene_agujero, figura],
            outputs=[
                diametro_agujero,
                cara_agujero,
                tipo_agujero,
                u_agujero,
                v_agujero,
                profundidad_agujero,
            ],
        )

        def _toggle_profundidad(tipo):
            return gr.update(visible=tipo == "ciego")

        tipo_agujero.change(
            fn=_toggle_profundidad,
            inputs=tipo_agujero,
            outputs=profundidad_agujero,
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
            btn_json = gr.DownloadButton(label="Descargar proyecto", value=None, visible=False)

        btn.click(
            fn=generar_con_visor,
            inputs=[
                largo,
                ancho,
                alto,
                diametro,
                figura,
                vistas_iram,
                tiene_agujero,
                diametro_agujero,
                cara_agujero,
                u_agujero,
                v_agujero,
                tipo_agujero,
                profundidad_agujero,
            ],
            outputs=[salida, visor, btn_stl, btn_step, btn_json],
        )

        gr.Markdown(
            "---\n### Abrir proyecto\n\n"
            "Para editar una pieza, abrí su proyecto.json. "
            "Los archivos STL y STEP son para impresión y programas de CAD."
        )
        archivo_proyecto = gr.File(label="Cargar proyecto.json", file_types=[".json"])

        def abrir_proyecto(archivo):
            if archivo is None:
                return tuple(gr.update() for _ in range(12))
            p = cargar_proyecto_json(archivo.name)
            es_prisma = p["figura"] == "prisma_rectangular"
            hay_agujero = p.get("tiene_agujero", False)
            tipo = p.get("tipo_agujero", "pasante")
            caras = _CARAS_PRISMA if es_prisma else _CARAS_CILINDRO
            return (
                gr.update(value=p["figura"]),
                gr.update(value=p["largo"], visible=es_prisma),
                gr.update(value=p["ancho"], visible=es_prisma),
                gr.update(value=p["alto"]),
                gr.update(value=p["diametro"], visible=not es_prisma),
                gr.update(value=hay_agujero),
                gr.update(value=p.get("diametro_agujero", ""), visible=hay_agujero),
                gr.update(
                    choices=caras,
                    value=p.get("cara_agujero", "superior"),
                    visible=hay_agujero,
                ),
                gr.update(value=tipo, visible=hay_agujero),
                gr.update(
                    value=p.get("u_agujero", "0"),
                    visible=hay_agujero and es_prisma,
                ),
                gr.update(
                    value=p.get("v_agujero", "0"),
                    visible=hay_agujero and es_prisma,
                ),
                gr.update(
                    value=p.get("profundidad_agujero", ""),
                    visible=hay_agujero and tipo == "ciego",
                ),
            )

        archivo_proyecto.change(
            fn=abrir_proyecto,
            inputs=archivo_proyecto,
            outputs=[
                figura,
                largo,
                ancho,
                alto,
                diametro,
                tiene_agujero,
                diametro_agujero,
                cara_agujero,
                tipo_agujero,
                u_agujero,
                v_agujero,
                profundidad_agujero,
            ],
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

    gr.set_static_paths(paths=[str(_static_dir)])

    demo = crear_interfaz()
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        allowed_paths=[str(_WORKSPACE_BASE)],
    )


if __name__ == "__main__":
    iniciar()
