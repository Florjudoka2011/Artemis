"""
Validación mutante manual para src/schemas/figuras.py.

Aplica cada mutante de forma secuencial, corre los tests de schemas
y verifica que los tests FALLEN (el mutante muere). Restaura el
archivo original después de cada mutante.

Uso:
    cd D:\\Proyecto
    .venv\\Scripts\\python.exe scripts/mutacion_manual.py

Salida: imprime "MURIO [OK]" o "SOBREVIVIO [FALLO]" por cada mutante
y termina con código 1 si algún mutante sobrevive.

Los 4 mutantes cubren:
  M1: v <= 0  →  v < 0   (permitiría cero — T-105 debe matar)
  M2: isfinite elimiado  →  siempre True  (T-104 en AgujeroParams debe matar)
  M3: extra='forbid' → 'ignore'  (T-106 debe matar)
  M4: diametro <= 0  →  diametro < 0  (T-105 en AgujeroParams debe matar)
"""

import subprocess
import sys
from pathlib import Path

SCHEMA = Path(__file__).parent.parent / "src" / "schemas" / "figuras.py"
PROJECT_ROOT = Path(__file__).parent.parent
PYTHON = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"

original = SCHEMA.read_text(encoding="utf-8")

MUTANTS = [
    (
        "M1: v <= 0  ->  v < 0  en PrismaRectangularParams/CilindroParams (permitiria cero)",
        'if v <= 0:\n            raise ValueError("las dimensiones deben ser > 0")',
        'if v < 0:\n            raise ValueError("las dimensiones deben ser > 0")',
    ),
    (
        "M2: math.isfinite(v)  ->  True  en AgujeroParams (siempre finito, T-104 debe matar)",
        (
            "if not math.isfinite(v):\n"
            '            raise ValueError("diametro debe ser un número finito")'
        ),
        (
            "if False:  # mutante: elimina chequeo isfinite en AgujeroParams\n"
            '            raise ValueError("diametro debe ser un número finito")'
        ),
    ),
    (
        "M3: extra='forbid'  ->  extra='ignore'  (T-106 debe matar)",
        'model_config = ConfigDict(extra="forbid")',
        'model_config = ConfigDict(extra="ignore")',
    ),
    (
        "M4: diametro <= 0  ->  diametro < 0  en AgujeroParams (permitiria cero)",
        'if v <= 0:\n            raise ValueError("diametro debe ser > 0")',
        'if v < 0:\n            raise ValueError("diametro debe ser > 0")',
    ),
]

results = []
for name, old, new in MUTANTS:
    mutated = original.replace(old, new, 1)
    if mutated == original:
        print(f"[ADVERTENCIA] Mutante no aplicado (patron no encontrado): {name}")
        results.append((name, "NO_APLICADO [ERROR]", ""))
        continue

    SCHEMA.write_text(mutated, encoding="utf-8")
    r = subprocess.run(
        [
            str(PYTHON),
            "-m",
            "pytest",
            "tests/unit/test_schemas.py",
            "-x",
            "-q",
            "--no-header",
            "--tb=no",
        ],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
        encoding="utf-8",
    )
    passed = r.returncode == 0
    last_line = (r.stdout.strip().splitlines() or [""])[-1]
    status = "SOBREVIVIO [FALLO]" if passed else "MURIO  [OK]"
    results.append((name, status, last_line))
    SCHEMA.write_text(original, encoding="utf-8")  # restaurar siempre

print("\n=== Resultados de validacion mutante ===\n")
for name, status, summary in results:
    print(f"  {status}  {name}")
    if summary:
        print(f"           {summary}\n")

survived = sum(1 for _, s, _ in results if "SOBREVIVIO" in s)
print(f"Supervivientes: {survived}/{len(MUTANTS)}")
if survived:
    sys.exit(1)
