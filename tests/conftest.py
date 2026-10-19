"""
Fixtures compartidas para la suite de tests de Artemis.
"""

from pathlib import Path

import pytest


@pytest.fixture
def workspace_tmp(tmp_path: Path) -> Path:
    """
    Directorio temporal limpio para cada test de exportación.
    Se crea antes del test y se elimina automáticamente al finalizar.
    """
    ws = tmp_path / "workspace"
    ws.mkdir()
    return ws
