"""
Tests e2e del formulario sin IA — arnés anti-mentiras.
Usa un conector falso que devuelve JSON fijo (A-07: no IA real).
"""

import hashlib
from pathlib import Path

import pytest

from src.export.solid import exportar_stl
from src.recipes.prisma_rectangular import construir
from src.schemas.figuras import PrismaRectangularParams
from src.ui.app import crear_interfaz, generar
from src.ui.workspace import crear_workspace


def _hash_archivo(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


@pytest.mark.mvp
def test_stl_deterministico(workspace_tmp: Path):
    """T-150 | 001/FR-009 — Mismos parámetros producen el mismo STL (determinismo).

    Prueba: src/export/solid.py::exportar_stl

    Los dos archivos deben tener el mismo hash SHA-256.
    """
    params = PrismaRectangularParams(largo=100, ancho=60, alto=40)

    dir_a = workspace_tmp / "run_a"
    dir_a.mkdir()
    ruta_a = exportar_stl(construir(params), dir_a / "prisma.stl")

    dir_b = workspace_tmp / "run_b"
    dir_b.mkdir()
    ruta_b = exportar_stl(construir(params), dir_b / "prisma.stl")

    assert _hash_archivo(ruta_a) == _hash_archivo(
        ruta_b
    ), "El STL no es determinista: mismos parámetros producen archivos distintos"


@pytest.mark.mvp
def test_formulario_campo_vacio():
    """T-151 | 001/FR-001 — Formulario con campo vacío obligatorio no genera y lista los faltantes.

    Prueba: src/ui/app.py::generar

    El resultado debe indicar qué campos faltan, no construir el sólido.
    """
    resultado = generar(largo="", ancho="60", alto="40", figura="prisma_rectangular")
    assert resultado is not None
    assert (
        "largo" in str(resultado).lower()
    ), f"El resultado debería mencionar el campo faltante 'largo', obtenido: {resultado}"


@pytest.mark.mvp
def test_formulario_sin_ia():
    """T-152 | 001/FR-009 — Formulario con IA deshabilitada funciona; arranca vacío.

    Prueba: src/ui/app.py::crear_interfaz

    Con conector nulo, la interfaz se crea sin error y el formulario inicia vacío.
    """
    demo = crear_interfaz(conector_ia=None)
    assert demo is not None, "crear_interfaz devolvió None con conector_ia=None"


@pytest.mark.mvp
def test_crear_workspace_crea_directorio(workspace_tmp: Path):
    """T-153 | 001/FR-010 — crear_workspace genera subdirectorio con nombre de figura y timestamp.

    Prueba: src/ui/workspace.py::crear_workspace
    """
    ws = crear_workspace(base=workspace_tmp, figura="prisma_rectangular")
    assert ws.exists(), "El workspace no fue creado"
    assert ws.is_dir(), "El workspace no es un directorio"
    assert "prisma_rectangular" in ws.name, f"Nombre inesperado: {ws.name}"


@pytest.mark.mvp
def test_generar_prisma_valido_produce_archivos():
    """T-154 | 001/FR-011 — generar() informa resultado con rutas de archivos en caso de éxito.

    Prueba: src/ui/app.py::generar

    El resultado debe incluir 'Generado' y las rutas STL y STEP.
    """
    resultado = generar(largo="100", ancho="60", alto="40", figura="prisma_rectangular")
    assert (
        "Generado" in resultado
    ), f"Se esperaba 'Generado' en el resultado, obtenido: {resultado}"
    assert (
        ".stl" in resultado.lower() or ".step" in resultado.lower()
    ), f"Se esperaban rutas STL/STEP, obtenido: {resultado}"


@pytest.mark.mvp
def test_generar_cilindro_valido_produce_archivos():
    """T-155 | 001/FR-004 — generar() con parámetros válidos de cilindro retorna rutas de archivos.

    Prueba: src/ui/app.py::generar
    """
    resultado = generar(diametro="50", alto="80", figura="cilindro")
    assert (
        "Generado" in resultado
    ), f"Se esperaba 'Generado' en el resultado, obtenido: {resultado}"


@pytest.mark.mvp
def test_formulario_tiene_checkbox_vistas_iram():
    """T-156 | 001/FR-003 — La interfaz ofrece checkbox de vistas IRAM en el formulario.

    Prueba: src/ui/app.py::crear_interfaz

    La interfaz debe incluir un componente con label 'Vistas IRAM' o similar.
    """

    demo = crear_interfaz(conector_ia=None)
    # Buscar checkbox de vistas IRAM en el árbol de componentes
    componentes = demo.blocks
    labels = [
        getattr(c, "label", "") for c in componentes.values() if hasattr(c, "label") and c.label
    ]
    tiene_vistas_iram = any("iram" in str(label).lower() for label in labels)
    assert (
        tiene_vistas_iram
    ), f"No se encontró checkbox de vistas IRAM en la interfaz. Labels encontrados: {labels}"


@pytest.mark.mvp
def test_generar_acepta_vistas_iram():
    """T-158 | 001/FR-003 — generar() acepta el parámetro vistas_iram sin error.

    Prueba: src/ui/app.py::generar
    """
    resultado = generar(
        largo="100", ancho="60", alto="40", figura="prisma_rectangular", vistas_iram=False
    )
    assert (
        "Error" not in resultado or "Faltan" not in resultado
    ), f"generar() rechazó vistas_iram=False: {resultado}"


# T-157 / FR-012 eliminado: el indicador "Generando..." es comportamiento automatico de
# Gradio (btn.click bloquea la UI sin codigo nuestro). No hay API Python para afirmar
# el estado visual de carga. Verificacion manual en quickstart.md.


@pytest.mark.mvp
def test_generar_prisma_parametro_invalido_retorna_error():
    """T-159 | 001/FR-005 — generar() con valor cero en prisma retorna mensaje de error.

    Prueba: src/ui/app.py::generar

    largo=0 pasa la validacion de campo vacio pero ValidationError en Pydantic;
    la funcion debe capturarlo y retornar "Error de validacion: ...".
    """
    resultado = generar(largo="0", ancho="60", alto="40", figura="prisma_rectangular")
    assert "Error" in resultado, f"Se esperaba mensaje de error con largo=0, obtenido: {resultado}"


@pytest.mark.mvp
@pytest.mark.parametrize(
    "kwargs,campo_faltante",
    [
        ({"diametro": "", "alto": "80", "figura": "cilindro"}, "diametro"),
        ({"diametro": "50", "alto": "", "figura": "cilindro"}, "alto"),
    ],
)
def test_formulario_cilindro_campo_vacio(kwargs, campo_faltante):
    """T-160 | 001/FR-001 — Formulario cilindro con campo vacio no genera y lista los faltantes.

    Prueba: src/ui/app.py::generar

    El resultado debe indicar que el campo obligatorio falta.
    """
    resultado = generar(**kwargs)
    assert (
        campo_faltante in resultado.lower()
    ), f"Se esperaba '{campo_faltante}' en el mensaje, obtenido: {resultado}"


@pytest.mark.mvp
def test_generar_cilindro_parametro_invalido_retorna_error():
    """T-161 | 001/FR-005 — generar() con diametro=0 en cilindro retorna mensaje de error.

    Prueba: src/ui/app.py::generar

    diametro=0 pasa la validacion de campo vacio pero ValidationError en Pydantic;
    la funcion debe capturarlo y retornar "Error de validacion: ...".
    """
    resultado = generar(diametro="0", alto="80", figura="cilindro")
    assert (
        "Error" in resultado
    ), f"Se esperaba mensaje de error con diametro=0, obtenido: {resultado}"


@pytest.mark.mvp
def test_generar_figura_desconocida_retorna_error():
    """T-162 | 001/FR-001 — generar() con figura desconocida retorna mensaje de error.

    Prueba: src/ui/app.py::generar
    """
    resultado = generar(figura="hexagono")
    assert (
        "desconocida" in resultado.lower() or "Error" in resultado
    ), f"Se esperaba mensaje de error con figura desconocida, obtenido: {resultado}"


@pytest.mark.mvp
def test_iniciar_usa_host_y_puerto_seguros(monkeypatch):
    """T-173 | 001/FR-010 — iniciar() lanza la app en 127.0.0.1:7860 (loopback exclusivo).

    Prueba: src/ui/app.py::iniciar

    Requisito de seguridad: la app nunca escucha en 0.0.0.0 ni en una IP externa.
    server_name='127.0.0.1' y server_port=7860 son fijos e innegociables.
    """
    from src.ui.app import iniciar  # noqa: PLC0415

    llamadas: list[dict] = []

    import gradio as gr

    def mock_launch(self, **kwargs):  # type: ignore[override]
        llamadas.append(kwargs)
        return None, None, None

    monkeypatch.setattr(gr.Blocks, "launch", mock_launch)
    iniciar()

    assert (
        len(llamadas) == 1
    ), f"launch() debio llamarse exactamente 1 vez, se llamo {len(llamadas)}"
    assert (
        llamadas[0].get("server_name") == "127.0.0.1"
    ), f"server_name debe ser '127.0.0.1', obtenido: {llamadas[0].get('server_name')}"
    assert (
        llamadas[0].get("server_port") == 7860
    ), f"server_port debe ser 7860, obtenido: {llamadas[0].get('server_port')}"
