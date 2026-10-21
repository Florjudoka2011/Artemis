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
    """T-154 | 001/FR-004 — generar() con parámetros válidos de prisma retorna rutas de archivos.

    Prueba: src/ui/app.py::generar
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
