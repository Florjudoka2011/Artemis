# ADR-003: Visor 3D — Three.js (WebGL) en lugar de gr.Model3D (Babylon.js WebGPU)

**Estado**: Aceptado
**Fecha**: 2026-10-25
**Autores**: Diego Saavedra

---

## Contexto

La Historia de Usuario 4 (US4) requiere un visor 3D interactivo integrado en el formulario Gradio
(FR-013). La primera implementación usó `gr.Model3D` de Gradio, que internamente usa Babylon.js v8
con motor de renderizado WebGPU.

### Errores observados con gr.Model3D (evidencia de la consola del navegador)

```
Texture "randomSampler" not found
Sampler "randomSamplerSampler" not found
Uncaught TypeError: Failed to execute 'createBindGroup' on 'GPUDevice'
```

- Reproducido en **Brave** y **Edge** (tema claro y oscuro).
- El componente falla incluso arrastrando un STL válido manualmente (Cura lo abre correctamente).
- Falla es del motor WebGPU de Babylon.js, no del STL generado.

### Investigación de alternativas dentro de gr.Model3D

Revisada la documentación oficial de Gradio (https://gradio.app/docs/gradio/model3d):
- No existe parámetro `renderer`, `engine`, `webgl` ni fallback configurable.
- El único motor disponible es Babylon.js (WebGPU).
- Issues en GitHub: no existe ningún issue de WebGL fallback ni feature request aceptado.

**Conclusión**: no es posible forzar WebGL en `gr.Model3D`. El componente debe reemplazarse.

---

## Decisión

Reemplazar `gr.Model3D` por un visor HTML propio basado en **Three.js r0.128.0** (WebGL puro),
embebido en un componente `gr.HTML` con `elem_id="visor-3d"`.

### Características del visor implementado

- **Motor**: Three.js r0.128.0 (WebGL exclusivo — lanzado antes de que Three.js incorporara
  soporte WebGPU, garantizando compatibilidad con Brave, Edge, Firefox y Chrome).
- **Archivos locales**: `src/ui/static/three/` (three.min.js, STLLoader.js, OrbitControls.js).
  Principio "todo local" — sin dependencias externas en runtime.
- **Controles**: OrbitControls (rotar, zoom, pan).
- **Referencia visual**: GridHelper + AxesHelper, estilo Cura.
- **Convención de ejes**: CadQuery genera Z-up. Three.js usa Y-up. Se aplica rotación
  `-Math.PI/2` en X para alinear los ejes al mostrar el modelo.
- **Servicio de archivos**: los STL y archivos static se sirven via
  `/gradio_api/file=<ruta>` (Gradio 6.x — `API_PREFIX=/gradio_api`).
  `gr.set_static_paths([src/ui/static])` registra los archivos Three.js.
  El workspace se declara en `allowed_paths` de `launch()`.
- **Integración con Gradio**: los `<script>` en `gr.HTML` son bloqueados por Gradio
  (issue #7649 — innerHTML no ejecuta scripts). Solución: `<iframe srcdoc="...">` con
  `sandbox="allow-scripts allow-same-origin"`.
- **Advertencia sandbox**: la combinación `allow-scripts` + `allow-same-origin` en el
  atributo sandbox del iframe puede en teoría permitir escapar el sandbox. Es aceptable
  porque: (1) el origen es `127.0.0.1:7860` — loopback exclusivo, sin acceso desde red;
  (2) el contenido del srcdoc es generado completamente por código Python interno, sin
  aceptar HTML externo; (3) las URLs de scripts usan `/gradio_api/file=` que requiere
  `gr.set_static_paths()` — no sirve rutas arbitrarias.
  Si en el futuro se requiere un sandbox más estricto, la alternativa es inline todos
  los scripts en el srcdoc (sin requests externos), eliminando la necesidad de
  `allow-same-origin`.

---

## Alternativas descartadas

| Alternativa | Razón de descarte |
|---|---|
| `gr.Model3D` (Babylon.js) | Error WebGPU en Brave/Edge, sin opción de fallback |
| Three.js vía CDN | Viola el principio "todo local" de la constitución |
| Babylon.js propio (WebGL mode) | Mayor peso, complejidad de integración con gr.HTML |
| vtk.js | Orientado a datos científicos/médicos, overkill para modelos mecánicos |

---

## Consecuencias

- `generar()` sigue devolviendo `(mensaje, ruta_stl: str | None)` — sin cambios en la API interna.
- `crear_interfaz()` usa `generar_con_visor()` como wrapper que convierte `ruta_stl` a HTML
  mediante `src/ui/visor.py::make_viewer_html()`.
- `gr.Model3D` eliminado de la interfaz. T-183 actualizado para verificar `gr.HTML` con
  `elem_id='visor-3d'`. T-186 cubre el invariante completo.
- Tres archivos locales nuevos (~625 KB total) en `src/ui/static/three/`. Licencia MIT.
