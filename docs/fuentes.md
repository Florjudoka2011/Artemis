# Fuentes y licencias de dependencias externas

## Dependencias directas del proyecto

| Paquete | Versión | Licencia | URL |
|---------|---------|----------|-----|
| pydantic | 2.14.1 | MIT | https://github.com/pydantic/pydantic |
| cadquery | 2.8.0 | Apache-2.0 | https://github.com/CadQuery/cadquery |
| gradio | (pendiente instalación) | Apache-2.0 | https://github.com/gradio-app/gradio |
| skia-python | 144.0 | BSD-3-Clause | https://github.com/kyamagu/skia-python |
| mcp | 2.3.0 | MIT | https://github.com/modelcontextprotocol/python-sdk |

## Archivos estáticos incluidos localmente

| Archivo | Versión | Licencia | URL fuente |
|---------|---------|----------|-----------|
| src/ui/static/three/three.min.js | r0.128.0 | MIT | https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js |
| src/ui/static/three/STLLoader.js | r0.128.0 | MIT | https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/STLLoader.js |
| src/ui/static/three/OrbitControls.js | r0.128.0 | MIT | https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js |

Motivo de inclusión local: principio "todo local" de la constitución. Sin CDN en runtime.
Ver ADR `docs/ADR/003-visor-3d.md`.

## Notas

- `mcp 2.3.0`: SDK oficial de Model Context Protocol para Python. Versión mínima requerida
  para compatibilidad con Pydantic ≥ 2.11 (la v1.9.4 usaba `pydantic._internal._typing_extra.eval_type_backport`,
  API privada eliminada en Pydantic 2.11).
- `skia-python 144.0`: Reemplaza a `cairosvg` en Windows porque `cairosvg` requiere
  `libcairo-2.dll` que no está disponible en Windows sin instalación manual adicional.
  Ver ADR `docs/ADR/001-entorno.md`.
