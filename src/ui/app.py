"""
Interfaz Gradio de Artemis.
Servidor local (127.0.0.1). Sin IA activa en el MVP.
"""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from src.schemas.figuras import CilindroParams, PrismaRectangularParams


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
    ruta_stl apunta al archivo .stl para el visor 3D (gr.Model3D acepta .stl).
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

    return f"Generado: {ruta_stl}, {ruta_step}", str(ruta_stl)


def crear_interfaz(conector_ia: Any = None) -> Any:
    """Crea la interfaz Gradio.

    conector_ia=None deshabilita la IA; el formulario arranca vacío.
    Devuelve el objeto gr.Blocks.
    """
    import gradio as gr

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
        visor = gr.Model3D(label="Vista 3D", value=None)

        btn.click(
            fn=generar,
            inputs=[largo, ancho, alto, diametro, figura, vistas_iram],
            outputs=[salida, visor],
        )

    return demo


def iniciar() -> None:
    """Lanza la interfaz Gradio en 127.0.0.1:7860 (loopback exclusivo).

    server_name y server_port son fijos por requisito de seguridad (T-173):
    la app nunca escucha en 0.0.0.0 ni en ninguna IP externa.
    """
    demo = crear_interfaz()
    demo.launch(server_name="127.0.0.1", server_port=7860)


if __name__ == "__main__":
    iniciar()
