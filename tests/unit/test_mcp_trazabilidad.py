"""
T-200 | 001/FR-MCP — Tests del servidor MCP artemis-trazabilidad.

Verifica que cada herramienta devuelva exactamente el archivo, la línea
y el texto esperados usando el repo de prueba en tests/fixtures/repo_ejemplo/.
"""

import pathlib
import pytest

REPO = pathlib.Path(__file__).parent.parent / "fixtures" / "repo_ejemplo"


# ── importar las funciones puras del MCP (bajo test sin servidor activo) ──────


@pytest.fixture
def tools():
    """T-200 | 001/FR-MCP — Importar herramientas del servidor MCP."""
    from artemis_trazabilidad.tools import (
        buscar_test,
        funcion_bajo_test,
        requisito,
        estado_tareas,
        ultima_evidencia,
        huecos_trazabilidad,
    )

    return {
        "buscar_test": buscar_test,
        "funcion_bajo_test": funcion_bajo_test,
        "requisito": requisito,
        "estado_tareas": estado_tareas,
        "ultima_evidencia": ultima_evidencia,
        "huecos_trazabilidad": huecos_trazabilidad,
    }


# ── buscar_test ───────────────────────────────────────────────────────────────


@pytest.mark.mvp
def test_buscar_test_retorna_archivo_y_linea(tools):
    """T-201 | 001/FR-MCP — buscar_test devuelve archivo y línea exactos."""
    resultado = tools["buscar_test"](
        test_id="T-100",
        repo_root=str(REPO),
    )
    assert resultado["encontrado"] is True
    assert "test_schemas.py" in resultado["archivo"]
    assert resultado["linea"] == 9  # línea donde empieza test_prisma_valido
    assert "001/FR-005" in resultado["requisito"]
    assert "test_prisma_valido" in resultado["funcion"]


@pytest.mark.mvp
def test_buscar_test_id_inexistente(tools):
    """T-202 | 001/FR-MCP — buscar_test con ID inexistente retorna encontrado=False."""
    resultado = tools["buscar_test"](
        test_id="T-999",
        repo_root=str(REPO),
    )
    assert resultado["encontrado"] is False
    assert "T-999" in resultado["error"]


@pytest.mark.mvp
def test_buscar_test_sin_id_en_docstring(tools):
    """T-203 | 001/FR-MCP — tests sin ID en docstring no aparecen en buscar_test."""
    resultado = tools["buscar_test"](
        test_id="T-SIN-ID",
        repo_root=str(REPO),
    )
    assert resultado["encontrado"] is False


# ── funcion_bajo_test ─────────────────────────────────────────────────────────


@pytest.mark.mvp
def test_funcion_bajo_test_retorna_codigo(tools):
    """T-204 | 001/FR-MCP — funcion_bajo_test retorna código real con archivo y línea."""
    resultado = tools["funcion_bajo_test"](
        test_id="T-100",
        repo_root=str(REPO),
    )
    assert resultado["encontrado"] is True
    assert "figuras.py" in resultado["archivo"]
    assert "positivos" in resultado["codigo"] or "positivos" in resultado.get("funcion_nombre", "")
    assert resultado["linea"] > 0


@pytest.mark.mvp
def test_funcion_bajo_test_id_inexistente(tools):
    """T-205 | 001/FR-MCP — funcion_bajo_test con ID inexistente retorna encontrado=False."""
    resultado = tools["funcion_bajo_test"](
        test_id="T-999",
        repo_root=str(REPO),
    )
    assert resultado["encontrado"] is False


# ── requisito ─────────────────────────────────────────────────────────────────


@pytest.mark.mvp
def test_requisito_retorna_texto_y_tests(tools):
    """T-206 | 001/FR-MCP — requisito devuelve texto del spec y tests que lo cubren."""
    resultado = tools["requisito"](
        req_id="FR-005",
        repo_root=str(REPO),
    )
    assert resultado["encontrado"] is True
    assert "validaci" in resultado["texto"].lower()
    assert isinstance(resultado["tests"], list)
    assert len(resultado["tests"]) >= 1
    ids = [t["id"] for t in resultado["tests"]]
    assert "T-100" in ids


@pytest.mark.mvp
def test_requisito_inexistente(tools):
    """T-207 | 001/FR-MCP — requisito inexistente retorna encontrado=False."""
    resultado = tools["requisito"](
        req_id="FR-999",
        repo_root=str(REPO),
    )
    assert resultado["encontrado"] is False


# ── estado_tareas ─────────────────────────────────────────────────────────────


@pytest.mark.mvp
def test_estado_tareas_agrupa_correctamente(tools):
    """T-208 | 001/FR-MCP — estado_tareas agrupa en hechas, pendientes y bloqueadas."""
    resultado = tools["estado_tareas"](repo_root=str(REPO))
    assert "hechas" in resultado
    assert "pendientes" in resultado
    ids_hechas = [t["id"] for t in resultado["hechas"]]
    ids_pendientes = [t["id"] for t in resultado["pendientes"]]
    assert "T001" in ids_hechas
    assert "T014" in ids_pendientes


# ── ultima_evidencia ──────────────────────────────────────────────────────────


@pytest.mark.mvp
def test_ultima_evidencia_retorna_contenido(tools):
    """T-209 | 001/FR-MCP — ultima_evidencia devuelve la salida más reciente."""
    resultado = tools["ultima_evidencia"](repo_root=str(REPO))
    assert resultado["encontrado"] is True
    assert "2026-10-20" in resultado["archivo"]
    assert "passed" in resultado["contenido"]


@pytest.mark.mvp
def test_ultima_evidencia_sin_archivos(tools):
    """T-210 | 001/FR-MCP — ultima_evidencia sin archivos retorna encontrado=False."""
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "docs", "evidencia", "fase1"))
        resultado = tools["ultima_evidencia"](repo_root=tmp)
    assert resultado["encontrado"] is False


# ── huecos_trazabilidad ───────────────────────────────────────────────────────


@pytest.mark.mvp
def test_huecos_trazabilidad_detecta_test_sin_id(tools):
    """T-211 | 001/FR-MCP — huecos_trazabilidad detecta tests sin ID de trazabilidad."""
    resultado = tools["huecos_trazabilidad"](repo_root=str(REPO))
    sin_id = [t["funcion"] for t in resultado.get("tests_sin_requisito", [])]
    assert "test_sin_id" in sin_id


@pytest.mark.mvp
def test_huecos_trazabilidad_detecta_req_sin_test(tools):
    """T-212 | 001/FR-MCP — huecos_trazabilidad detecta requisitos sin test."""
    resultado = tools["huecos_trazabilidad"](repo_root=str(REPO))
    req_sin_test = [r["id"] for r in resultado.get("requisitos_sin_test", [])]
    assert "FR-004" in req_sin_test
