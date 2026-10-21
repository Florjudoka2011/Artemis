"""
Exportación de sólidos CadQuery a STL y STEP.
Funciones puras: reciben sólido + ruta → escriben archivo → devuelven Path.
"""

from pathlib import Path

import cadquery as cq


def exportar_stl(solido: cq.Workplane, ruta: Path) -> Path:
    """Exporta el sólido a STL binario. Devuelve la ruta del archivo creado."""
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(solido, str(ruta), cq.exporters.ExportTypes.STL)
    return ruta


def exportar_step(solido: cq.Workplane, ruta: Path) -> Path:
    """Exporta el sólido a STEP. Devuelve la ruta del archivo creado."""
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(solido, str(ruta), cq.exporters.ExportTypes.STEP)
    return ruta
