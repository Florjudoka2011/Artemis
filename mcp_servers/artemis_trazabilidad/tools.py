"""
Lógica pura de las herramientas del MCP artemis-trazabilidad.

Solo lectura: no modifica ni importa src/.
Recibe repo_root como parámetro para facilitar tests con fixtures.
Todas las rutas devueltas son relativas a repo_root.
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


def _rel(path: pathlib.Path, root: pathlib.Path) -> str:
    """Devuelve la ruta relativa a root, siempre con separadores /."""
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


# Directorios excluidos del recorrido de tests (rutas relativas a repo_root)
_DEFAULT_EXCLUDE_DIRS: frozenset[str] = frozenset(["tests/fixtures"])


def _iter_py_files(
    base: pathlib.Path,
    root: pathlib.Path | None = None,
    exclude_dirs: frozenset[str] | None = None,
) -> list[pathlib.Path]:
    """Itera archivos .py bajo base, excluyendo directorios configurados.

    exclude_dirs: rutas relativas a root que se omiten.
    Por defecto excluye tests/fixtures/ para evitar contaminación de fixtures.
    """
    if exclude_dirs is None:
        exclude_dirs = _DEFAULT_EXCLUDE_DIRS
    result = []
    for py in sorted(base.rglob("*.py")):
        if root is not None and exclude_dirs:
            try:
                rel = py.relative_to(root).as_posix()
                if any(rel == excl or rel.startswith(excl + "/") for excl in exclude_dirs):
                    continue
            except ValueError:
                pass
        result.append(py)
    return result


# Patrón: "T-XXX | 001/FR-XXX" en primera línea del docstring
_TRACE_RE = re.compile(r"(T-[\w-]+)\s*\|\s*([\w/]*/FR-[\w-]+)")

# Patrón línea "Prueba: ruta/archivo.py::NombreClaseOFuncion"
_PRUEBA_RE = re.compile(r"^\s*Prueba:\s*(.+?)::(\w+)\s*$", re.MULTILINE)

# Patrón para requisitos en formato Spec Kit: "- **FR-XXX**: texto"
_FR_SPECKIT_RE = re.compile(r"^-\s+\*\*FR-([\w-]+)\*\*:\s+(.*)")

# Patrón para nombre de archivo de evidencia con fecha: AAAA-MM-DD_HHMM_tipo.txt
_FECHA_RE = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{4}_.*\.txt$")


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

    for py in _iter_py_files(tests_dir, root=root):
        for t in _parse_tests(py):
            if t["test_id"] == test_id:
                return {
                    "encontrado": True,
                    "archivo": _rel(py, root),
                    "linea": t["linea"],
                    "funcion": t["funcion"],
                    "requisito": t["requisito"],
                    "docstring": t["docstring"],
                }

    return {"encontrado": False, "error": f"No se encontró ningún test con ID {test_id!r}"}


# ─── herramienta 2: funcion_bajo_test ────────────────────────────────────────


def _extract_node_source(path: pathlib.Path, name: str) -> dict[str, Any] | None:
    """Extrae el código fuente de una función o clase de un archivo .py."""
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
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name == name:
                end = node.end_lineno or node.lineno
                snippet = "\n".join(lines[node.lineno - 1 : end])
                return {
                    "funcion_nombre": name,
                    "linea": node.lineno,
                    "codigo": snippet,
                }
    return None


def funcion_bajo_test(test_id: str, repo_root: str | None = None) -> dict[str, Any]:
    """Devuelve el código de la función/clase bajo test.

    Usa la línea "Prueba: ruta/archivo.py::NombreClaseOFuncion" del docstring del test.
    Si el test no tiene esa línea, devuelve encontrado=False con error="no determinable".
    Soporta funciones y clases.
    Rechaza rutas que salen del repositorio (path traversal).
    """
    result = buscar_test(test_id, repo_root)
    if not result["encontrado"]:
        return result

    root = _find_repo_root(repo_root)
    docstring = result.get("docstring", "")

    m = _PRUEBA_RE.search(docstring)
    if not m:
        return {
            "encontrado": False,
            "error": "no determinable — el test no tiene línea 'Prueba: archivo::nombre'",
        }

    rel_path = m.group(1).strip()
    target_name = m.group(2).strip()
    candidate = (root / rel_path).resolve()

    # Validar que la ruta resuelta quede dentro del repositorio
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return {
            "encontrado": False,
            "error": (
                f"Ruta fuera del repositorio: {rel_path!r} resuelve a "
                f"{candidate} (raíz: {root})"
            ),
        }

    if not candidate.exists():
        return {
            "encontrado": False,
            "error": f"Archivo no encontrado: {rel_path!r} (desde raíz {root})",
        }

    found = _extract_node_source(candidate, target_name)
    if not found:
        return {
            "encontrado": False,
            "error": f"No se encontró '{target_name}' en {rel_path!r}",
        }

    return {
        "encontrado": True,
        "archivo": _rel(candidate, root),
        **found,
    }


# ─── herramienta 3: requisito ─────────────────────────────────────────────────


def _spec_prefix_from_req_id(req_id: str) -> str | None:
    """Extrae el prefijo de la spec de un req_id del estilo '001/FR-005'.

    Devuelve '001' o None si el formato no tiene prefijo.
    """
    parts = req_id.split("/")
    if len(parts) == 2:
        return parts[0]
    return None


def _bare_fr(req_id: str) -> str:
    """Extrae el ID bare 'FR-XXX' de '001/FR-XXX' o 'FR-XXX'."""
    parts = req_id.split("/")
    return parts[-1]


def requisito(req_id: str, repo_root: str | None = None) -> dict[str, Any]:
    """Devuelve el texto del requisito en specs/ y los tests que lo cubren.

    Acepta 'NNN/FR-XXX' (busca solo en la spec NNN) o 'FR-XXX':
      - Si hay una sola spec, autocompleta el prefijo (ej. '001/FR-005').
      - Si hay múltiples specs, devuelve error pidiendo especificar el prefijo.
    Coincidencia exacta: 'FR-005' no coincide con 'FR-0050'.
    Detecta el formato Spec Kit: '- **FR-XXX**: texto'.
    """
    root = _find_repo_root(repo_root)
    specs_dir = root / "specs"
    if not specs_dir.exists():
        return {"encontrado": False, "error": f"specs/ no encontrado en {root}"}

    spec_prefix = _spec_prefix_from_req_id(req_id)
    bare = _bare_fr(req_id)

    # Sin prefijo: autocompletar si hay una sola spec, error si hay más de una
    if not spec_prefix:
        all_specs = sorted(specs_dir.rglob("spec.md"))
        if len(all_specs) == 1:
            # Extraer prefijo de la única spec y reescribir req_id
            folder = all_specs[0].relative_to(specs_dir).parts[0]
            spec_prefix = folder.split("-")[0] if "-" in folder else folder
            req_id = f"{spec_prefix}/{bare}"
        elif len(all_specs) > 1:
            spec_names = [s.relative_to(specs_dir).parts[0] for s in all_specs]
            examples = "/".join([f"{n.split('-')[0]}/{bare}" for n in spec_names[:2]])
            return {
                "encontrado": False,
                "error": (
                    f"Hay {len(all_specs)} specs ({', '.join(spec_names)}). "
                    f"Especificá el prefijo, ej: '{examples.split('/')[0]}/{bare}'"
                ),
            }

    texto = None
    archivo_req = None
    linea_req = None

    for md in sorted(specs_dir.rglob("spec.md")):
        # Filtrar por spec: la carpeta debe EMPEZAR con "NNN-", no solo CONTENER "NNN"
        if spec_prefix:
            rel = md.relative_to(specs_dir).parts
            if not any(part == spec_prefix or part.startswith(spec_prefix + "-") for part in rel):
                continue

        lines = md.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines, 1):
            # Formato Spec Kit: "- **FR-XXX**: texto"
            m_sk = _FR_SPECKIT_RE.match(line)
            if m_sk:
                fr_id = "FR-" + m_sk.group(1)
                if fr_id == bare:
                    texto = line.strip()
                    archivo_req = _rel(md, root)
                    linea_req = i
                    break
            # Formato legacy: SOLO títulos "### FR-XXX" (no cualquier línea que contenga el ID)
            elif re.match(r"###\s+" + re.escape(bare) + r"(?:$|[:\s])", line):
                block = [line]
                for j in range(i, min(i + 15, len(lines))):
                    if lines[j].startswith("###") and j != i - 1:
                        break
                    block.append(lines[j])
                texto = "\n".join(block).strip()
                archivo_req = _rel(md, root)
                linea_req = i
                break
        if texto:
            break

    if not texto:
        return {"encontrado": False, "error": f"No se encontró el requisito {req_id!r} en specs/"}

    # Buscar tests que cubren este requisito (comparación exacta del ID completo)
    tests_dir = root / "tests"
    tests_cubriendo = []
    if tests_dir.exists():
        for py in _iter_py_files(tests_dir, root=root):
            for t in _parse_tests(py):
                if t["requisito"] and t["requisito"] == req_id:
                    tests_cubriendo.append(
                        {
                            "id": t["test_id"],
                            "funcion": t["funcion"],
                            "archivo": _rel(py, root),
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

_CRITERIO = (
    "[X] = hecha; [ ] = pendiente. "
    "No hay estado 'bloqueada' automático: el título de sección no afecta "
    "la clasificación de las tareas. Solo [X] y [ ] son estados válidos."
)


def _parse_tasks(tasks_path: pathlib.Path) -> dict[str, list[dict[str, Any]]]:
    """Parsea tasks.md y clasifica en hechas y pendientes.

    Criterio: [X] = hecha; [ ] = pendiente.
    El título de sección (BLOQUEANTE, etc.) NO cambia el estado de las tareas.
    """
    try:
        lines = tasks_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return {"hechas": [], "pendientes": []}

    done_re = re.compile(r"^\s*-\s*\[X\]\s*(T[\w]+)\s+(.*)", re.IGNORECASE)
    todo_re = re.compile(r"^\s*-\s*\[\s\]\s*(T[\w]+)\s+(.*)")

    hechas: list[dict[str, Any]] = []
    pendientes: list[dict[str, Any]] = []

    for line in lines:
        m = done_re.match(line)
        if m:
            hechas.append({"id": m.group(1), "descripcion": m.group(2).strip()})
            continue
        m = todo_re.match(line)
        if m:
            pendientes.append({"id": m.group(1), "descripcion": m.group(2).strip()})

    return {"hechas": hechas, "pendientes": pendientes}


def estado_tareas(repo_root: str | None = None) -> dict[str, Any]:
    """Devuelve tareas de tasks.md agrupadas en hechas y pendientes.

    Criterio de clasificación: [X] = hecha; [ ] = pendiente.
    El título de sección (ej. 'BLOQUEANTE') NO afecta la clasificación.
    """
    root = _find_repo_root(repo_root)
    specs_dir = root / "specs"
    if not specs_dir.exists():
        return {
            "hechas": [],
            "pendientes": [],
            "criterio": _CRITERIO,
            "error": "specs/ no encontrado",
        }

    tasks_files = sorted(specs_dir.rglob("tasks.md"))
    if not tasks_files:
        return {
            "hechas": [],
            "pendientes": [],
            "criterio": _CRITERIO,
            "error": "No se encontró tasks.md",
        }

    hechas: list[dict] = []
    pendientes: list[dict] = []
    for tf in tasks_files:
        parsed = _parse_tasks(tf)
        hechas.extend(parsed["hechas"])
        pendientes.extend(parsed["pendientes"])

    return {
        "hechas": hechas,
        "pendientes": pendientes,
        "criterio": _CRITERIO,
    }


# ─── herramienta 5: ultima_evidencia ─────────────────────────────────────────


def ultima_evidencia(repo_root: str | None = None) -> dict[str, Any]:
    """Devuelve el contenido del archivo de evidencia más reciente.

    Solo considera archivos cuyo nombre tenga fecha: AAAA-MM-DD_HHMM_tipo.txt.
    Los ordena lexicográficamente (el formato garantiza orden cronológico).
    """
    root = _find_repo_root(repo_root)
    evidencia_dir = root / "docs" / "evidencia" / "fase1"
    if not evidencia_dir.exists():
        return {
            "encontrado": False,
            "error": f"docs/evidencia/fase1/ no encontrado en {root}",
        }

    # Solo archivos con fecha en el nombre
    txt_files = sorted(f for f in evidencia_dir.glob("*.txt") if _FECHA_RE.match(f.name))
    if not txt_files:
        return {
            "encontrado": False,
            "error": "No hay archivos de evidencia con fecha en docs/evidencia/fase1/",
        }

    ultimo = txt_files[-1]
    try:
        contenido = ultimo.read_text(encoding="utf-8")
    except OSError as e:
        return {"encontrado": False, "error": str(e)}

    return {
        "encontrado": True,
        "archivo": _rel(ultimo, root),
        "contenido": contenido,
    }


# ─── herramienta 6: huecos_trazabilidad ──────────────────────────────────────


def huecos_trazabilidad(repo_root: str | None = None) -> dict[str, Any]:
    """Detecta huecos de trazabilidad en el repositorio.

    - tests_sin_requisito: tests que no tienen ID de trazabilidad en su docstring.
    - tests_sin_prueba: tests con ID pero sin línea 'Prueba: archivo::nombre'.
    - ids_duplicados: T-IDs que aparecen en más de un test.
    - requisitos_sin_test: requisitos en spec.md que ningún test cubre.
    - tareas_sin_evidencia: control global (no por tarea).
    """
    root = _find_repo_root(repo_root)

    # 1. Recopilar todos los tests
    tests_dir = root / "tests"
    todos_los_tests: list[dict] = []
    tests_sin_requisito: list[dict] = []
    tests_sin_prueba: list[dict] = []
    if tests_dir.exists():
        for py in _iter_py_files(tests_dir, root=root):
            for t in _parse_tests(py):
                todos_los_tests.append(t)
                if not t["test_id"]:
                    tests_sin_requisito.append(
                        {
                            "funcion": t["funcion"],
                            "archivo": _rel(py, root),
                            "linea": t["linea"],
                        }
                    )
                else:
                    # Tiene ID pero ¿tiene línea Prueba:?
                    if not _PRUEBA_RE.search(t["docstring"]):
                        tests_sin_prueba.append(
                            {
                                "funcion": t["funcion"],
                                "test_id": t["test_id"],
                                "archivo": _rel(py, root),
                                "linea": t["linea"],
                            }
                        )

    # IDs duplicados: T-IDs que aparecen más de una vez
    from collections import Counter

    conteo_ids: Counter = Counter(t["test_id"] for t in todos_los_tests if t["test_id"])
    ids_duplicados = [tid for tid, cnt in conteo_ids.items() if cnt > 1]

    # IDs cubiertos: usar el ID completo con prefijo de spec (001/FR-XXX)
    ids_cubiertos: set[str] = set()
    for t in todos_los_tests:
        if t["requisito"]:
            ids_cubiertos.add(t["requisito"])

    # 2. Recopilar requisitos en specs/ — con ID completo "NNN/FR-XXX"
    specs_dir = root / "specs"
    todos_los_requisitos: list[dict] = []
    if specs_dir.exists():
        for md in sorted(specs_dir.rglob("spec.md")):
            # Extraer prefijo de spec de la carpeta: "NNN-nombre" → "NNN"
            spec_folder = (
                md.relative_to(specs_dir).parts[0] if md.relative_to(specs_dir).parts else ""
            )
            spec_num = spec_folder.split("-")[0] if "-" in spec_folder else spec_folder

            lines = md.read_text(encoding="utf-8").splitlines()
            for i, line in enumerate(lines, 1):
                m = _FR_SPECKIT_RE.match(line)
                if m:
                    bare_fr = "FR-" + m.group(1)
                    full_id = f"{spec_num}/{bare_fr}" if spec_num else bare_fr
                    todos_los_requisitos.append(
                        {
                            "id": full_id,
                            "titulo": m.group(2).strip(),
                            "archivo": _rel(md, root),
                            "linea": i,
                        }
                    )
                else:
                    # Formato legacy: ### FR-XXX: título (solo títulos exactos)
                    m2 = re.match(r"###\s+(FR-[\w-]+)(?::\s+(.*))?", line)
                    if m2:
                        bare_fr = m2.group(1)
                        full_id = f"{spec_num}/{bare_fr}" if spec_num else bare_fr
                        todos_los_requisitos.append(
                            {
                                "id": full_id,
                                "titulo": (m2.group(2) or "").strip(),
                                "archivo": _rel(md, root),
                                "linea": i,
                            }
                        )

    requisitos_sin_test = [r for r in todos_los_requisitos if r["id"] not in ids_cubiertos]

    # 3. Control global: ¿hay evidencia de ejecución?
    evidencia_dir = root / "docs" / "evidencia" / "fase1"
    archivos_con_fecha = list(evidencia_dir.glob("*.txt")) if evidencia_dir.exists() else []
    archivos_con_fecha = [f for f in archivos_con_fecha if _FECHA_RE.match(f.name)]
    hay_evidencia = bool(archivos_con_fecha)

    nota = (
        "Control global: indica si NO hay ningún archivo de evidencia con fecha "
        "en docs/evidencia/fase1/. No es un control por tarea individual."
    )
    tareas_sin_evidencia: list[dict] = [] if hay_evidencia else estado_tareas(repo_root)["hechas"]

    return {
        "tests_sin_requisito": tests_sin_requisito,
        "tests_sin_prueba": tests_sin_prueba,
        "ids_duplicados": ids_duplicados,
        "requisitos_sin_test": requisitos_sin_test,
        "tareas_sin_evidencia": tareas_sin_evidencia,
        "nota_tareas_sin_evidencia": nota,
        "resumen": {
            "total_tests": len(todos_los_tests),
            "sin_requisito": len(tests_sin_requisito),
            "sin_prueba": len(tests_sin_prueba),
            "ids_duplicados": len(ids_duplicados),
            "total_requisitos": len(todos_los_requisitos),
            "sin_test": len(requisitos_sin_test),
        },
    }
