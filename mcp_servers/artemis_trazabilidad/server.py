"""
Servidor MCP artemis-trazabilidad.

Solo lectura: permite consultar el proyecto con evidencia verificable
(archivo y línea), sin depender de la memoria de la IA.

Ejecutar:
    python -m artemis_trazabilidad.server  (con PYTHONPATH=mcp_servers/)
    # o via .mcp.json (stdio transport)
"""

from __future__ import annotations

from mcp.server import MCPServer

from artemis_trazabilidad.tools import (
    buscar_test as _buscar_test,
    funcion_bajo_test as _funcion_bajo_test,
    requisito as _requisito,
    estado_tareas as _estado_tareas,
    ultima_evidencia as _ultima_evidencia,
    huecos_trazabilidad as _huecos_trazabilidad,
)

mcp = MCPServer("artemis-trazabilidad")


@mcp.tool()
def buscar_test(id: str) -> dict:
    """Localiza un test por su ID (ej: T-100).

    Devuelve archivo, línea, requisito (001/FR-XX), docstring completo
    y función que prueba.
    """
    return _buscar_test(test_id=id)


@mcp.tool()
def funcion_bajo_test(id: str) -> dict:
    """Devuelve el código real de la función probada por el test con ID dado.

    Incluye archivo y número de línea.
    """
    return _funcion_bajo_test(test_id=id)


@mcp.tool()
def requisito(id: str) -> dict:
    """Devuelve el texto del requisito en specs/ y la lista de tests que lo cubren.

    Ejemplo: requisito("FR-005")
    """
    return _requisito(req_id=id)


@mcp.tool()
def estado_tareas() -> dict:
    """Devuelve las tareas de tasks.md agrupadas en hechas, pendientes y bloqueadas."""
    return _estado_tareas()


@mcp.tool()
def ultima_evidencia() -> dict:
    """Devuelve la salida de la ejecución más reciente en docs/evidencia/."""
    return _ultima_evidencia()


@mcp.tool()
def huecos_trazabilidad() -> dict:
    """Detecta requisitos sin test, tests sin requisito y tareas hechas sin evidencia."""
    return _huecos_trazabilidad()


if __name__ == "__main__":
    mcp.run(transport="stdio")
