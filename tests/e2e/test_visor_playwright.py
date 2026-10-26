"""
Test Playwright headless para verificar que el visor Three.js renderiza.

Abre la app Gradio, genera un prisma, captura el area del visor y
verifica que el canvas no es de un solo color (confirmacion de render).

Requiere la app corriendo: python -m src.ui.app (puerto 7860).
Este test se ejecuta manualmente (no esta marcado mvp) porque requiere
un servidor activo. Ver instrucciones al final del archivo.

Guarda la captura en docs/evidencia/fase1/ para revision visual del usuario.
"""

from __future__ import annotations

from pathlib import Path

import pytest


EVIDENCIA_DIR = Path(__file__).parents[2] / "docs" / "evidencia" / "fase1"
APP_URL = "http://127.0.0.1:7860"


@pytest.fixture(scope="module")
def browser_page():
    """Fixture que abre el navegador headless y navega a la app."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.goto(APP_URL, timeout=30_000)
        yield page
        browser.close()


@pytest.mark.visor
def test_visor_renderiza_modelo_3d(browser_page):
    """T-189 — El visor Three.js renderiza el modelo (canvas no es un solo color).

    Flujo manual de punta a punta:
    1. Abre http://127.0.0.1:7860 en Chromium headless.
    2. Completa largo=100, ancho=60, alto=40 (prisma rectangular).
    3. Hace clic en Generar.
    4. Espera a que aparezca el visor (iframe con canvas).
    5. Captura screenshot del area del visor.
    6. Analiza los pixels: si el canvas es un solo color solido, el
       render fallo. Se espera variacion de al menos 10 valores distintos.
    7. Guarda la captura en docs/evidencia/fase1/.
    """
    page = browser_page

    # Esperar que Gradio 6.x cargue los textboxes (renderizados como textarea)
    page.wait_for_selector("textarea", timeout=30_000)
    page.wait_for_timeout(1000)

    # Buscar los campos de texto (Gradio 6.x usa <textarea> para gr.Textbox)
    textareas = page.query_selector_all("textarea")
    # Los 3 primeros textareas visibles con ancho ~400 son largo, ancho, alto.
    # El ultimo textarea (ancho ~1190) es el campo Resultado (output, no editar).
    visible_textareas = [t for t in textareas if t.is_visible()]
    input_textareas = visible_textareas[:3]  # largo, ancho, alto
    assert (
        len(input_textareas) >= 3
    ), f"Se esperaban al menos 3 textareas visibles, encontrados: {len(visible_textareas)}"

    input_textareas[0].fill("100")  # largo
    input_textareas[1].fill("60")  # ancho
    input_textareas[2].fill("40")  # alto

    # Clic en Generar
    page.click('button:has-text("Generar")')

    # Esperar resultado (mensaje de exito o cambio en el visor)
    page.wait_for_selector("#visor-3d iframe", timeout=30_000)

    # Dar tiempo al Three.js para renderizar
    page.wait_for_timeout(3000)

    # Capturar screenshot del area del visor
    EVIDENCIA_DIR.mkdir(parents=True, exist_ok=True)
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    screenshot_path = EVIDENCIA_DIR / f"{timestamp}_visor_playwright.png"

    visor_elem = page.query_selector("#visor-3d")
    assert visor_elem is not None, "No se encontro el elemento #visor-3d en la pagina"

    visor_elem.screenshot(path=str(screenshot_path))
    print(f"\nCaptura guardada en: {screenshot_path}")

    # Verificar que la imagen no es un solo color (el render funciono)
    _verificar_variacion_pixels(screenshot_path)


def _verificar_variacion_pixels(screenshot_path: Path) -> None:
    """Verifica que la imagen tiene variacion de color (no es pantalla solida)."""
    try:
        from PIL import Image
        import numpy as np

        img = Image.open(screenshot_path).convert("RGB")
        arr = np.array(img)

        # Obtener valores R de toda la imagen
        canal_r = arr[:, :, 0].flatten().tolist()
        valores_unicos = len(set(canal_r))

        assert valores_unicos >= 10, (
            f"El visor parece ser un color solido ({valores_unicos} valores unicos "
            f"en canal R). El render Three.js probablemente fallo. "
            f"Ver captura: {screenshot_path}"
        )
    except ImportError:
        # Pillow/numpy no disponibles: verificacion basica por tamano de archivo
        size_kb = screenshot_path.stat().st_size / 1024
        assert size_kb > 5, (
            f"El screenshot es muy pequeno ({size_kb:.1f} KB), posible pantalla vacia. "
            f"Ver captura: {screenshot_path}"
        )
        print(
            f"AVISO: Pillow no disponible. Verificacion por tamano: {size_kb:.1f} KB. "
            "Instalar Pillow para verificacion de pixels: pip install Pillow"
        )
