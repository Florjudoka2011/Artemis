"""
Genera docs/trazabilidad.md leyendo los docstrings de tests/.

Busca el patrón:  T-XX | 001/FR-XX  (o T-XXX | 001/SC-XXX)
en la primera línea de cada docstring de función de test.

Uso:
    python scripts/gen_traceability.py
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
TESTS_DIR = ROOT / "tests"
OUTPUT = ROOT / "docs" / "trazabilidad.md"

# T-XX | 001/FR-XX  or  T-XX | 001/FR-XX | 001/FR-YY  etc.
PATTERN = re.compile(r"(T-\w+)\s*\|\s*((?:001/(?:FR|SC)-\w+)(?:\s*\|\s*001/(?:FR|SC)-\w+)*)")


def extract_entries(path: Path) -> list[dict]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    entries = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        if not node.name.startswith("test_"):
            continue
        docstring = ast.get_docstring(node) or ""
        first_line = docstring.strip().splitlines()[0] if docstring else ""
        m = PATTERN.search(first_line)
        if not m:
            continue
        test_id = m.group(1)
        feature_ids = [s.strip() for s in m.group(2).split("|")]
        rel = path.relative_to(ROOT)
        entries.append(
            {
                "test_id": test_id,
                "feature_ids": feature_ids,
                "file": str(rel).replace("\\", "/"),
                "function": node.name,
            }
        )
    return entries


def main() -> None:
    all_entries: list[dict] = []
    for test_file in sorted(TESTS_DIR.rglob("test_*.py")):
        all_entries.extend(extract_entries(test_file))

    if not all_entries:
        print("No se encontraron entradas con patrón T-XX | 001/FR-XX en tests/.")
        sys.exit(0)

    # Build output
    lines = [
        "# Matriz de Trazabilidad — Artemis MVP",
        "",
        "_Generado automáticamente por `scripts/gen_traceability.py`_",
        "",
        "| Test ID | Feature ID(s) | Archivo | Función |",
        "|---------|---------------|---------|---------|",
    ]
    seen_frs: set[str] = set()

    for e in sorted(all_entries, key=lambda x: x["test_id"]):
        fids = ", ".join(e["feature_ids"])
        seen_frs.update(e["feature_ids"])
        lines.append(f"| {e['test_id']} | {fids} | {e['file']} | `{e['function']}` |")

    lines += [
        "",
        f"**Total tests trazados**: {len(all_entries)}",
        f"**Feature IDs cubiertos**: {len(seen_frs)}",
        "",
    ]

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Trazabilidad generada: {OUTPUT}")
    print(f"  {len(all_entries)} tests trazados, {len(seen_frs)} feature IDs cubiertos")


if __name__ == "__main__":
    main()
