"""
Generador del visor 3D basado en Three.js (WebGL).

Reemplaza gr.Model3D (Babylon.js WebGPU) que falla en Brave/Edge con:
  - Texture "randomSampler" not found
  - Uncaught TypeError: Failed to execute 'createBindGroup' on 'GPUDevice'

Three.js r0.128.0 (WebGL exclusivo, sin WebGPU). MIT License.
Archivos locales: src/ui/static/three/
"""

from __future__ import annotations

from pathlib import Path

_STATIC_DIR = Path(__file__).parent / "static" / "three"

_EMPTY_HTML = (
    '<div id="visor-3d-empty" style="'
    "width:100%;height:360px;background:#1a1a2e;border-radius:8px;"
    "display:flex;align-items:center;justify-content:center;color:#555;"
    'font-family:monospace;font-size:13px;">'
    "Generá un modelo para ver el visor 3D"
    "</div>"
)


def _file_url(path: Path) -> str:
    """Convierte ruta local a URL /file= de Gradio (slash forward)."""
    return "/file=" + str(path).replace("\\", "/")


def make_viewer_html(ruta_stl: str | None) -> str:
    """Devuelve HTML con el visor Three.js apuntando a ruta_stl.

    ruta_stl es la ruta absoluta al archivo .stl generado. Gradio lo sirve
    via '/file=<ruta>' cuando la ruta está en allowed_paths.
    Si ruta_stl es None, devuelve HTML con mensaje de espera.
    """
    if ruta_stl is None:
        return _EMPTY_HTML

    stl_url = "/file=" + ruta_stl.replace("\\", "/")
    three_url = _file_url(_STATIC_DIR / "three.min.js")
    stl_loader_url = _file_url(_STATIC_DIR / "STLLoader.js")
    orbit_url = _file_url(_STATIC_DIR / "OrbitControls.js")

    wrapper_style = (
        "width:100%;height:400px;background:#0d0d1a;"
        "border-radius:8px;overflow:hidden;position:relative;"
    )
    return f"""<div id="visor-3d-canvas-wrapper" style="{wrapper_style}">
  <canvas id="visor-3d-canvas" style="width:100%;height:100%;display:block;"></canvas>
</div>
<script src="{three_url}"></script>
<script src="{stl_loader_url}"></script>
<script src="{orbit_url}"></script>
<script>
(function() {{
  var canvas = document.getElementById('visor-3d-canvas');
  if (!canvas || typeof THREE === 'undefined') return;

  var renderer = new THREE.WebGLRenderer({{ canvas: canvas, antialias: true }});
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(canvas.clientWidth || 600, canvas.clientHeight || 400);
  renderer.setClearColor(0x0d0d1a);

  var scene = new THREE.Scene();
  var w = canvas.clientWidth || 600;
  var h = canvas.clientHeight || 400;
  var camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 10000);
  camera.position.set(200, 200, 200);
  camera.lookAt(0, 0, 0);

  var controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.1;

  scene.add(new THREE.AmbientLight(0xffffff, 0.6));
  var dir = new THREE.DirectionalLight(0xffffff, 0.8);
  dir.position.set(300, 400, 300);
  scene.add(dir);

  // Grilla y ejes estilo Cura
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
    // Centrar el objeto sobre la grilla
    geometry.translate(-center.x, -box.min.z, center.y);

    var mat = new THREE.MeshPhongMaterial({{
      color: 0x4fc3f7, specular: 0x888888, shininess: 60, side: THREE.DoubleSide
    }});
    scene.add(new THREE.Mesh(geometry, mat));

    // Ajustar camara al bounding box del objeto
    var size = new THREE.Vector3();
    box.getSize(size);
    var d = Math.max(size.x, size.y, size.z) * 1.5;
    camera.position.set(d, d * 0.8, d);
    camera.lookAt(0, 0, 0);
    controls.update();
  }});

  function animate() {{
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
  }}
  animate();
}})();
</script>"""
