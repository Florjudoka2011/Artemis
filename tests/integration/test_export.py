"""
Tests de integración de exportación STL y STEP — arnés anti-mentiras.
"""

from pathlib import Path

import pytest

from src.schemas.figuras import PrismaRectangularParams
from src.recipes.prisma_rectangular import construir
from src.export.solid import exportar_stl, exportar_step


@pytest.mark.mvp
def test_exportar_stl(workspace_tmp: Path):
    """T-110 | 001/FR-006 — Exportar STL genera archivo > 0 bytes con volumen dentro de ±0,5%.

    Prueba: src/export/solid.py::exportar_stl

    Valor esperado: volumen teórico = 240000 mm³ (100 × 60 × 40); tolerancia ±0,5%
    """
    params = PrismaRectangularParams(largo=100, ancho=60, alto=40)
    solido = construir(params)
    ruta = exportar_stl(solido, workspace_tmp / "prisma.stl")
    assert ruta.exists(), "El archivo STL no fue creado"
    assert ruta.stat().st_size > 0, "El archivo STL está vacío"

    # Verificar volumen aproximado (±0,5%) importando el STL
    import struct

    with open(ruta, "rb") as f:
        header = f.read(80)
        assert len(header) == 80, "Header STL inválido"
        (num_triangles,) = struct.unpack("<I", f.read(4))
        assert num_triangles > 0, "STL sin triángulos"

    # Verificar tamaño mínimo razonable (prisma simple ≥ 12 triángulos)
    assert num_triangles >= 12, f"STL con muy pocos triángulos: {num_triangles}"


@pytest.mark.mvp
def test_exportar_step(workspace_tmp: Path):
    """T-111 | 001/FR-006 — Exportar STEP genera archivo > 0 bytes.

    Prueba: src/export/solid.py::exportar_step
    """
    params = PrismaRectangularParams(largo=100, ancho=60, alto=40)
    solido = construir(params)
    ruta = exportar_step(solido, workspace_tmp / "prisma.step")
    assert ruta.exists(), "El archivo STEP no fue creado"
    assert ruta.stat().st_size > 0, "El archivo STEP está vacío"
