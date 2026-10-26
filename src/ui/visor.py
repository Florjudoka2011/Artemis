"""
Generador del visor 3D basado en Three.js (WebGL).

Reemplaza gr.Model3D (Babylon.js WebGPU) que falla en Brave/Edge con:
  - Texture "randomSampler" not found
  - Uncaught TypeError: Failed to execute 'createBindGroup' on 'GPUDevice'

Three.js r0.128.0 (WebGL exclusivo, sin WebGPU). MIT License.
Archivos locales: src/ui/static/three/

Nota de integracion con Gradio:
  Gradio sanitiza gr.HTML y no ejecuta <script> directos
  (https://github.com/gradio-app/gradio/issues/7649).
  La solucion es un <iframe srcdoc="..."> cuyo contenido carga
  los scripts via URLs absolutas http://127.0.0.1:7860/file=...
  para evitar la dependencia en resolucion de paths relativos
  dentro del srcdoc. Ver ADR-003 para la justificacion de
  allow-same-origin.
"""

from __future__ import annotations

import html
from pathlib import Path

_STATIC_DIR = Path(__file__).parent / "static" / "three"

# URL base del servidor Gradio — fija por requisito de seguridad (T-173).
# La app solo escucha en 127.0.0.1:7860 (ver iniciar()).
# En Gradio 6.x el endpoint de archivos es /gradio_api/file= (API_PREFIX=/gradio_api).
_GRADIO_BASE_URL = "http://127.0.0.1:7860"
_FILE_ROUTE = "/gradio_api/file="

_EMPTY_HTML = (
    '<div id="visor-3d-empty" style="'
    "width:100%;height:360px;background:#1a1a2e;border-radius:8px;"
    "display:flex;align-items:center;justify-content:center;color:#555;"
    'font-family:monospace;font-size:13px;">'
    "Generá un modelo para ver el visor 3D"
    "</div>"
)


def _abs_file_url(path: Path) -> str:
    """URL absoluta http://127.0.0.1:7860/gradio_api/file=<ruta> para Gradio 6.x."""
    return _GRADIO_BASE_URL + _FILE_ROUTE + str(path).replace("\\", "/")


def make_viewer_html(ruta_stl: str | None) -> str:
    """Devuelve HTML con el visor Three.js dentro de un iframe srcdoc.

    Gradio sanitiza gr.HTML y no ejecuta <script> directos. La solucion
    es un <iframe srcdoc="..."> que corre su propio contexto JS.

    Los scripts Three.js se cargan con URLs absolutas
    http://127.0.0.1:7860/file=... para evitar la dependencia en
    resolucion de base href dentro del srcdoc. Ver ADR-003.

    ruta_stl es la ruta absoluta al archivo .stl generado. Gradio lo sirve
    via '/file=<ruta>' cuando la ruta esta en allowed_paths.
    Si ruta_stl es None, devuelve HTML con mensaje de espera.
    """
    if ruta_stl is None:
        return _EMPTY_HTML

    stl_url = _GRADIO_BASE_URL + _FILE_ROUTE + ruta_stl.replace("\\", "/")
    three_url = _abs_file_url(_STATIC_DIR / "three.min.js")
    stl_loader_url = _abs_file_url(_STATIC_DIR / "STLLoader.js")
    orbit_url = _abs_file_url(_STATIC_DIR / "OrbitControls.js")

    # HTML completo del visor — va dentro del srcdoc del iframe.
    # Scripts con URLs absolutas: no requiere <base href>.
    # allow-same-origin: necesario para que el STLLoader pueda hacer
    # XHR a http://127.0.0.1:7860 desde el iframe (ver ADR-003 S.4).
    inner_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ margin:0; padding:0; background:#0d0d1a; overflow:hidden; }}
  canvas {{ display:block; width:100%; height:100%; }}
</style>
</head>
<body>
<script src="{three_url}"></script>
<script src="{stl_loader_url}"></script>
<script src="{orbit_url}"></script>
<script>
(function() {{
  var renderer = new THREE.WebGLRenderer({{ antialias: true }});
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setClearColor(0x0d0d1a);
  document.body.appendChild(renderer.domElement);

  var scene = new THREE.Scene();
  var camera = new THREE.PerspectiveCamera(
    45, window.innerWidth / window.innerHeight, 0.1, 100000
  );
  camera.position.set(200, 200, 200);
  camera.lookAt(0, 0, 0);

  var controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.1;

  scene.add(new THREE.AmbientLight(0xffffff, 0.6));
  var dir = new THREE.DirectionalLight(0xffffff, 0.8);
  dir.position.set(300, 400, 300);
  scene.add(dir);

  scene.add(new THREE.GridHelper(300, 30, 0x333366, 0x222244));
  scene.add(new THREE.AxesHelper(50));

  var loader = new THREE.STLLoader();
  loader.load('{stl_url}', function(geometry) {{
    geometry.computeBoundingBox();
    var box = geometry.boundingBox;
    var center = new THREE.Vector3();
    box.getCenter(center);

    // CadQuery usa Z-up; Three.js usa Y-up: rotar -90 grados en X
    geometry.rotateX(-Math.PI / 2);
    geometry.translate(-center.x, -box.min.z, center.y);

    var mat = new THREE.MeshPhongMaterial({{
      color: 0x4fc3f7, specular: 0x888888, shininess: 60,
      side: THREE.DoubleSide
    }});
    scene.add(new THREE.Mesh(geometry, mat));

    // Encuadrar camara segun bounding box
    var size = new THREE.Vector3();
    box.getSize(size);
    var d = Math.max(size.x, size.y, size.z) * 1.5;
    camera.position.set(d, d * 0.8, d);
    camera.lookAt(0, 0, 0);
    controls.update();
  }});

  window.addEventListener('resize', function() {{
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  }});

  function animate() {{
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
  }}
  animate();
}})();
</script>
</body>
</html>"""

    # html.escape convierte " en &quot; para que el atributo srcdoc sea valido HTML
    srcdoc_attr = html.escape(inner_html, quote=True)

    return (
        f'<iframe srcdoc="{srcdoc_attr}" '
        'style="width:100%;height:400px;border:none;border-radius:8px;" '
        'sandbox="allow-scripts allow-same-origin">'
        "</iframe>"
    )
