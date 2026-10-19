"""
Genera evidencia verificable de la suite completa del MVP de Artemis.

Ejecuta en orden:
  1. pytest -v con --junitxml
  2. cobertura con --cov-report=term-missing
  3. scripts/mutacion_manual.py
  4. scripts/gen_traceability.py

Cada salida se guarda en docs/evidencia/fase1/ con fecha y hora en el nombre:
  AAAA-MM-DD_HHMM_pytest.txt
  AAAA-MM-DD_HHMM_cobertura.txt
  AAAA-MM-DD_HHMM_mutacion.txt
  AAAA-MM-DD_HHMM_trazabilidad.txt

El script usa el Python del entorno virtual del proyecto (.venv).
Sale con código 1 si alguna etapa falla.

Uso:
    cd D:\\Proyecto
    .venv\\Scripts\\python.exe scripts/evidencia.py
"""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
EVIDENCIA_DIR = ROOT / "docs" / "evidencia" / "fase1"
PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"

EVIDENCIA_DIR.mkdir(parents=True, exist_ok=True)


def ts() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H%M")


def run(label: str, cmd: list[str], *, cwd: Path = ROOT) -> int:
    stamp = ts()
    out_path = EVIDENCIA_DIR / f"{stamp}_{label}.txt"
    print(f"\n{'='*60}")
    print(f"[{label}] ejecutando...")
    print(f"  Salida: {out_path}")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(cwd),
        encoding="utf-8",
    )
    combined = result.stdout
    if result.stderr:
        combined += "\n--- stderr ---\n" + result.stderr

    out_path.write_text(combined, encoding="utf-8")
    print(combined[-2000:] if len(combined) > 2000 else combined)

    status = "OK" if result.returncode == 0 else f"FALLO (codigo {result.returncode})"
    print(f"[{label}] {status}")
    return result.returncode


def main() -> None:
    failures: list[str] = []

    # 1. pytest -v con JUnit XML
    junit_path = EVIDENCIA_DIR / f"{ts()}_junit.xml"
    rc = run(
        "pytest",
        [
            str(PYTHON),
            "-m",
            "pytest",
            "-m",
            "mvp",
            "-v",
            "--tb=short",
            f"--junitxml={junit_path}",
        ],
    )
    if rc != 0:
        failures.append("pytest")

    # 2. Cobertura
    rc = run(
        "cobertura",
        [
            str(PYTHON),
            "-m",
            "pytest",
            "-m",
            "mvp",
            "--tb=no",
            "-q",
            "--cov=src",
            "--cov-report=term-missing",
            "--cov-fail-under=90",
        ],
    )
    if rc != 0:
        failures.append("cobertura")

    # 3. Mutación manual
    rc = run(
        "mutacion",
        [str(PYTHON), "scripts/mutacion_manual.py"],
    )
    if rc != 0:
        failures.append("mutacion")

    # 4. Trazabilidad
    rc = run(
        "trazabilidad",
        [str(PYTHON), "scripts/gen_traceability.py"],
    )
    if rc != 0:
        failures.append("trazabilidad")

    print(f"\n{'='*60}")
    if failures:
        print(f"FALLOS: {', '.join(failures)}")
        sys.exit(1)
    else:
        print("Todas las etapas OK.")
        print(f"Evidencia guardada en: {EVIDENCIA_DIR}")


if __name__ == "__main__":
    main()
