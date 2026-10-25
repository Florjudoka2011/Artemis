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
) -> str:
    """Valida los parámetros del formulario y construye el sólido.

    Devuelve un mensaje de error si faltan campos obligatorios,
    o un mensaje de éxito con la ruta de los archivos generados.
    """
    faltantes: list[str] = []

    if figura == "prisma_rectangular":
        campos = {"largo": largo, "ancho": ancho, "alto": alto}
        for nombre, valor in campos.items():
            if not valor or not valor.strip():
                faltantes.append(nombre)
        if faltantes:
            return f"Faltan campos obligatorios: {', '.join(faltantes)}"

        try:
            params = PrismaRectangularParams(
                largo=float(largo),
                ancho=float(ancho),
                alto=float(alto),
            )
        except (ValidationError, ValueError) as exc:
            return f"Error de validación: {exc}"

    elif figura == "cilindro":
        campos = {"diametro": diametro, "alto": alto}
        for nombre, valor in campos.items():
            if not valor or not valor.strip():
                faltantes.append(nombre)
        if faltantes:
            return f"Faltan campos obligatorios: {', '.join(faltantes)}"

        try:
            params = CilindroParams(
                diametro=float(diametro),
                alto=float(alto),
            )
        except (ValidationError, ValueError) as exc:
            return f"Error de validación: {exc}"
    else:
        return f"Figura desconocida: {figura}"

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

    return f"Generado: {ruta_stl}, {ruta_step}"


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
            largo = gr.Textbox(label="Largo (mm)", value="")
            ancho = gr.Textbox(label="Ancho (mm)", value="")
            alto = gr.Textbox(label="Alto (mm)", value="")
            diametro = gr.Textbox(label="Diámetro (mm)", value="")

        with gr.Row():
            vistas_iram = gr.Checkbox(
                label="Vistas IRAM",
                value=False,
                interactive=False,
                info="Disponible en Phase 5 (US3)",
            )

        btn = gr.Button("Generar", variant="primary")
        salida = gr.Textbox(label="Resultado", interactive=False)

        btn.click(
            fn=generar,
            inputs=[largo, ancho, alto, diametro, figura, vistas_iram],
            outputs=salida,
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
