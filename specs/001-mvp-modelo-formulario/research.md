# Research: MVP — Modelo 3D desde Formulario

**Date**: 2026-10-18 | **Branch**: `001-mvp-modelo-formulario`

## Decisiones técnicas resueltas

---

### 1. Motor de modelado 3D: CadQuery

**Decision**: CadQuery (Python) con backend OCC (Open CASCADE Technology).

**Rationale**: Es la elección definida en la constitución y en `docs/00-idea.md §18`.
Modelado paramétrico determinista, API Python nativa, soporta STL y STEP. Alternativas
como FreeCAD (GUI-first), OpenSCAD (lenguaje propio), o build123d (wrapper más nuevo)
fueron descartadas antes de la constitución.

**Prisma rectangular en CadQuery**:
```python
import cadquery as cq
solid = cq.Workplane("XY").box(largo, ancho, alto)
```
El sólido resultante está centrado en el origen. Para agujero pasante centrado:
```python
solid = solid.faces(">Z").workplane().hole(diametro)
```
Para agujero con offset (cx, cy desde el centro de la cara):
```python
solid = solid.faces(">Z").workplane().center(cx, cy).hole(diametro)
```

**Cilindro en CadQuery**:
```python
solid = cq.Workplane("XY").cylinder(alto, diametro / 2)
```

**Tolerancia geométrica**: CadQuery opera en doble precisión (≈1e-15 mm). La tolerancia
del proyecto es 0,001 mm — ampliamente cubierta.

**Alternatives considered**: build123d (API más moderna, pero menos documentada para
exportación STEP en Windows); OpenSCAD (lenguaje DSL propio, no Python).

---

### 2. Exportación STL y STEP

**Decision**: API nativa de CadQuery.

**Rationale**: CadQuery expone `exporters.export()` con soporte para STL, STEP y SVG.
No requiere dependencias adicionales.

```python
from cadquery import exporters
exporters.export(solid, "modelo.stl")          # STL
exporters.export(solid, "modelo.step")         # STEP
exporters.export(solid, "vistas.svg",          # SVG (proyecciones)
    exportType="SVG",
    opt={"projectionDir": (1, -1, 1), ...}
)
```

**STL tolerance**: la triangulación introduce error máximo de ±0,5% en volumen — valor
documentado en constitución y tests.

**Alternatives considered**: pythonOCC directo (más control, mucho más verboso).

---

### 3. Vistas IRAM: proyecciones 2D desde CadQuery

**Decision**: Usar el exportador SVG de CadQuery con tres llamadas de proyección (planta,
alzado, perfil), ensambladas en un SVG compuesto.

**Rationale**: CadQuery puede exportar proyecciones ortogonales a SVG. Para vistas IRAM
(ISO E) se necesitan tres direcciones de proyección:

| Vista | Dirección de proyección (vector) |
|---|---|
| Alzado (frontal) | (0, -1, 0) — mirando desde el frente (Y negativo) |
| Planta (superior) | (0, 0, -1) — mirando desde arriba (Z negativo) |
| Perfil (lateral derecho) | (-1, 0, 0) — mirando desde la derecha (X negativo) |

La disposición ISO E: alzado en posición central, planta debajo, perfil a la derecha.
Las líneas de proyección (extensiones de cota) que conectan vistas se generan en el SVG
compuesto.

**Challenge conocido**: el exportador SVG de CadQuery produce un SVG por llamada. Hay que
componer las tres vistas en un solo SVG con offsets correctos para que los invariantes de
disposición se cumplan (tests T-120 a T-124). El módulo `views_iram/generator.py` es
responsable de esta composición.

**Alternatives considered**: FreeCAD en modo headless (excesivo para este caso); dibujar
las proyecciones manualmente con SVG primitives calculados desde los bounding boxes del
sólido (más control, pero mucho más trabajo).

---

### 4. Conversión SVG → PNG

**Decision**: cairosvg como primera opción; validar en Tarea 0 (ítem 6 de `docs/00-idea.md`).

**Rationale**: cairosvg es una librería Python pura (con dependencia de libcairo). En
Windows puede requerir instalar las DLLs de Cairo. Si la validación de Tarea 0 muestra
problemas, la alternativa es svglib + reportlab (más compatible con Windows sin DLLs).

**Tarea 0 gate**: no escribir código de conversión hasta validar que cairosvg (o la
alternativa elegida) funciona en el entorno de producción.

**Alternatives considered**: Inkscape en modo CLI (funciona pero requiere instalar Inkscape);
wand/ImageMagick (requiere ImageMagick instalado); Pillow solo (no tiene parser SVG nativo).

---

### 5. Interfaz: Gradio

**Decision**: Gradio como servidor local (127.0.0.1).

**Rationale**: Definido en constitución y docs. Gradio permite construir formularios
interactivos con Python puro, sin HTML/JS. Si el visor 3D no es suficientemente funcional
se reemplaza por Three.js (fuera del MVP).

**Feedback de generación**: Gradio soporta `gr.Button` con `loading=True` y `gr.State`
para bloquear la interfaz durante la generación. El mensaje "Generando…" se muestra
mediante un `gr.Textbox` o `gr.Label` de estado que se actualiza antes y después de la
llamada a la receta.

**Alternatives considered**: Streamlit (similar, pero menos control sobre el estado de
botones); Flask + HTML propio (más control, más trabajo fuera del alcance MVP).

---

### 6. Validación Pydantic

**Decision**: Pydantic v2 con `model_config = ConfigDict(extra="forbid")`.

**Rationale**: Definido en constitución §II y spec FR-005. `extra="forbid"` hace que campos
desconocidos fallen en validación (test T-106). Pydantic v2 es más rápido y tiene mejor
soporte para validators personalizados (para las reglas de rango: > 0, etc.).

**Schema de entrada** (ver `data-model.md` y `contracts/schema-figura.md` para el detalle).

---

### 7. Workspace y naming de archivos

**Decision**: carpeta por generación con formato `<figura>_<YYYYMMDD_HHMMSS>`. Si ya existe,
preguntar antes de sobreescribir (FR-010b, clarificación del 2026-10-18).

**Rationale**: el timestamp hace que dos generaciones del mismo tipo no colisionen de forma
silenciosa, preservando el trabajo anterior. La confirmación explícita es la única
interacción de conflicto en el MVP.

**Naming**: generado por la app, sin tildes, espacios ni secuencias de path traversal. Solo
caracteres `[a-z0-9_]` y guión bajo.

---

### 8. Tarea 0 — validaciones de entorno pendientes

Las siguientes decisiones están condicionadas a Tarea 0 y NO bloquean la arquitectura del
MVP, pero SÍ bloquean el inicio de la codificación:

| Ítem | Estado | Acción |
|---|---|---|
| GPU + ROCm (para IA futura) | Pendiente Tarea 0 | No aplica al MVP; registrar en ADR-001 |
| Stack Python: CadQuery + Gradio en Windows 11 | **Pendiente — BLOQUEANTE** | Validar antes de escribir código |
| cairosvg en Windows (SVG→PNG) | **Pendiente — BLOQUEANTE** | Validar antes de escribir export/views.py |
| Ruta workspace (fuera de OneDrive) | Pendiente Tarea 0 | Confirmar ruta default en config |
