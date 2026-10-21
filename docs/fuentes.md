# Fuentes y licencias de dependencias externas

## Dependencias directas del proyecto

| Paquete | Versión | Licencia | URL |
|---------|---------|----------|-----|
| pydantic | 2.14.1 | MIT | https://github.com/pydantic/pydantic |
| cadquery | 2.8.0 | Apache-2.0 | https://github.com/CadQuery/cadquery |
| gradio | (pendiente instalación) | Apache-2.0 | https://github.com/gradio-app/gradio |
| skia-python | 144.0 | BSD-3-Clause | https://github.com/kyamagu/skia-python |
| mcp | 2.3.0 | MIT | https://github.com/modelcontextprotocol/python-sdk |

## Notas

- `mcp 2.3.0`: SDK oficial de Model Context Protocol para Python. Versión mínima requerida
  para compatibilidad con Pydantic ≥ 2.11 (la v1.9.4 usaba `pydantic._internal._typing_extra.eval_type_backport`,
  API privada eliminada en Pydantic 2.11).
- `skia-python 144.0`: Reemplaza a `cairosvg` en Windows porque `cairosvg` requiere
  `libcairo-2.dll` que no está disponible en Windows sin instalación manual adicional.
  Ver ADR `docs/ADR/001-entorno.md`.
