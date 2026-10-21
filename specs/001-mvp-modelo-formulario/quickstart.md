# Quickstart: Validación del MVP — Modelo 3D desde Formulario

**Date**: 2026-10-18 | **Branch**: `001-mvp-modelo-formulario`

Guía de validación end-to-end. Cubre los criterios de aceptación del MVP sin detalles de
implementación. Ver `contracts/` para schemas y `data-model.md` para entidades.

---

## Prerrequisitos

1. **Tarea 0 completada**: stack Python (CadQuery + Gradio) validado en Windows 11; ruta
   de workspace definida en config (no bajo OneDrive, sin espacios ni tildes).
2. Entorno virtual activo con dependencias instaladas.
3. Workspace de prueba disponible (ej. `C:\ModeladorPrueba\`).

---

## Escenario 1 — Prisma rectangular sin agujero (SC-001, SC-002, SC-006)

**Objetivo**: verificar generación básica, tiempo < 10 s, determinismo.

```bash
# Ejecutar tests de receta del prisma rectangular
pytest tests/unit/test_recipes_prisma.py::test_nominal -v
```

**Resultado esperado**:
- Test pasa en < 10 s.
- Volumen calculado: 240 000 mm³ ± 1 ppm (tolerancia interna CadQuery).
- Ejecutar dos veces → mismo hash de sólido resultante.

---

## Escenario 2 — Cilindro (SC-001, SC-002)

```bash
pytest tests/unit/test_recipes_cilindro.py::test_nominal -v
```

**Resultado esperado**: volumen = 157 079,633 mm³ ± 1 ppm.

---

## Escenario 3 — Agujero pasante en prisma rectangular (SC-004)

```bash
pytest tests/unit/test_recipes_prisma.py::test_agujero_pasante_centrado -v
pytest tests/unit/test_recipes_prisma.py::test_agujero_invalido_diametro_mayor -v
pytest tests/unit/test_recipes_prisma.py::test_agujero_invalido_fuera_de_cara -v
```

**Resultado esperado**:
- Agujero válido (d=20): volumen = 227 433,629 mm³ ± 1 ppm.
- Agujero inválido (d=40 en ancho=40): `ValueError` con mensaje descriptivo, sin tocar CadQuery.
- Agujero fuera de cara: `ValueError` antes de construir.

---

## Escenario 4 — Validación Pydantic (SC-004)

```bash
pytest tests/unit/test_schemas.py -v
```

**Resultado esperado**: T-100 a T-108 pasan; JSONs inválidos producen `ValidationError`
con el campo identificado.

---

## Escenario 5 — Exportación STL y STEP (SC-002)

```bash
pytest tests/integration/test_export.py -v
```

**Resultado esperado**:
- T-110: archivo `.stl` > 0 bytes; volumen STL dentro de ±0,5% del volumen teórico.
- T-111: archivo `.step` > 0 bytes; parseable por una librería STEP.

---

## Escenario 6 — Vistas IRAM: invariantes geométricos (SC-003)

```bash
pytest tests/integration/test_views_iram.py -v
```

**Resultado esperado**: T-120 a T-124 pasan. Para el prisma rectangular (100×60×40):
- Planta debajo del alzado en el SVG compuesto.
- Perfil a la derecha del alzado.
- Ancho X compartido entre alzado y planta.
- Altura Z compartida entre alzado y perfil.
- Profundidad Y compartida entre planta y perfil.

---

## Escenario 7 — Conversión SVG → PNG (SC-003)

```bash
pytest tests/integration/test_export.py::test_svg_a_png -v
```

**Resultado esperado**: T-113 pasa; archivo `.png` válido con dimensiones > 0.

---

## Escenario 8 — Modo formulario sin IA (SC-005, SC-006)

```bash
pytest tests/e2e/test_formulario.py -v
```

**Resultado esperado**:
- T-150: STL desde conector falso = STL desde entrada manual (mismo hash).
- T-151: campo vacío obligatorio → lista de campos faltantes, sin generación.
- T-152: IA deshabilitada → formulario arranca vacío, funciona igual.

---

## Suite completa del MVP

```bash
# Todos los tests del MVP con cobertura
pytest -m mvp --tb=short -v --cov=src --cov-report=term-missing

# Guardar evidencia
pytest -m mvp --tb=short -v --cov=src --cov-report=term-missing \
  > docs/evidencia/fase1/mvp-$(date +%Y%m%d-%H%M%S).txt
```

**Criterio de aceptación del MVP**: todos los tests del conjunto `mvp` pasan, cobertura
de `src/recipes/` y `src/schemas/` al 100%, sin líneas no cubiertas en rutas de validación.

---

## Indicador "Generando…" (FR-012) — Verificación manual

El bloqueo de UI durante la generación lo provee Gradio automáticamente (`btn.click` deshabilita
el botón y muestra un spinner). No existe API Python para afirmar el estado visual en tests.

**Validar manualmente**:
1. Lanzar la app: `.venv\Scripts\python.exe -c "from src.ui.app import crear_interfaz; crear_interfaz().launch()"`
2. Completar los campos del formulario con valores válidos (ej. largo=100, ancho=60, alto=40).
3. Hacer click en **Generar**.
4. **Resultado esperado**: el botón se bloquea (gris, no clickeable) mientras el sólido se construye.
5. Al terminar, el botón vuelve a estar activo y el campo "Resultado" muestra las rutas generadas.

---

## Conflicto de overwrite (FR-010b)

**Validar manualmente** (no hay test automatizado para la interacción UI):
1. Generar el prisma rectangular → carpeta creada en workspace.
2. Generar el mismo prisma rectangular nuevamente.
3. **Resultado esperado**: la app muestra un diálogo de confirmación antes de sobreescribir.
4. Cancelar → carpeta original intacta.
5. Confirmar → carpeta sobreescrita con nuevos archivos.

---

## Indicador de generación (FR-012)

**Validar manualmente** (interacción UI):
1. Iniciar generación de cualquier figura desde el formulario.
2. **Resultado esperado**: mientras CadQuery calcula, la interfaz muestra "Generando…" y
   el botón "Generar" queda deshabilitado.
3. Al terminar, el indicador desaparece y se muestran las rutas de los archivos.
