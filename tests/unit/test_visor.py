"""
Tests del generador de HTML del visor Three.js.

T-199 | geometria del visor respeta coordenadas del archivo STL (no centra).
"""

import pytest


@pytest.mark.mvp
def test_visor_no_centra_geometria():
    """T-199 | visor Three.js respeta zmin=0 de las recetas (no llama geometry.center()).

    Prueba: src/ui/visor.py::make_viewer_html

    Con la convencion zmin=0 en recetas, el visor NO debe compensar manualmente
    la posicion vertical. En particular:
    - NO debe usar geometry.center() (desharia la convencion).
    - Debe recomputar el bounding box DESPUES de rotateX para obtener valores
      correctos en coordenadas Three.js.
    - La camara debe apuntar al centro de la pieza (no al origen 0,0,0).
    """
    from src.ui.visor import make_viewer_html

    html = make_viewer_html("/fake/path/pieza.stl")

    assert "geometry.center()" not in html, (
        "El visor NO debe llamar geometry.center(): deshace la convencion zmin=0 "
        "de las recetas y hace que la pieza atraviese la grilla."
    )

    # Debe recomputar bounding box despues de la rotacion
    rotate_pos = html.find("rotateX")
    compute_pos = html.find("computeBoundingBox", rotate_pos)
    assert rotate_pos != -1, "El visor debe llamar rotateX"
    assert compute_pos != -1, (
        "El visor debe llamar computeBoundingBox() DESPUES de rotateX "
        "para obtener el bounding box en coordenadas Three.js correctas."
    )

    # La camara NO debe apuntar fijo al origen; debe usar el centro de la pieza
    assert "lookAt(0, 0, 0)" not in html, (
        "camera.lookAt(0,0,0) apunta al borde inferior de la pieza. "
        "Debe apuntar al centro geometrico de la pieza."
    )
