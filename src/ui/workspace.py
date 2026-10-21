"""
Gestión del workspace: crea la subcarpeta de cada generación.
Formato: <figura>_<YYYYMMDD_HHMMSS>
"""

from datetime import datetime
from pathlib import Path

_WORKSPACE_BASE = Path("C:/Artemis/workspace")


def crear_workspace(base: Path | None = None, figura: str = "figura") -> Path:
    """Crea y devuelve el subdirectorio para una generación nueva."""
    base = Path(base) if base is not None else _WORKSPACE_BASE
    nombre = f"{figura}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    directorio = base / nombre
    directorio.mkdir(parents=True, exist_ok=True)
    return directorio
