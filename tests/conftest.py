"""
Fixtures compartidas para la suite de tests de Artemis.
"""

import sys
from pathlib import Path

import pytest

# Hace que mcp/artemis_trazabilidad/ sea importable como `artemis_trazabilidad`
_MCP_DIR = Path(__file__).parent.parent / "mcp"
if str(_MCP_DIR) not in sys.path:
    sys.path.insert(0, str(_MCP_DIR))


@pytest.fixture
def workspace_tmp(tmp_path: Path) -> Path:
    """
    Directorio temporal limpio para cada test de exportación.
    Se crea antes del test y se elimina automáticamente al finalizar.
    """
    ws = tmp_path / "workspace"
    ws.mkdir()
    return ws
