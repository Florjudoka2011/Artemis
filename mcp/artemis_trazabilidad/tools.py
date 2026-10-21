"""
Lógica pura de las herramientas del MCP artemis-trazabilidad.

Solo lectura: no modifica ni importa src/.
Recibe repo_root como parámetro para facilitar tests con fixtures.
"""

from __future__ import annotations

import ast
import pathlib
import re
from typing import Any


# ─── helpers ──────────────────────────────────────────────────────────────────


def _find_repo_root(repo_root: str | None) -> pathlib.Path:
    if repo_root:
        return pathlib.Path(repo_root)
    return pathlib.Path(__file__).parent.parent.parent


def _iter_py_files(base: pathlib.Path) -> list[pathlib.Path]:
    return sorted(base.rglob("*.py"))


# Patrón: "T-XXX | 001/FR-XXX" en primera línea del docstring
_TRACE_RE = re.compile(r"(T-[\w-]+)\s*\|\s*([\w/]*/FR-[\w-]+)")


def _parse_tests(path: pathlib.Path) -> list[dict[str, Any]]:
    """Extrae metadatos de cada función de test con ID de trazabilidad."""
    try:
        source = path.read_text(encoding="utf-8")
    except OSError:
        return []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    results = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        if not node.name.startswith("test_"):
            continue
        docstring = ast.get_docstring(node) or ""
        first_line = docstring.split("\n")[0].strip()
        m = _TRACE_RE.search(first_line)
        results.append(
            {
                "funcion": node.name,
                "linea": node.lineno,
                "archivo": str(path),
                "docstring": docstring,
                "test_id": m.group(1) if m else None,
                "requisito": m.group(2) if m else None,
            }
        )
    return results


# ─── herramienta 1: buscar_test ───────────────────────────────────────────────


def buscar_test(test_id: str, repo_root: str | None = None) -> dict[str, Any]:
    """Localiza un test por su ID (T-XXX) en el repositorio."""
    root = _find_repo_root(repo_root)
    tests_dir = root / "tests"
    if not tests_dir.exists():
        return {"encontrado": False, "error": f"Directorio tests/ no encontrado en {root}"}

    for py in _iter_py_files(tests_dir):
        for t in _parse_tests(py):
            if t["test_id"] == test_id:
                return {
                    "encontrado": True,
                    "archivo": str(py),
                    "linea": t["linea"],
                    "funcion": t["funcion"],
                    "requisito": t["requisito"],
                    "docstring": t["docstring"],
                }

    return {"encontrado": False, "error": f"No se encontró ningún test con ID {test_id!r}"}


# ─── herramienta 2: funcion_bajo_test ────────────────────────────────────────


def _extract_function_source(path: pathlib.Path, func_name: str) -> dict[str, Any] | None:
    """Extrae el código fuente de una función de un archivo .py."""
    try:
        source = path.read_text(encoding="utf-8")
    except OSError:
        return None
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None

    lines = source.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            end = node.end_lineno or node.lineno
            snippet = "\n".join(lines[node.lineno - 1 : end])
            return {
                "funcion_nombre": func_name,
                "linea": node.lineno,
                "codigo": snippet,
            }
    return None


def funcion_bajo_test(test_id: str, repo_root: str | None = None) -> dict[str, Any]:
    """Devuelve el código real de la función probada por el test dado."""
    result = buscar_test(test_id, repo_root)
    if not result["encontrado"]:
        return result

    root = _find_repo_root(repo_root)
    test_file = pathlib.Path(result["archivo"])
    try:
        source = test_file.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (OSError, SyntaxError):
        return {"encontrado": False, "error": "No se pudo leer el archivo de tests"}

    # Buscar la función bajo test: importaciones en el archivo de test
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            module_path = node.module.replace(".", "/")
            candidate = root / (module_path + ".py")
            if candidate.exists():
                for alias in node.names:
                    found = _extract_function_source(candidate, alias.name)
                    if found:
                        return {
                            "encontrado": True,
                            "archivo": str(candidate),
                            **found,
                        }

    # Fallback: buscar en src/ por el nombre del test (heurística)
    src_dir = root / "src"
    if src_dir.exists():
        func_hint = result["funcion"].replace("test_", "").split("_")[0]
        for py in _iter_py_files(src_dir):
            found = _extract_function_source(py, func_hint)
            if found:
                return {"encontrado": True, "archivo": str(py), **found}
            # También busca validators que contienen el nombre del test
            try:
                tree2 = ast.parse(py.read_text(encoding="utf-8"))
                for n in ast.walk(tree2):
                    if isinstance(n, ast.FunctionDef):
                        for child in ast.walk(n):
                            if isinstance(child, ast.FunctionDef) and (
                                child.name in result["funcion"]
                                or any(
                                    kw in child.name for kw in ["positivos", "finito", "validator"]
                                )
                            ):
                                src = _extract_function_source(py, child.name)
                                if src:
                                    return {"encontrado": True, "archivo": str(py), **src}
            except (OSError, SyntaxError):
                continue

    return {"encontrado": False, "error": f"No se encontró la función bajo test para {test_id!r}"}


# ─── herramienta 3: requisito ─────────────────────────────────────────────────


def requisito(req_id: str, repo_root: str | None = None) -> dict[str, Any]:
    """Devuelve el texto del requisito en specs/ y los tests que lo cubren."""
    root = _find_repo_root(repo_root)
    specs_dir = root / "specs"
    if not specs_dir.exists():
        return {"encontrado": False, "error": f"specs/ no encontrado en {root}"}

    # Buscar el requisito en archivos spec.md
    texto = None
    archivo_req = None
    linea_req = None
    # También acepta "FR-005: Texto" o "FR-005" directo
    frid_re = re.compile(re.escape(req_id), re.IGNORECASE)

    for md in sorted(specs_dir.rglob("spec.md")):
        lines = md.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines, 1):
            if frid_re.search(line):
                # Extrae párrafo completo a partir de aquí
                block = [line]
                for j in range(i, min(i + 15, len(lines))):
                    if lines[j].startswith("###") and j != i - 1:
                        break
                    block.append(lines[j])
                texto = "\n".join(block).strip()
                archivo_req = str(md)
                linea_req = i
                break
        if texto:
            break

    if not texto:
        return {"encontrado": False, "error": f"No se encontró el requisito {req_id!r} en specs/"}

    # Buscar tests que cubren este requisito
    tests_dir = root / "tests"
    tests_cubriendo = []
    if tests_dir.exists():
        for py in _iter_py_files(tests_dir):
            for t in _parse_tests(py):
                if t["requisito"] and req_id in t["requisito"]:
                    tests_cubriendo.append(
                        {
                            "id": t["test_id"],
                            "funcion": t["funcion"],
                            "archivo": str(py),
                            "linea": t["linea"],
                        }
                    )

    return {
        "encontrado": True,
        "id": req_id,
        "texto": texto,
        "archivo": archivo_req,
        "linea": linea_req,
        "tests": tests_cubriendo,
    }


# ─── herramienta 4: estado_tareas ────────────────────────────────────────────


def _parse_tasks(tasks_path: pathlib.Path) -> dict[str, list[dict[str, Any]]]:
    """Parsea tasks.md y clasifica en hechas, pendientes y bloqueadas."""
    try:
        lines = tasks_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return {"hechas": [], "pendientes": [], "bloqueadas": []}

    done_re = re.compile(r"^\s*-\s*\[X\]\s*(T\w+)\s+(.*)", re.IGNORECASE)
    todo_re = re.compile(r"^\s*-\s*\[\s\]\s*(T\w+)\s+(.*)")
    blocked_section = False

    hechas: list[dict[str, Any]] = []
    pendientes: list[dict[str, Any]] = []
    bloqueadas: list[dict[str, Any]] = []

    for line in lines:
        if "BLOQUEANTE" in line.upper() or "BLOQUEA" in line.upper():
            blocked_section = True
        m = done_re.match(line)
        if m:
            hechas.append({"id": m.group(1), "descripcion": m.group(2).strip()})
            continue
        m = todo_re.match(line)
        if m:
            entry = {"id": m.group(1), "descripcion": m.group(2).strip()}
            if blocked_section:
                bloqueadas.append(entry)
            else:
                pendientes.append(entry)

    return {"hechas": hechas, "pendientes": pendientes, "bloqueadas": bloqueadas}


def estado_tareas(repo_root: str | None = None) -> dict[str, Any]:
    """Devuelve tareas de tasks.md agrupadas en hechas, pendientes y bloqueadas."""
    root = _find_repo_root(repo_root)
    specs_dir = root / "specs"
    if not specs_dir.exists():
        return {"hechas": [], "pendientes": [], "bloqueadas": [], "error": "specs/ no encontrado"}

    tasks_files = sorted(specs_dir.rglob("tasks.md"))
    if not tasks_files:
        return {
            "hechas": [],
            "pendientes": [],
            "bloqueadas": [],
            "error": "No se encontró tasks.md",
        }

    # Combina si hay varios specs (proyecto multi-spec)
    hechas: list[dict] = []
    pendientes: list[dict] = []
    bloqueadas: list[dict] = []
    for tf in tasks_files:
        parsed = _parse_tasks(tf)
        hechas.extend(parsed["hechas"])
        pendientes.extend(parsed["pendientes"])
        bloqueadas.extend(parsed["bloqueadas"])

    return {"hechas": hechas, "pendientes": pendientes, "bloqueadas": bloqueadas}


# ─── herramienta 5: ultima_evidencia ─────────────────────────────────────────


def ultima_evidencia(repo_root: str | None = None) -> dict[str, Any]:
    """Devuelve la salida de la ejecución más reciente en docs/evidencia/."""
    root = _find_repo_root(repo_root)
    evidencia_dir = root / "docs" / "evidencia" / "fase1"
    if not evidencia_dir.exists():
        return {
            "encontrado": False,
            "error": f"docs/evidencia/fase1/ no encontrado en {root}",
        }

    txt_files = sorted(evidencia_dir.glob("*.txt"))
    if not txt_files:
        return {
            "encontrado": False,
            "error": "No hay archivos de evidencia en docs/evidencia/fase1/",
        }

    # El más reciente por nombre (formato AAAA-MM-DD_HHMM_tipo.txt)
    ultimo = txt_files[-1]
    try:
        contenido = ultimo.read_text(encoding="utf-8")
    except OSError as e:
        return {"encontrado": False, "error": str(e)}

    return {
        "encontrado": True,
        "archivo": str(ultimo),
        "contenido": contenido,
    }


# ─── herramienta 6: huecos_trazabilidad ──────────────────────────────────────


def huecos_trazabilidad(repo_root: str | None = None) -> dict[str, Any]:
    """Detecta requisitos sin test, tests sin requisito y tareas hechas sin evidencia."""
    root = _find_repo_root(repo_root)

    # 1. Recopilar todos los tests
    tests_dir = root / "tests"
    todos_los_tests: list[dict] = []
    tests_sin_requisito: list[dict] = []
    if tests_dir.exists():
        for py in _iter_py_files(tests_dir):
            for t in _parse_tests(py):
                todos_los_tests.append(t)
                if not t["test_id"]:
                    tests_sin_requisito.append(
                        {
                            "funcion": t["funcion"],
                            "archivo": str(py),
                            "linea": t["linea"],
                        }
                    )

    ids_cubiertos = {t["requisito"] for t in todos_los_tests if t["requisito"]}

    # 2. Recopilar requisitos en specs/
    specs_dir = root / "specs"
    todos_los_requisitos: list[dict] = []
    req_re = re.compile(r"###\s+(FR-[\w-]+)(?::\s+(.*))?")
    if specs_dir.exists():
        for md in sorted(specs_dir.rglob("spec.md")):
            lines = md.read_text(encoding="utf-8").splitlines()
            for i, line in enumerate(lines, 1):
                m = req_re.match(line)
                if m:
                    todos_los_requisitos.append(
                        {
                            "id": m.group(1),
                            "titulo": (m.group(2) or "").strip(),
                            "archivo": str(md),
                            "linea": i,
                        }
                    )

    requisitos_sin_test = [r for r in todos_los_requisitos if r["id"] not in ids_cubiertos]

    # 3. Tareas marcadas [X] sin evidencia de ejecución de tests
    tareas = estado_tareas(repo_root)
    evidencia_dir = root / "docs" / "evidencia" / "fase1"
    hay_evidencia = evidencia_dir.exists() and bool(list(evidencia_dir.glob("*.txt")))
    tareas_sin_evidencia = tareas["hechas"] if not hay_evidencia else []

    return {
        "tests_sin_requisito": tests_sin_requisito,
        "requisitos_sin_test": requisitos_sin_test,
        "tareas_sin_evidencia": tareas_sin_evidencia,
        "resumen": {
            "total_tests": len(todos_los_tests),
            "sin_requisito": len(tests_sin_requisito),
            "total_requisitos": len(todos_los_requisitos),
            "sin_test": len(requisitos_sin_test),
        },
    }
