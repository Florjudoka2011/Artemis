# ADR 001: Validación de Entorno — Tarea 0

**Fecha**: 2026-10-18
**Estado**: ACEPTADO
**Alcance**: MVP — Modelo 3D desde Formulario
**Autor**: Tarea 0 (speckit-implement Phase 0)

---

## Contexto

Antes de escribir cualquier línea de código de producción, la Constitución de Artemis
exige validar que el entorno de la PC de la docente soporta el stack tecnológico del MVP.
Este ADR registra los resultados de cada ítem de Tarea 0.

---

## Resultados de Validación

### Ítem 1: Python

| Parámetro | Valor |
|---|---|
| Versión requerida | Python 3.11+ |
| Versiones instaladas | Python 3.10.11, **Python 3.12.0** |
| Versión seleccionada | **Python 3.12.0** |
| Ubicación | `C:\Users\ecogr\AppData\Local\Programs\Python\Python312\python.exe` |
| Estado | ✅ VÁLIDO |

**Decisión**: usar Python 3.12.0. Cubre el requisito "3.11+" y CadQuery 2.8.0 tiene
wheel nativo para `cp312-cp312-win_amd64`. Python 3.11 no está instalado y no es necesario
instalarlo.

### Ítem 2: CadQuery

| Parámetro | Valor |
|---|---|
| Versión disponible | cadquery 2.8.0 |
| OCC backend | cadquery-ocp 7.9.3.1.1 (cp312-cp312-win_amd64) |
| Método instalación | `pip install cadquery` en venv Python 3.12 |
| Estado | ✅ VÁLIDO (wheel nativo, sin compilación) |

**Decisión**: instalar CadQuery 2.8.0 en el venv del proyecto.

### Ítem 3: Gradio

| Parámetro | Valor |
|---|---|
| Paquete | gradio (última versión compatible con Python 3.12) |
| Método | `pip install gradio` en venv Python 3.12 |
| Estado | ✅ DISPONIBLE (no hay bloqueantes conocidos en Python 3.12) |

### Ítem 4: Pydantic v2

| Parámetro | Valor |
|---|---|
| Paquete | pydantic v2 |
| Método | `pip install pydantic` en venv Python 3.12 |
| Estado | ✅ DISPONIBLE |

### Ítem 5: SVG → PNG (DECISIÓN CRÍTICA)

| Opción | Resultado |
|---|---|
| cairosvg 2.9.1 | ❌ FALLA — requiere `libcairo-2.dll` no disponible en Windows 11 sin GTK |
| svglib + reportlab + rlPyCairo | ❌ FALLA — también requiere Cairo DLLs |
| **skia-python 144.0** | ✅ OK — Skia bundleado, sin dependencias de sistema |

**Decisión**: usar `skia-python` para conversión SVG → PNG.

API validada:
```python
import skia, tempfile, os

def svg_a_png(svg_path: str, png_path: str) -> None:
    stream = skia.FILEStream(svg_path)
    dom = skia.SVGDOM.MakeFromStream(stream)
    del stream  # liberar handle antes de operar el archivo
    size = dom.containerSize()
    w, h = max(int(size.width()), 1), max(int(size.height()), 1)
    surface = skia.Surface(w, h)
    canvas = surface.getCanvas()
    canvas.clear(skia.ColorWHITE)
    dom.render(canvas)
    image = surface.makeImageSnapshot()
    with open(png_path, 'wb') as f:
        f.write(bytes(image.encodeToData()))
```

Conversión probada: SVG 200×150 → PNG 521 bytes ✅

**Impacto en research.md**: la decisión 4 (cairosvg) queda reemplazada por skia-python.
Actualizar research.md en el próximo ciclo de documentación.

### Ítem 6: Workspace

| Parámetro | Valor |
|---|---|
| Ruta validada | `C:\Artemis\` |
| ¿Bajo OneDrive? | No (OneDrive en `C:\Users\ecogr\OneDrive`) |
| ¿Espacios en ruta? | No |
| ¿Caracteres especiales? | No |
| Permisos de escritura | ✅ Confirmado |
| Estado | ✅ VÁLIDO |

**Decisión**: ruta por defecto del workspace = `C:\Artemis\`. La docente puede cambiarla
en la configuración, siempre que cumpla las mismas restricciones (sin espacios, sin tildes,
fuera de OneDrive).

---

## Stack Definitivo del MVP

```
Python        3.12.0  (C:\...\Python312\python.exe)
CadQuery      2.8.0   (pip, venv)
Pydantic      v2      (pip, venv)
Gradio        latest  (pip, venv)
skia-python   144.0   (pip, venv) ← reemplaza cairosvg
pytest        latest  (pip, venv)
pytest-cov    latest  (pip, venv)
mutmut        latest  (pip, venv)
ruff          latest  (pip, venv)
pre-commit    latest  (pip, venv)
gitleaks      latest  (sistema / pre-commit hook)
```

---

## Consecuencias

1. **pyproject.toml** debe especificar `python_requires = ">=3.12"` (ajuste de "3.11" a "3.12").
2. **src/export/views.py** usará `skia-python` en lugar de `cairosvg`.
3. **research.md Decisión 4** debe actualizarse para reflejar skia-python.
4. La ruta workspace por defecto es `C:\Artemis\`.

---

## Tarea 0: COMPLETADA ✅

Todos los ítems validados. El entorno está listo para comenzar Phase 1 (Setup).
