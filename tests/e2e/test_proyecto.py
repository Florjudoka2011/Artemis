"""
Tests e2e para exportación y carga de proyectos.

T-193 | guardado de proyecto.json junto al STL/STEP
T-194 | interfaz expone gr.File para descarga STL y STEP
T-195 | cargar_proyecto_json devuelve params reproducibles
T-196 | save + load + regenerate = mismo hash STL (round-trip)
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# T-193: generar() debe guardar proyecto.json en el mismo directorio que STL
# ---------------------------------------------------------------------------


@pytest.mark.mvp
def test_generar_guarda_proyecto_json(workspace_tmp: Path):
    """T-193 | 001/FR-014 — generar() guarda proyecto.json con la definicion de la pieza.

    Prueba: src/ui/app.py::generar

    Junto con cada STL/STEP debe existir un archivo proyecto.json con:
    - 'figura': nombre de la figura (str)
    - 'parametros': dict con los valores validados
    - 'version_artemis': string de version
    - 'fecha': string ISO 8601

    Permite a la docente reabrir exactamente la pieza generada.
    """
    from src.ui.app import generar

    msg, ruta_stl = generar(
        largo="100",
        ancho="60",
        alto="40",
        diametro="",
        figura="prisma_rectangular",
        vistas_iram=False,
    )

    assert ruta_stl is not None, f"generar() debio producir STL. msg={msg}"
    ruta_json = Path(ruta_stl).parent / "proyecto.json"

    assert ruta_json.exists(), (
        f"proyecto.json no encontrado en {ruta_json.parent}. "
        "generar() debe guardar la definicion de la pieza junto al STL."
    )

    data = json.loads(ruta_json.read_text(encoding="utf-8"))
    assert "figura" in data, "proyecto.json debe tener campo 'figura'"
    assert data["figura"] == "prisma_rectangular"
    assert "parametros" in data, "proyecto.json debe tener campo 'parametros'"
    assert data["parametros"]["largo"] == 100.0
    assert data["parametros"]["ancho"] == 60.0
    assert data["parametros"]["alto"] == 40.0
    assert "version_artemis" in data, "proyecto.json debe tener campo 'version_artemis'"
    assert "fecha" in data, "proyecto.json debe tener campo 'fecha'"


# ---------------------------------------------------------------------------
# T-194: crear_interfaz() expone botones de descarga para STL y STEP
# ---------------------------------------------------------------------------


@pytest.mark.mvp
def test_interfaz_tiene_descarga_stl_step():
    """T-194 | 001/FR-014 — crear_interfaz() expone componentes de descarga para STL y STEP.

    Prueba: src/ui/app.py::crear_interfaz

    La interfaz debe incluir al menos dos gr.DownloadButton (o gr.File con
    type='filepath') para que la docente pueda elegir dónde guardar STL y STEP.
    Verificamos que existen exactamente los componentes de salida de descarga.
    """
    import gradio as gr
    from src.ui.app import crear_interfaz

    demo = crear_interfaz()

    # Contar componentes de descarga (DownloadButton)
    download_components = [c for c in demo.blocks.values() if isinstance(c, gr.DownloadButton)]

    assert len(download_components) >= 2, (
        f"crear_interfaz() debe incluir al menos 2 gr.DownloadButton "
        f"(uno para STL y otro para STEP). Encontrados: {len(download_components)}. "
        f"Componentes: {[type(c).__name__ for c in demo.blocks.values()]}"
    )


# ---------------------------------------------------------------------------
# T-195: cargar_proyecto_json devuelve parametros para rellenar el formulario
# ---------------------------------------------------------------------------


@pytest.mark.mvp
def test_cargar_proyecto_json_devuelve_params(tmp_path):
    """T-195 | 001/FR-014 — cargar_proyecto_json() devuelve los params del formulario.

    Prueba: src/ui/app.py::cargar_proyecto_json

    Dado un proyecto.json valido, la funcion debe devolver un dict con los
    campos del formulario (figura, largo, ancho, alto, diametro) para que
    la UI pueda rellenar los campos automaticamente.
    """
    from src.ui.app import cargar_proyecto_json

    proyecto = {
        "figura": "prisma_rectangular",
        "parametros": {"largo": 150.0, "ancho": 80.0, "alto": 25.0},
        "version_artemis": "1.0.0",
        "fecha": "2026-10-25T22:00:00",
    }
    ruta = tmp_path / "proyecto.json"
    ruta.write_text(json.dumps(proyecto), encoding="utf-8")

    result = cargar_proyecto_json(str(ruta))

    assert result["figura"] == "prisma_rectangular"
    assert result["largo"] == "150.0"
    assert result["ancho"] == "80.0"
    assert result["alto"] == "25.0"
    assert result["diametro"] == ""


@pytest.mark.mvp
def test_cargar_proyecto_json_cilindro(tmp_path):
    """T-195b | cargar_proyecto_json maneja cilindro correctamente."""
    from src.ui.app import cargar_proyecto_json

    proyecto = {
        "figura": "cilindro",
        "parametros": {"diametro": 50.0, "alto": 30.0},
        "version_artemis": "1.0.0",
        "fecha": "2026-10-25T22:00:00",
    }
    ruta = tmp_path / "proyecto.json"
    ruta.write_text(json.dumps(proyecto), encoding="utf-8")

    result = cargar_proyecto_json(str(ruta))

    assert result["figura"] == "cilindro"
    assert result["diametro"] == "50.0"
    assert result["alto"] == "30.0"
    assert result["largo"] == ""
    assert result["ancho"] == ""


# ---------------------------------------------------------------------------
# T-196: round-trip save + load + regenerate = mismo hash STL
# ---------------------------------------------------------------------------


@pytest.mark.mvp
def test_generar_con_agujero_prisma(workspace_tmp: Path):
    """T-200 | 001/FR-002 — generar() con agujero pasante produce STL válido.

    Prueba: src/ui/app.py::generar (rama tiene_agujero=True)
    """
    from src.ui.app import generar

    # u=50, v=30: centro de cara superior (100×60). Coordenadas de borde.
    msg, ruta_stl = generar(
        largo="100",
        ancho="60",
        alto="40",
        diametro="",
        figura="prisma_rectangular",
        vistas_iram=False,
        tiene_agujero=True,
        diametro_agujero="20",
        cara_agujero="superior",
        u_agujero="50",
        v_agujero="30",
    )
    assert ruta_stl is not None, f"generar() con agujero debio producir STL. msg={msg}"
    assert Path(ruta_stl).exists()

    ruta_json = Path(ruta_stl).parent / "proyecto.json"
    assert ruta_json.exists()
    data = json.loads(ruta_json.read_text(encoding="utf-8"))
    assert data["parametros"].get("agujero") is not None
    assert data["parametros"]["agujero"]["diametro"] == 20.0


@pytest.mark.mvp
def test_generar_con_agujero_cilindro(workspace_tmp: Path):
    """T-201 | 001/FR-002 — generar() cilindro con agujero coaxial produce STL válido.

    Prueba: src/ui/app.py::generar (rama tiene_agujero=True, figura=cilindro)
    """
    from src.ui.app import generar

    msg, ruta_stl = generar(
        largo="",
        ancho="",
        alto="80",
        diametro="50",
        figura="cilindro",
        vistas_iram=False,
        tiene_agujero=True,
        diametro_agujero="20",
    )
    assert ruta_stl is not None, f"generar() cilindro con agujero debio producir STL. msg={msg}"
    assert Path(ruta_stl).exists()


@pytest.mark.mvp
def test_cargar_proyecto_json_con_agujero(tmp_path):
    """T-202 | 001/FR-002 — cargar_proyecto_json() recupera agujero del proyecto.json.

    Prueba: src/ui/app.py::cargar_proyecto_json (rama con agujero)
    """
    from src.ui.app import cargar_proyecto_json

    proyecto = {
        "figura": "prisma_rectangular",
        "parametros": {
            "largo": 100.0,
            "ancho": 60.0,
            "alto": 40.0,
            "agujero": {"diametro": 20.0, "cara": "superior"},
        },
        "version_artemis": "1.0.0",
        "fecha": "2026-10-26T00:00:00",
    }
    ruta = tmp_path / "proyecto.json"
    ruta.write_text(json.dumps(proyecto), encoding="utf-8")

    result = cargar_proyecto_json(str(ruta))

    assert result["tiene_agujero"] is True
    assert result["diametro_agujero"] == "20.0"


@pytest.mark.mvp
def test_generar_agujero_diametro_faltante():
    """T-203 | 001/FR-002 — generar() con tiene_agujero=True y sin diámetro retorna error.

    Prueba: src/ui/app.py::generar (rama faltante diámetro agujero)
    """
    from src.ui.app import generar

    msg, ruta_stl = generar(
        largo="100",
        ancho="60",
        alto="40",
        diametro="",
        figura="prisma_rectangular",
        vistas_iram=False,
        tiene_agujero=True,
        diametro_agujero="",
    )
    assert ruta_stl is None
    assert (
        "diametro_agujero" in msg.lower()
        or "faltante" in msg.lower()
        or "obligatorio" in msg.lower()
    )


@pytest.mark.mvp
def test_round_trip_proyecto_mismo_hash(workspace_tmp: Path):
    """T-196 | 001/FR-014 — Save + load proyecto.json + regenerate = mismo hash STL.

    Prueba: src/ui/app.py::generar, cargar_proyecto_json

    Guardar la pieza, leer el proyecto.json y regenerar con los mismos
    parametros debe producir exactamente el mismo archivo STL (mismo hash
    SHA-256). Garantiza que el formato de guardado es exacto y reproducible.
    """
    from src.ui.app import generar, cargar_proyecto_json

    # 1. Generar pieza original
    msg1, ruta_stl1 = generar(
        largo="120",
        ancho="70",
        alto="35",
        diametro="",
        figura="prisma_rectangular",
        vistas_iram=False,
    )
    assert ruta_stl1 is not None, f"Primera generacion fallo: {msg1}"
    hash1 = _sha256(Path(ruta_stl1))

    # 2. Cargar proyecto.json generado
    ruta_json = Path(ruta_stl1).parent / "proyecto.json"
    assert ruta_json.exists(), "proyecto.json no fue guardado en la primera generacion"
    params = cargar_proyecto_json(str(ruta_json))

    # 3. Regenerar con los mismos params
    msg2, ruta_stl2 = generar(
        largo=params["largo"],
        ancho=params["ancho"],
        alto=params["alto"],
        diametro=params["diametro"],
        figura=params["figura"],
        vistas_iram=False,
    )
    assert ruta_stl2 is not None, f"Segunda generacion fallo: {msg2}"
    hash2 = _sha256(Path(ruta_stl2))

    assert hash1 == hash2, (
        f"Round-trip fallido: el STL regenerado difiere del original.\n"
        f"Hash original: {hash1}\n"
        f"Hash regenerado: {hash2}\n"
        f"Params usados: {params}"
    )


# ---------------------------------------------------------------------------
# Tests US2-Ampliación: nuevos parámetros de agujero en app.py
# ---------------------------------------------------------------------------


@pytest.mark.mvp
def test_generar_agujero_ciego_via_ui(workspace_tmp: Path):
    """T-204 | 001/FR-002 — generar() prisma con agujero ciego via UI → STL válido.

    Prueba: src/ui/app.py::generar (agujero ciego con profundidad)
    """
    from src.ui.app import generar

    msg, ruta_stl = generar(
        largo="100",
        ancho="60",
        alto="40",
        diametro="",
        figura="prisma_rectangular",
        vistas_iram=False,
        tiene_agujero=True,
        diametro_agujero="20",
        cara_agujero="superior",
        u_agujero="50",
        v_agujero="30",
        tipo_agujero="ciego",
        profundidad_agujero="15",
    )
    assert ruta_stl is not None, f"generar() ciego debio producir STL. msg={msg}"
    assert Path(ruta_stl).exists()


@pytest.mark.mvp
def test_generar_agujero_desplazado_via_ui(workspace_tmp: Path):
    """T-205 | 001/FR-002 — generar() prisma con agujero desplazado u=20 → STL válido.

    Prueba: src/ui/app.py::generar (agujero pasante con u/v offset)
    """
    from src.ui.app import generar

    msg, ruta_stl = generar(
        largo="100",
        ancho="60",
        alto="40",
        diametro="",
        figura="prisma_rectangular",
        vistas_iram=False,
        tiene_agujero=True,
        diametro_agujero="20",
        cara_agujero="superior",
        u_agujero="20",
        v_agujero="30",
        tipo_agujero="pasante",
        profundidad_agujero="",
    )
    assert ruta_stl is not None, f"generar() desplazado debio producir STL. msg={msg}"
    assert Path(ruta_stl).exists()


@pytest.mark.mvp
def test_generar_agujero_fuera_de_cara_retorna_error(workspace_tmp: Path):
    """T-206 | 001/FR-002 — generar() prisma agujero fuera de cara → error geométrico.

    Prueba: src/ui/app.py::generar (agujero rechazado por límites)

    Coordenadas de borde: u=91 > u_max=90 (face_w=100, radio=10) → rechazado.
    """
    from src.ui.app import generar

    msg, ruta_stl = generar(
        largo="100",
        ancho="60",
        alto="40",
        diametro="",
        figura="prisma_rectangular",
        vistas_iram=False,
        tiene_agujero=True,
        diametro_agujero="20",
        cara_agujero="superior",
        u_agujero="91",
        v_agujero="30",
        tipo_agujero="pasante",
        profundidad_agujero="",
    )
    assert ruta_stl is None, "Agujero fuera de cara debe retornar ruta_stl=None"
    assert "geométrico" in msg or "fuera" in msg.lower() or "excede" in msg.lower()


@pytest.mark.mvp
def test_cargar_proyecto_json_agujero_completo(tmp_path):
    """T-207 | 001/FR-002 — cargar_proyecto_json() recupera todos los campos del agujero.

    Prueba: src/ui/app.py::cargar_proyecto_json (campos tipo, u, v, profundidad)
    """
    from src.ui.app import cargar_proyecto_json

    proyecto = {
        "figura": "prisma_rectangular",
        "parametros": {
            "largo": 100.0,
            "ancho": 60.0,
            "alto": 40.0,
            "agujero": {
                "diametro": 20.0,
                "cara": "superior",
                "tipo": "ciego",
                "u": 10.0,
                "v": 5.0,
                "profundidad": 15.0,
            },
        },
        "version_artemis": "1.0.0",
        "fecha": "2026-10-26T00:00:00",
    }
    ruta = tmp_path / "proyecto.json"
    ruta.write_text(json.dumps(proyecto), encoding="utf-8")

    result = cargar_proyecto_json(str(ruta))

    assert result["tiene_agujero"] is True
    assert result["diametro_agujero"] == "20.0"
    assert result["cara_agujero"] == "superior"
    assert result["tipo_agujero"] == "ciego"
    assert result["u_agujero"] == "10.0"
    assert result["v_agujero"] == "5.0"
    assert result["profundidad_agujero"] == "15.0"


@pytest.mark.mvp
def test_generar_agujero_ciego_sin_profundidad_retorna_error():
    """T-208 | 001/FR-002 — generar() ciego sin profundidad → error de validación.

    Prueba: src/ui/app.py::generar (ciego requiere profundidad)
    """
    from src.ui.app import generar

    msg, ruta_stl = generar(
        largo="100",
        ancho="60",
        alto="40",
        diametro="",
        figura="prisma_rectangular",
        vistas_iram=False,
        tiene_agujero=True,
        diametro_agujero="20",
        cara_agujero="superior",
        u_agujero="0",
        v_agujero="0",
        tipo_agujero="ciego",
        profundidad_agujero="",
    )
    assert ruta_stl is None
    assert "validación" in msg.lower() or "profundidad" in msg.lower()
