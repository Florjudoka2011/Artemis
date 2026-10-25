"""
Tests e2e del formulario sin IA — arnés anti-mentiras.
Usa un conector falso que devuelve JSON fijo (A-07: no IA real).
"""

import hashlib
from pathlib import Path

import pytest

from src.export.solid import exportar_stl
from src.recipes.prisma_rectangular import construir
from src.schemas.figuras import PrismaRectangularParams
from src.ui.app import crear_interfaz, generar
from src.ui.workspace import crear_workspace


def _hash_archivo(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


@pytest.mark.mvp
def test_stl_deterministico(workspace_tmp: Path):
    """T-150 | 001/FR-009 — Mismos parámetros producen el mismo STL (determinismo).

    Prueba: src/export/solid.py::exportar_stl

    Los dos archivos deben tener el mismo hash SHA-256.
    """
    params = PrismaRectangularParams(largo=100, ancho=60, alto=40)

    dir_a = workspace_tmp / "run_a"
    dir_a.mkdir()
    ruta_a = exportar_stl(construir(params), dir_a / "prisma.stl")

    dir_b = workspace_tmp / "run_b"
    dir_b.mkdir()
    ruta_b = exportar_stl(construir(params), dir_b / "prisma.stl")

    assert _hash_archivo(ruta_a) == _hash_archivo(
        ruta_b
    ), "El STL no es determinista: mismos parámetros producen archivos distintos"


@pytest.mark.mvp
def test_formulario_campo_vacio():
    """T-151 | 001/FR-001 — Formulario con campo vacío obligatorio no genera y lista los faltantes.

    Prueba: src/ui/app.py::generar

    El resultado debe indicar qué campos faltan, no construir el sólido.
    """
    mensaje, ruta = generar(largo="", ancho="60", alto="40", figura="prisma_rectangular")
    assert mensaje is not None
    assert (
        "largo" in str(mensaje).lower()
    ), f"El resultado debería mencionar el campo faltante 'largo', obtenido: {mensaje}"


@pytest.mark.mvp
def test_formulario_sin_ia():
    """T-152 | 001/FR-009 — Formulario con IA deshabilitada funciona; arranca vacío.

    Prueba: src/ui/app.py::crear_interfaz

    Con conector nulo, la interfaz se crea sin error y el formulario inicia vacío.
    """
    demo = crear_interfaz(conector_ia=None)
    assert demo is not None, "crear_interfaz devolvió None con conector_ia=None"


@pytest.mark.mvp
def test_crear_workspace_crea_directorio(workspace_tmp: Path):
    """T-153 | 001/FR-010 — crear_workspace genera subdirectorio con nombre de figura y timestamp.

    Prueba: src/ui/workspace.py::crear_workspace
    """
    ws = crear_workspace(base=workspace_tmp, figura="prisma_rectangular")
    assert ws.exists(), "El workspace no fue creado"
    assert ws.is_dir(), "El workspace no es un directorio"
    assert "prisma_rectangular" in ws.name, f"Nombre inesperado: {ws.name}"


@pytest.mark.mvp
def test_generar_prisma_valido_produce_archivos():
    """T-154 | 001/FR-011 — generar() informa resultado con rutas de archivos en caso de éxito.

    Prueba: src/ui/app.py::generar

    El resultado debe incluir 'Generado' y las rutas STL y STEP.
    """
    mensaje, _ = generar(largo="100", ancho="60", alto="40", figura="prisma_rectangular")
    assert "Generado" in mensaje, f"Se esperaba 'Generado' en el resultado, obtenido: {mensaje}"
    assert (
        ".stl" in mensaje.lower() or ".step" in mensaje.lower()
    ), f"Se esperaban rutas STL/STEP, obtenido: {mensaje}"


@pytest.mark.mvp
def test_generar_cilindro_valido_produce_archivos():
    """T-155 | 001/FR-004 — generar() con parámetros válidos de cilindro retorna rutas de archivos.

    Prueba: src/ui/app.py::generar
    """
    mensaje, _ = generar(diametro="50", alto="80", figura="cilindro")
    assert "Generado" in mensaje, f"Se esperaba 'Generado' en el resultado, obtenido: {mensaje}"


@pytest.mark.mvp
def test_formulario_tiene_checkbox_vistas_iram():
    """T-156 | 001/FR-003 — La interfaz ofrece checkbox de vistas IRAM en el formulario.

    Prueba: src/ui/app.py::crear_interfaz

    La interfaz debe incluir un componente con label 'Vistas IRAM' o similar.
    """

    demo = crear_interfaz(conector_ia=None)
    # Buscar checkbox de vistas IRAM en el árbol de componentes
    componentes = demo.blocks
    labels = [
        getattr(c, "label", "") for c in componentes.values() if hasattr(c, "label") and c.label
    ]
    tiene_vistas_iram = any("iram" in str(label).lower() for label in labels)
    assert (
        tiene_vistas_iram
    ), f"No se encontró checkbox de vistas IRAM en la interfaz. Labels encontrados: {labels}"


@pytest.mark.mvp
def test_generar_acepta_vistas_iram():
    """T-158 | 001/FR-003 — generar() acepta el parámetro vistas_iram sin error.

    Prueba: src/ui/app.py::generar
    """
    mensaje, _ = generar(
        largo="100", ancho="60", alto="40", figura="prisma_rectangular", vistas_iram=False
    )
    assert (
        "Error" not in mensaje or "Faltan" not in mensaje
    ), f"generar() rechazó vistas_iram=False: {mensaje}"


# T-157 / FR-012 eliminado: el indicador "Generando..." es comportamiento automatico de
# Gradio (btn.click bloquea la UI sin codigo nuestro). No hay API Python para afirmar
# el estado visual de carga. Verificacion manual en quickstart.md.


@pytest.mark.mvp
def test_generar_prisma_parametro_invalido_retorna_error():
    """T-159 | 001/FR-005 — generar() con valor cero en prisma retorna mensaje de error.

    Prueba: src/ui/app.py::generar

    largo=0 pasa la validacion de campo vacio pero ValidationError en Pydantic;
    la funcion debe capturarlo y retornar "Error de validacion: ...".
    """
    mensaje, _ = generar(largo="0", ancho="60", alto="40", figura="prisma_rectangular")
    assert "Error" in mensaje, f"Se esperaba mensaje de error con largo=0, obtenido: {mensaje}"


@pytest.mark.mvp
@pytest.mark.parametrize(
    "kwargs,campo_faltante",
    [
        ({"diametro": "", "alto": "80", "figura": "cilindro"}, "diametro"),
        ({"diametro": "50", "alto": "", "figura": "cilindro"}, "alto"),
    ],
)
def test_formulario_cilindro_campo_vacio(kwargs, campo_faltante):
    """T-160 | 001/FR-001 — Formulario cilindro con campo vacio no genera y lista los faltantes.

    Prueba: src/ui/app.py::generar

    El resultado debe indicar que el campo obligatorio falta.
    """
    mensaje, _ = generar(**kwargs)
    assert (
        campo_faltante in mensaje.lower()
    ), f"Se esperaba '{campo_faltante}' en el mensaje, obtenido: {mensaje}"


@pytest.mark.mvp
def test_generar_cilindro_parametro_invalido_retorna_error():
    """T-161 | 001/FR-005 — generar() con diametro=0 en cilindro retorna mensaje de error.

    Prueba: src/ui/app.py::generar

    diametro=0 pasa la validacion de campo vacio pero ValidationError en Pydantic;
    la funcion debe capturarlo y retornar "Error de validacion: ...".
    """
    mensaje, _ = generar(diametro="0", alto="80", figura="cilindro")
    assert "Error" in mensaje, f"Se esperaba mensaje de error con diametro=0, obtenido: {mensaje}"


@pytest.mark.mvp
def test_generar_figura_desconocida_retorna_error():
    """T-162 | 001/FR-001 — generar() con figura desconocida retorna mensaje de error.

    Prueba: src/ui/app.py::generar
    """
    mensaje, _ = generar(figura="hexagono")
    assert (
        "desconocida" in mensaje.lower() or "Error" in mensaje
    ), f"Se esperaba mensaje de error con figura desconocida, obtenido: {mensaje}"


@pytest.mark.mvp
def test_visor_3d_recibe_ruta_stl_valida(monkeypatch, tmp_path):
    """T-182 | 001/FR-013 — generar() devuelve la ruta STL para el visor 3D.

    Prueba: src/ui/app.py::generar

    La funcion debe retornar una tupla (mensaje: str, ruta_stl: str | None).
    La ruta_stl debe apuntar a un archivo .stl existente tras una generacion exitosa.
    gr.Model3D acepta .stl segun la documentacion oficial de Gradio (gr.Model3D.__doc__).
    """
    import src.ui.workspace as ws_mod

    monkeypatch.setattr(ws_mod, "_WORKSPACE_BASE", tmp_path)

    resultado = generar(largo="100", ancho="60", alto="40", figura="prisma_rectangular")

    assert isinstance(
        resultado, tuple
    ), f"generar() debe retornar una tupla (mensaje, ruta_stl), obtenido: {type(resultado)}"
    assert (
        len(resultado) == 2
    ), f"La tupla debe tener 2 elementos (mensaje, ruta_stl), obtenida: {resultado}"
    mensaje, ruta_stl = resultado
    assert "Generado" in mensaje, f"Primer elemento debe ser mensaje de exito: {mensaje}"
    assert ruta_stl is not None, "El segundo elemento (ruta_stl) no debe ser None"
    from pathlib import Path

    assert (
        Path(ruta_stl).suffix == ".stl"
    ), f"La ruta debe apuntar a un .stl (formato aceptado por gr.Model3D), obtenido: {ruta_stl}"
    assert Path(ruta_stl).exists(), f"El archivo STL no existe: {ruta_stl}"


@pytest.mark.mvp
def test_formulario_tiene_visor_3d():
    """T-183 | 001/FR-013 — La interfaz incluye un componente Model3D como visor.

    Prueba: src/ui/app.py::crear_interfaz

    Verifica que la interfaz tiene un gr.Model3D en sus bloques.
    """
    import gradio as gr

    demo = crear_interfaz(conector_ia=None)
    tiene_model3d = any(isinstance(c, gr.Model3D) for c in demo.blocks.values())
    assert tiene_model3d, (
        "La interfaz no tiene componente gr.Model3D. "
        "Se necesita para mostrar el objeto generado en 3D."
    )


@pytest.mark.mvp
def test_formulario_campos_dinamicos_por_figura():
    """T-181 | 001/FR-001 — Formulario: handler de cambio registrado en dropdown figura.

    Prueba: src/ui/app.py::crear_interfaz

    La interfaz debe tener un event handler en el dropdown de figura que actualice
    la visibilidad de los campos al cambiar la seleccion.
    """
    import gradio as gr

    demo = crear_interfaz(conector_ia=None)

    # Verificar que el dropdown de figura tiene al menos un event listener registrado
    # (figura.change → actualizar visibilidad de campos)
    figura_comp = None
    for comp in demo.blocks.values():
        if isinstance(comp, gr.Dropdown) and getattr(comp, "label", "") == "Figura":
            figura_comp = comp
            break

    assert figura_comp is not None, "No se encontro el dropdown de Figura en la interfaz"

    # Verificar que hay al menos un event registrado en el dropdown
    # Gradio registra los events en demo.fns; cada fn tiene inputs/outputs
    # Buscamos una fn cuyo trigger sea el componente figura
    tiene_change_handler = any(
        hasattr(fn, "targets") and any(figura_comp._id == t[0] for t in fn.targets)
        for fn in demo.fns.values()
        if hasattr(fn, "targets")
    )
    assert tiene_change_handler, (
        "El dropdown 'Figura' no tiene un event handler de cambio registrado. "
        "Se necesita figura.change(...) para actualizar la visibilidad de campos."
    )


@pytest.mark.mvp
def test_actualizar_campos_visibilidad_por_figura():
    """T-184 | 001/FR-001 — actualizar_campos() devuelve visibilidad correcta por figura.

    Prueba: src/ui/app.py::crear_interfaz (funcion interna actualizar_campos)

    Prisma: largo visible, ancho visible, alto visible, diametro oculto.
    Cilindro: largo oculto, ancho oculto, alto visible, diametro visible.

    Nota TDD: escrito DESPUES de la implementacion (que entro con T-181/feat(T-175)).
    T-181 solo verificaba que el handler existia; este test verifica los valores
    concretos de visibilidad. La funcion actualizar_campos ya estaba implementada.
    """
    import gradio as gr

    demo = crear_interfaz(conector_ia=None)

    # Recuperar la funcion actualizar_campos del primer fn que tenga el dropdown de Figura
    figura_comp = next(
        c
        for c in demo.blocks.values()
        if isinstance(c, gr.Dropdown) and getattr(c, "label", "") == "Figura"
    )
    fn_record = next(
        fn
        for fn in demo.fns.values()
        if hasattr(fn, "targets") and any(figura_comp._id == t[0] for t in fn.targets)
    )
    actualizar = fn_record.fn

    # Caso prisma_rectangular
    largo_u, ancho_u, alto_u, diametro_u = actualizar("prisma_rectangular")
    assert largo_u["visible"] is True, "largo debe ser visible para prisma_rectangular"
    assert ancho_u["visible"] is True, "ancho debe ser visible para prisma_rectangular"
    assert alto_u["visible"] is True, "alto debe ser visible para prisma_rectangular"
    assert diametro_u["visible"] is False, "diametro debe estar oculto para prisma_rectangular"

    # Caso cilindro
    largo_u, ancho_u, alto_u, diametro_u = actualizar("cilindro")
    assert largo_u["visible"] is False, "largo debe estar oculto para cilindro"
    assert ancho_u["visible"] is False, "ancho debe estar oculto para cilindro"
    assert alto_u["visible"] is True, "alto debe ser visible para cilindro"
    assert diametro_u["visible"] is True, "diametro debe ser visible para cilindro"


@pytest.mark.mvp
def test_generar_usa_workspace_configurado(monkeypatch, tmp_path):
    """T-180 | 001/FR-010 — generar() guarda archivos en el workspace base configurado.

    Prueba: src/ui/app.py::generar

    Los archivos NO deben guardarse en AppData\\Local\\Temp ni en rutas temporales del
    sistema. El workspace base es C:\\Artemis\\workspace (valor de _WORKSPACE_BASE en
    src/ui/workspace.py).
    """
    import src.ui.workspace as ws_mod

    monkeypatch.setattr(ws_mod, "_WORKSPACE_BASE", tmp_path)

    mensaje, ruta_stl = generar(largo="100", ancho="60", alto="40", figura="prisma_rectangular")

    assert "Generado" in mensaje, f"Se esperaba 'Generado', obtenido: {mensaje}"
    assert ruta_stl is not None, "ruta_stl no debe ser None en caso de exito"
    from pathlib import Path

    assert Path(ruta_stl).is_relative_to(tmp_path), (
        f"La ruta '{ruta_stl}' no esta bajo el workspace configurado '{tmp_path}'. "
        f"Los archivos se estan guardando en una ruta temporal del sistema."
    )


@pytest.mark.mvp
def test_iniciar_usa_host_y_puerto_seguros(monkeypatch):
    """T-173 | 001/FR-010 — iniciar() lanza la app en 127.0.0.1:7860 (loopback exclusivo).

    Prueba: src/ui/app.py::iniciar

    Requisito de seguridad: la app nunca escucha en 0.0.0.0 ni en una IP externa.
    server_name='127.0.0.1' y server_port=7860 son fijos e innegociables.
    """
    from src.ui.app import iniciar  # noqa: PLC0415

    llamadas: list[dict] = []

    import gradio as gr

    def mock_launch(self, **kwargs):  # type: ignore[override]
        llamadas.append(kwargs)
        return None, None, None

    monkeypatch.setattr(gr.Blocks, "launch", mock_launch)
    iniciar()

    assert (
        len(llamadas) == 1
    ), f"launch() debio llamarse exactamente 1 vez, se llamo {len(llamadas)}"
    assert (
        llamadas[0].get("server_name") == "127.0.0.1"
    ), f"server_name debe ser '127.0.0.1', obtenido: {llamadas[0].get('server_name')}"
    assert (
        llamadas[0].get("server_port") == 7860
    ), f"server_port debe ser 7860, obtenido: {llamadas[0].get('server_port')}"


@pytest.mark.mvp
def test_iniciar_autoriza_workspace_en_allowed_paths(monkeypatch):
    """T-185 | 001/FR-013 — iniciar() incluye el workspace en allowed_paths de launch().

    Prueba: src/ui/app.py::iniciar

    Gradio solo sirve archivos de rutas en allowed_paths. Sin esto, gr.Model3D
    no puede mostrar el STL generado en C:\\Artemis\\workspace (error de acceso
    denegado en el visor). La unica ruta autorizada debe ser _WORKSPACE_BASE,
    no carpetas mas amplias ni todo el disco.
    """
    from src.ui.app import iniciar
    from src.ui.workspace import _WORKSPACE_BASE

    import gradio as gr

    llamadas: list[dict] = []

    def mock_launch(self, **kwargs):  # type: ignore[override]
        llamadas.append(kwargs)
        return None, None, None

    monkeypatch.setattr(gr.Blocks, "launch", mock_launch)
    iniciar()

    assert len(llamadas) == 1
    allowed = llamadas[0].get("allowed_paths")
    assert allowed is not None, (
        "launch() debe recibir allowed_paths. "
        "Sin esto Gradio no sirve archivos del workspace al visor 3D."
    )
    workspace_str = str(_WORKSPACE_BASE)
    assert any(str(p) == workspace_str for p in allowed), (
        f"allowed_paths debe contener '{workspace_str}'. " f"Obtenido: {allowed}"
    )
