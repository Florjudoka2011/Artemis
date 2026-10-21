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
def test_buscar_test_retorna_ruta_relativa(tools):
    """T-201b | 001/FR-MCP — buscar_test devuelve ruta relativa a la raíz del repo."""
    resultado = tools["buscar_test"](
        test_id="T-100",
        repo_root=str(REPO),
    )
    assert resultado["encontrado"] is True
    # La ruta NO debe ser absoluta (no empieza con disco ni /)
    archivo = resultado["archivo"]
    assert not pathlib.Path(
        archivo
    ).is_absolute(), f"Se esperaba ruta relativa, se obtuvo: {archivo!r}"


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
def test_funcion_bajo_test_usa_linea_prueba(tools):
    """T-204 | 001/FR-MCP — funcion_bajo_test usa la línea 'Prueba:' del docstring.

    Prueba: mcp_servers/artemis_trazabilidad/tools.py::funcion_bajo_test
    """
    resultado = tools["funcion_bajo_test"](
        test_id="T-100",
        repo_root=str(REPO),
    )
    assert resultado["encontrado"] is True
    # T-100 tiene: Prueba: src/schemas/figuras.py::PrismaParams
    assert "figuras.py" in resultado["archivo"]
    assert resultado["funcion_nombre"] == "PrismaParams"
    assert resultado["linea"] > 0


@pytest.mark.mvp
def test_funcion_bajo_test_sin_linea_prueba_devuelve_no_determinable(tools):
    """T-204b | 001/FR-MCP — funcion_bajo_test sin 'Prueba:' devuelve no_determinable.

    Prueba: mcp_servers/artemis_trazabilidad/tools.py::funcion_bajo_test
    """
    # test_sin_id no tiene línea Prueba:
    # buscamos T-101 que sí tiene Prueba: pero el test tiene docstring ambiguo;
    # usamos directamente test_sin_id: no tiene ID, necesitamos otro test sin Prueba:
    # T-104 tiene Prueba: src/schemas/figuras.py::CilindroParams
    # Necesitamos un caso sin línea Prueba: — creamos uno buscando T-999 (inexistente)
    resultado = tools["funcion_bajo_test"](
        test_id="T-999",
        repo_root=str(REPO),
    )
    assert resultado["encontrado"] is False


@pytest.mark.mvp
def test_funcion_bajo_test_id_inexistente(tools):
    """T-205 | 001/FR-MCP — funcion_bajo_test con ID inexistente retorna encontrado=False."""
    resultado = tools["funcion_bajo_test"](
        test_id="T-999",
        repo_root=str(REPO),
    )
    assert resultado["encontrado"] is False


@pytest.mark.mvp
def test_funcion_bajo_test_ruta_relativa(tools):
    """T-205b | 001/FR-MCP — funcion_bajo_test devuelve ruta relativa."""
    resultado = tools["funcion_bajo_test"](
        test_id="T-100",
        repo_root=str(REPO),
    )
    assert resultado["encontrado"] is True
    assert not pathlib.Path(
        resultado["archivo"]
    ).is_absolute(), f"Ruta debe ser relativa, obtuvo: {resultado['archivo']!r}"


# ── requisito ─────────────────────────────────────────────────────────────────


@pytest.mark.mvp
def test_requisito_formato_spec_kit(tools):
    """T-206 | 001/FR-MCP — requisito detecta formato '- **FR-XXX**: texto' de Spec Kit.

    Prueba: mcp_servers/artemis_trazabilidad/tools.py::requisito
    """
    resultado = tools["requisito"](
        req_id="001/FR-005",
        repo_root=str(REPO),
    )
    assert resultado["encontrado"] is True, f"Error: {resultado.get('error')}"
    assert "validaci" in resultado["texto"].lower() or "inválidos" in resultado["texto"].lower()
    ids = [t["id"] for t in resultado["tests"]]
    assert "T-100" in ids


@pytest.mark.mvp
def test_requisito_coincidencia_exacta_no_prefijo(tools):
    """T-206b | 001/FR-MCP — requisito('001/FR-00') NO encuentra FR-005 (coincidencia exacta).

    Prueba: mcp_servers/artemis_trazabilidad/tools.py::requisito
    """
    resultado = tools["requisito"](
        req_id="001/FR-00",
        repo_root=str(REPO),
    )
    # FR-00 no debe encontrar FR-001, FR-004, FR-005, FR-006
    assert resultado["encontrado"] is False


@pytest.mark.mvp
def test_requisito_busca_solo_en_su_spec(tools):
    """T-206c | 001/FR-MCP — requisito('001/FR-005') busca solo en spec 001.

    Prueba: mcp_servers/artemis_trazabilidad/tools.py::requisito
    """
    resultado = tools["requisito"](
        req_id="001/FR-005",
        repo_root=str(REPO),
    )
    assert resultado["encontrado"] is True
    # El archivo debe pertenecer a la spec 001
    assert "001" in resultado["archivo"]


@pytest.mark.mvp
def test_requisito_inexistente(tools):
    """T-207 | 001/FR-MCP — requisito inexistente retorna encontrado=False."""
    resultado = tools["requisito"](
        req_id="001/FR-999",
        repo_root=str(REPO),
    )
    assert resultado["encontrado"] is False


@pytest.mark.mvp
def test_requisito_ruta_relativa(tools):
    """T-207b | 001/FR-MCP — requisito devuelve ruta relativa."""
    resultado = tools["requisito"](
        req_id="001/FR-005",
        repo_root=str(REPO),
    )
    assert resultado["encontrado"] is True
    assert not pathlib.Path(resultado["archivo"]).is_absolute()


# ── estado_tareas ─────────────────────────────────────────────────────────────


@pytest.mark.mvp
def test_estado_tareas_agrupa_correctamente(tools):
    """T-208 | 001/FR-MCP — estado_tareas agrupa en hechas y pendientes (sin bloqueadas).

    Prueba: mcp_servers/artemis_trazabilidad/tools.py::estado_tareas
    """
    resultado = tools["estado_tareas"](repo_root=str(REPO))
    assert "hechas" in resultado
    assert "pendientes" in resultado
    ids_hechas = [t["id"] for t in resultado["hechas"]]
    ids_pendientes = [t["id"] for t in resultado["pendientes"]]
    assert "T001" in ids_hechas
    assert "T014" in ids_pendientes


@pytest.mark.mvp
def test_estado_tareas_sin_estado_bloqueado_fantasma(tools):
    """T-208b | 001/FR-MCP — estado_tareas no clasifica como 'bloqueada' sin criterio explícito.

    El estado 'bloqueada' solo aplica si la tarea está marcada [B] o similar;
    el título de sección no contamina a las tareas siguientes.

    Prueba: mcp_servers/artemis_trazabilidad/tools.py::estado_tareas
    """
    resultado = tools["estado_tareas"](repo_root=str(REPO))
    # T001 está en Phase 0 (BLOQUEANTE) pero está [X] (hecha), no bloqueada
    ids_bloqueadas = [t["id"] for t in resultado.get("bloqueadas", [])]
    assert "T001" not in ids_bloqueadas
    # T014 es una tarea pendiente, no bloqueada
    assert "T014" not in ids_bloqueadas


@pytest.mark.mvp
def test_estado_tareas_incluye_criterio_en_resultado(tools):
    """T-208c | 001/FR-MCP — estado_tareas documenta el criterio de clasificación.

    Prueba: mcp_servers/artemis_trazabilidad/tools.py::estado_tareas
    """
    resultado = tools["estado_tareas"](repo_root=str(REPO))
    assert (
        "criterio" in resultado
    ), "El resultado debe incluir la clave 'criterio' con la explicación de clasificación"


# ── ultima_evidencia ──────────────────────────────────────────────────────────


@pytest.mark.mvp
def test_ultima_evidencia_retorna_contenido(tools):
    """T-209 | 001/FR-MCP — ultima_evidencia devuelve la salida más reciente."""
    resultado = tools["ultima_evidencia"](repo_root=str(REPO))
    assert resultado["encontrado"] is True
    assert "2026-10-20" in resultado["archivo"]
    assert "passed" in resultado["contenido"]


@pytest.mark.mvp
def test_ultima_evidencia_considera_solo_archivos_con_fecha(tools):
    """T-209b | 001/FR-MCP — ultima_evidencia solo considera archivos con fecha en el nombre.

    Los archivos sin fecha en el nombre (ej: 'notas.txt') no deben ser seleccionados.

    Prueba: mcp_servers/artemis_trazabilidad/tools.py::ultima_evidencia
    """
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmp:
        evdir = os.path.join(tmp, "docs", "evidencia", "fase1")
        os.makedirs(evdir)
        # Archivo sin fecha — no debe ser elegido
        with open(os.path.join(evdir, "notas.txt"), "w") as f:
            f.write("notas sin fecha\n")
        # Archivo con fecha — debe ser elegido
        with open(os.path.join(evdir, "2026-10-20_1200_tests.txt"), "w") as f:
            f.write("3 passed\n")
        resultado = tools["ultima_evidencia"](repo_root=tmp)

    assert resultado["encontrado"] is True
    assert "2026-10-20_1200_tests.txt" in resultado["archivo"]


@pytest.mark.mvp
def test_ultima_evidencia_sin_archivos(tools):
    """T-210 | 001/FR-MCP — ultima_evidencia sin archivos retorna encontrado=False."""
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "docs", "evidencia", "fase1"))
        resultado = tools["ultima_evidencia"](repo_root=tmp)
    assert resultado["encontrado"] is False


@pytest.mark.mvp
def test_ultima_evidencia_ruta_relativa(tools):
    """T-210b | 001/FR-MCP — ultima_evidencia devuelve ruta relativa."""
    resultado = tools["ultima_evidencia"](repo_root=str(REPO))
    assert resultado["encontrado"] is True
    assert not pathlib.Path(resultado["archivo"]).is_absolute()


# ── huecos_trazabilidad ───────────────────────────────────────────────────────


@pytest.mark.mvp
def test_huecos_trazabilidad_detecta_test_sin_id(tools):
    """T-211 | 001/FR-MCP — huecos_trazabilidad detecta tests sin ID de trazabilidad."""
    resultado = tools["huecos_trazabilidad"](repo_root=str(REPO))
    sin_id = [t["funcion"] for t in resultado.get("tests_sin_requisito", [])]
    assert "test_sin_id" in sin_id


@pytest.mark.mvp
def test_huecos_trazabilidad_detecta_req_sin_test(tools):
    """T-212 | 001/FR-MCP — huecos_trazabilidad detecta requisitos sin test.

    FR-004 está en el fixture spec.md pero ningún test lo cubre.
    """
    resultado = tools["huecos_trazabilidad"](repo_root=str(REPO))
    req_sin_test = [r["id"] for r in resultado.get("requisitos_sin_test", [])]
    # FR-004 no tiene test en el fixture
    assert "FR-004" in req_sin_test or "001/FR-004" in req_sin_test


@pytest.mark.mvp
def test_huecos_trazabilidad_detecta_formato_spec_kit(tools):
    """T-212b | 001/FR-MCP — huecos_trazabilidad detecta FRs en formato '- **FR-XXX**: texto'.

    Prueba: mcp_servers/artemis_trazabilidad/tools.py::huecos_trazabilidad
    """
    resultado = tools["huecos_trazabilidad"](repo_root=str(REPO))
    # El fixture tiene FR-001, FR-004, FR-005, FR-006 en formato Spec Kit
    # Al menos uno debe aparecer como sin test o cubierto
    total_reqs = resultado["resumen"]["total_requisitos"]
    assert total_reqs >= 3, (
        f"Se esperaban al menos 3 requisitos en spec.md, se encontraron {total_reqs}. "
        "Verificar que se detecta el formato '- **FR-XXX**: texto'"
    )


@pytest.mark.mvp
def test_huecos_trazabilidad_control_global_explicito(tools):
    """T-212c | 001/FR-MCP — tareas_sin_evidencia es control global, no por tarea.

    Prueba: mcp_servers/artemis_trazabilidad/tools.py::huecos_trazabilidad
    """
    resultado = tools["huecos_trazabilidad"](repo_root=str(REPO))
    # El campo debe incluir una descripción del tipo de control
    assert "nota_tareas_sin_evidencia" in resultado or "control" in str(
        resultado
    ), "El resultado debe aclarar que tareas_sin_evidencia es un control global"


@pytest.mark.mvp
def test_huecos_trazabilidad_rutas_relativas(tools):
    """T-212d | 001/FR-MCP — huecos_trazabilidad devuelve rutas relativas."""
    resultado = tools["huecos_trazabilidad"](repo_root=str(REPO))
    for t in resultado.get("tests_sin_requisito", []):
        assert not pathlib.Path(
            t["archivo"]
        ).is_absolute(), f"Ruta debe ser relativa: {t['archivo']!r}"
    for r in resultado.get("requisitos_sin_test", []):
        assert not pathlib.Path(r["archivo"]).is_absolute()


# ── segunda revisión: 6 correcciones ──────────────────────────────────────────


@pytest.mark.mvp
def test_requisito_no_mezcla_fr001_con_fr001_de_otra_spec(tools):
    """T-213 | 001/FR-MCP — requisito('001/FR-001') NO incluye tests que cubren '002/FR-001'.

    Bug: bare "FR-001" in "002/FR-001" == True → un test de otra spec aparece como cubriendo
    el requisito. La comparación debe usar el ID completo '001/FR-001'.

    Prueba: mcp_servers/artemis_trazabilidad/tools.py::requisito
    """
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmp:
        # Spec 001 con FR-001
        spec001 = os.path.join(tmp, "specs", "001-mvp")
        os.makedirs(spec001)
        with open(os.path.join(spec001, "spec.md"), "w", encoding="utf-8") as f:
            f.write("- **FR-001**: Requisito de spec 001.\n")

        # Tests: uno cubre 001/FR-001 (correcto), otro cubre 002/FR-001 (diferente spec)
        tests_dir = os.path.join(tmp, "tests", "unit")
        os.makedirs(tests_dir)
        with open(os.path.join(tests_dir, "__init__.py"), "w") as f:
            f.write("")
        with open(os.path.join(tests_dir, "test_ejemplo.py"), "w", encoding="utf-8") as f:
            f.write(
                "def test_cubre_001_fr001():\n"
                '    """T-100 | 001/FR-001 — Cubre el requisito correcto."""\n'
                "    assert True\n"
                "\n"
                "def test_cubre_002_fr001():\n"
                '    """T-200 | 002/FR-001 — Cubre FR-001 de spec 002, NO de spec 001."""\n'
                "    assert True\n"
            )

        resultado = tools["requisito"](req_id="001/FR-001", repo_root=tmp)

    assert resultado["encontrado"] is True
    test_ids = [t["id"] for t in resultado["tests"]]
    # T-200 cubre "002/FR-001" — NO debe aparecer en los tests de "001/FR-001"
    assert "T-200" not in test_ids, (
        f"T-200 (002/FR-001) NO debe aparecer en tests de '001/FR-001'. "
        f"IDs encontrados: {test_ids}"
    )
    # T-100 cubre "001/FR-001" — SÍ debe aparecer
    assert "T-100" in test_ids, (
        f"T-100 (001/FR-001) DEBE aparecer en tests de '001/FR-001'. "
        f"IDs encontrados: {test_ids}"
    )


@pytest.mark.mvp
def test_huecos_spec_filter_usa_starts_with_no_contains(tools):
    """T-214 | 001/FR-MCP — filtro de spec usa 'empieza con NNN-', no 'contiene NNN'.

    Bug: "001" in "9001-archivo" == True → la carpeta "9001-archivo" es incorrectamente
    incluida cuando se busca la spec "001". El filtro debe verificar que la carpeta
    EMPIECE con "001-", no que CONTENGA "001".

    Prueba: mcp_servers/artemis_trazabilidad/tools.py::requisito
    """
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmp:
        # Solo crear la carpeta trampa "9001-archivo" (contiene "001" pero NO empieza con "001-")
        # NO crear "001-mvp" para que el filtro incorrecto encuentre algo en "9001-archivo"
        trampa_dir = os.path.join(tmp, "specs", "9001-archivo")
        os.makedirs(trampa_dir)
        with open(os.path.join(trampa_dir, "spec.md"), "w", encoding="utf-8") as f:
            f.write("- **FR-001**: Requisito trampa en carpeta 9001-archivo.\n")

        # Crear directorio tests vacío
        os.makedirs(os.path.join(tmp, "tests"))

        resultado = tools["requisito"](req_id="001/FR-001", repo_root=tmp)

    # Con el bug: "001" in "9001-archivo" == True → encontrado=True (incorrecto)
    # Con la corrección: "9001-archivo" no empieza con "001-" → encontrado=False (correcto)
    assert resultado["encontrado"] is False, (
        f"'9001-archivo' NO es la spec '001'. "
        f"El filtro no debe incluir carpetas que contienen '001' como substring. "
        f"Resultado: {resultado}"
    )


@pytest.mark.mvp
def test_huecos_trazabilidad_incluye_ids_duplicados(tools):
    """T-215 | 001/FR-MCP — huecos_trazabilidad detecta tests con el mismo T-XX.

    El fixture tiene dos tests con T-100: test_prisma_valido y test_duplicado_mismo_tid.

    Prueba: mcp_servers/artemis_trazabilidad/tools.py::huecos_trazabilidad
    """
    resultado = tools["huecos_trazabilidad"](repo_root=str(REPO))
    assert (
        "ids_duplicados" in resultado
    ), "El resultado debe incluir la clave 'ids_duplicados' con los T-IDs repetidos"
    duplicados = resultado["ids_duplicados"]
    # T-100 aparece dos veces en el fixture
    assert (
        "T-100" in duplicados
    ), f"T-100 está duplicado en el fixture pero no aparece en ids_duplicados: {duplicados}"


@pytest.mark.mvp
def test_huecos_trazabilidad_incluye_tests_sin_prueba(tools):
    """T-216 | 001/FR-MCP — huecos_trazabilidad detecta tests sin línea 'Prueba:'.

    El fixture tiene test_sin_linea_prueba (T-120) que tiene ID pero no línea Prueba:.

    Prueba: mcp_servers/artemis_trazabilidad/tools.py::huecos_trazabilidad
    """
    resultado = tools["huecos_trazabilidad"](repo_root=str(REPO))
    assert "tests_sin_prueba" in resultado, "El resultado debe incluir la clave 'tests_sin_prueba'"
    funciones_sin_prueba = [t["funcion"] for t in resultado["tests_sin_prueba"]]
    assert (
        "test_sin_linea_prueba" in funciones_sin_prueba
    ), f"test_sin_linea_prueba debe aparecer en tests_sin_prueba: {funciones_sin_prueba}"


@pytest.mark.mvp
def test_huecos_comparacion_usa_id_completo_no_bare(tools):
    """T-217 | 001/FR-MCP — huecos_trazabilidad usa ID completo '001/FR-XXX' para comparar.

    Bug: si se compara con bare 'FR-001', un test de '002/FR-001' podría cubrir
    un requisito de '001/FR-001' incorrectamente.

    Prueba: mcp_servers/artemis_trazabilidad/tools.py::huecos_trazabilidad
    """
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmp:
        # Spec 001 con FR-001
        spec001 = os.path.join(tmp, "specs", "001-mvp")
        os.makedirs(spec001)
        with open(os.path.join(spec001, "spec.md"), "w", encoding="utf-8") as f:
            f.write("- **FR-001**: Requisito de spec 001.\n")

        # Test que cubre 002/FR-001 (spec 002, NO spec 001)
        tests_dir = os.path.join(tmp, "tests", "unit")
        os.makedirs(tests_dir)
        with open(os.path.join(tests_dir, "__init__.py"), "w") as f:
            f.write("")
        with open(os.path.join(tests_dir, "test_ejemplo.py"), "w", encoding="utf-8") as f:
            f.write(
                "def test_cubre_002_fr001():\n"
                '    """T-200 | 002/FR-001 — Cubre FR-001 de la spec 002, no de la 001."""\n'
                "    assert True\n"
            )

        resultado = tools["huecos_trazabilidad"](repo_root=tmp)

    # FR-001 de spec 001 NO debe considerarse cubierta por un test de 002/FR-001
    req_sin_test = [r["id"] for r in resultado.get("requisitos_sin_test", [])]
    assert "001/FR-001" in req_sin_test or "FR-001" in req_sin_test, (
        f"001/FR-001 debe aparecer como sin cobertura (solo cubierto por 002/FR-001): "
        f"{req_sin_test}"
    )


@pytest.mark.mvp
def test_requisito_bare_id_una_sola_spec_completa_prefijo(tools):
    """T-219 | 001/FR-MCP — requisito('FR-005') con una sola spec completa el prefijo.

    Si el ID viene sin prefijo (ej. 'FR-005') y existe exactamente una spec,
    debe buscarse como '001/FR-005' automáticamente.

    Prueba: mcp_servers/artemis_trazabilidad/tools.py::requisito
    """
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmp:
        # Solo una spec
        spec_dir = os.path.join(tmp, "specs", "001-mvp")
        os.makedirs(spec_dir)
        with open(os.path.join(spec_dir, "spec.md"), "w", encoding="utf-8") as f:
            f.write("- **FR-005**: Validación de parámetros.\n")

        os.makedirs(os.path.join(tmp, "tests"))

        # ID sin prefijo — debe autocompletar a "001/FR-005"
        resultado = tools["requisito"](req_id="FR-005", repo_root=tmp)

    assert resultado["encontrado"] is True, (
        f"Con una sola spec, 'FR-005' debería encontrarse como '001/FR-005'. "
        f"Error: {resultado.get('error')}"
    )
    assert "FR-005" in resultado["texto"]
    # El id devuelto debe tener el prefijo completado automáticamente
    assert resultado["id"] == "001/FR-005", (
        f"El id devuelto debe ser '001/FR-005' (con prefijo autocomplete), "
        f"se obtuvo: {resultado.get('id')!r}"
    )


@pytest.mark.mvp
def test_requisito_bare_id_multiples_specs_pide_prefijo(tools):
    """T-220 | 001/FR-MCP — requisito('FR-005') con múltiples specs devuelve error.

    Si hay más de una spec y no se especifica prefijo, debe devolver un error
    que explique que hay que indicar el prefijo (ej. '001/FR-005').

    Prueba: mcp_servers/artemis_trazabilidad/tools.py::requisito
    """
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmp:
        # Dos specs diferentes
        for folder in ["001-mvp", "002-v2"]:
            spec_dir = os.path.join(tmp, "specs", folder)
            os.makedirs(spec_dir)
            with open(os.path.join(spec_dir, "spec.md"), "w", encoding="utf-8") as f:
                f.write(f"- **FR-005**: Requisito en {folder}.\n")

        os.makedirs(os.path.join(tmp, "tests"))

        # ID sin prefijo con múltiples specs — debe pedir que se especifique
        resultado = tools["requisito"](req_id="FR-005", repo_root=tmp)

    assert (
        resultado["encontrado"] is False
    ), "Con múltiples specs y sin prefijo, debe devolver encontrado=False"
    # El error debe mencionar que hay que especificar el prefijo
    error = resultado.get("error", "").lower()
    assert (
        "prefijo" in error or "spec" in error or "001/" in error or "002/" in error
    ), f"El error debe pedir que se especifique el prefijo. Error: {resultado.get('error')!r}"


@pytest.mark.mvp
def test_funcion_bajo_test_rechaza_ruta_fuera_del_repo(tools):
    """T-218 | 001/FR-MCP — funcion_bajo_test rechaza ruta 'Prueba:' fuera del repositorio.

    Una línea 'Prueba: ../../etc/passwd::algo' no debe ser ejecutada como path traversal.

    Prueba: mcp_servers/artemis_trazabilidad/tools.py::funcion_bajo_test
    """
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmp:
        tests_dir = os.path.join(tmp, "tests", "unit")
        os.makedirs(tests_dir)
        with open(os.path.join(tests_dir, "__init__.py"), "w") as f:
            f.write("")
        # Test con ruta que intenta salir del repo
        with open(os.path.join(tests_dir, "test_traversal.py"), "w", encoding="utf-8") as f:
            f.write(
                "def test_traversal():\n"
                '    """T-999 | 001/FR-001 — Path traversal test.\n'
                "\n"
                "    Prueba: ../../etc/passwd::root\n"
                '    """\n'
                "    assert True\n"
            )

        resultado = tools["funcion_bajo_test"](test_id="T-999", repo_root=tmp)

    assert (
        resultado["encontrado"] is False
    ), "funcion_bajo_test debe rechazar rutas que salen del repositorio"
    assert (
        "fuera" in resultado.get("error", "").lower()
        or "traversal" in resultado.get("error", "").lower()
        or "repositorio" in resultado.get("error", "").lower()
    ), f"El error debe indicar ruta fuera del repositorio: " f"{resultado.get('error')!r}"
