# Tasks: Artemis — MVP Modelo 3D desde Formulario

**Input**: Design documents from `specs/001-mvp-modelo-formulario/`

**Prerequisites**: plan.md ✅ spec.md ✅ research.md ✅ data-model.md ✅ contracts/ ✅ quickstart.md ✅

**TDD**: Tests incluidos y obligatorios por Constitución Principio III — cada receta se escribe
DESPUÉS de que su test falle. Orden fijo: test rojo → implementación → test verde.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede correr en paralelo (archivos distintos, sin dependencias incompletas)
- **[Story]**: A qué user story pertenece la tarea
- Cada tarea incluye la ruta exacta del archivo

---

## Phase 0: Tarea 0 — Validación de Entorno ⚠️ BLOQUEANTE

**Purpose**: Validar el entorno completo antes de escribir una sola línea de código de producción.
Resultado de cada ítem registrado en `docs/ADR/001-entorno.md`.

**⚠️ CRÍTICO**: Nada del resto del proyecto puede comenzar hasta que esta fase esté completa
y sus resultados estén registrados.

- [X] T001 Validar que Python 3.11 + CadQuery + Gradio funcionan juntos en Windows 11 sin conflictos de versiones — registrar versiones exactas en docs/ADR/001-entorno.md
- [X] T002 [P] Validar que cairosvg (o alternativa: svglib+reportlab) convierte SVG a PNG en Windows 11 sin DLLs externas problemáticas — registrar decisión en docs/ADR/001-entorno.md
- [X] T003 [P] Confirmar ruta de workspace (ej. C:\Artemis\) fuera de OneDrive, sin espacios ni tildes, con permisos de escritura — registrar en docs/ADR/001-entorno.md
- [X] T004 Consolidar todos los resultados de Tarea 0 en docs/ADR/001-entorno.md con: versiones confirmadas, librería SVG→PNG elegida, ruta workspace, resultado de cada ítem validado

**Checkpoint**: Tarea 0 completa — entorno validado, ADR escrito. Recién ahora comienza el desarrollo.

---

## Phase 1: Setup — Infraestructura del Proyecto

**Purpose**: Estructura de directorios, herramientas y configuración base.

- [X] T005 Crear estructura de directorios completa según plan.md: src/recipes/, src/schemas/, src/export/, src/views_iram/, src/ui/, tests/unit/, tests/integration/, tests/e2e/, docs/evidencia/fase1/, docs/ADR/
- [X] T006 Crear pyproject.toml con Python 3.12, CadQuery, Pydantic v2, Gradio, skia-python, pytest, pytest-cov, mutmut; incluir markers `mvp` y `perf` en `[tool.pytest.ini_options]`
- [X] T007 [P] Configurar ruff en pyproject.toml con reglas S307 (eval) y S102 (exec) habilitadas para src/
- [X] T008 [P] Configurar pre-commit + gitleaks en .pre-commit-config.yaml; completar .gitignore
- [X] T009 Crear __init__.py en src/ y todos sus subdirectorios (recipes, schemas, export, views_iram, ui)
- [X] T010 Crear tests/conftest.py con fixture `workspace_tmp` que crea y limpia un directorio temporal para cada test de exportación
- [X] T010b [P] Crear .github/workflows/ci.yml: ejecutar `pytest -m mvp --tb=short -v` en Python 3.12 en Ubuntu (para CI); marker `perf` excluido de CI via `addopts`
- [X] T010c [P] Escribir scripts/gen_traceability.py: leer docstrings de tests/ buscando patrón `T-XX | 001/FR-XX`, generar docs/trazabilidad.md con columnas Test ID | Feature ID | Archivo | Función

**Checkpoint**: Setup completo — `python -m pytest --collect-only` no da errores de importación; `gh workflow list` muestra ci.yml.

---

## Phase 2: Foundational — Schemas Pydantic + Protocolo de Receta

**Purpose**: Capa de validación de entrada que BLOQUEA el inicio de cualquier user story.

**⚠️ CRÍTICO**: Sin schemas validados, ninguna receta puede recibir parámetros seguros.

### Tests Foundational (escribir PRIMERO — deben FALLAR antes de implementar)

- [X] T011 Escribir tests T-100 a T-108 en tests/unit/test_schemas.py: JSON válido completo, campo faltante, tipo incorrecto, valor negativo, NaN/inf, valor=0, campo extra (extra="forbid"), figura desconocida, cara desconocida — docstring de cada test: `T-1XX | 001/FR-005` — verificar que FALLAN antes de implementar

### Implementación Foundational

- [X] T012 Implementar src/schemas/figuras.py: FiguraTipo, CaraAgujero, AgujeroParams, PrismaRectangularParams, CilindroParams — todos con `extra="forbid"`, validators > 0 — hasta que T-100 a T-108 pasen
- [X] T013 [P] Implementar src/recipes/base.py con protocolo Receta (Protocol): firma `__call__(params: BaseModel) -> cq.Workplane`, docstring con contrato de comportamiento

**Checkpoint**: `pytest tests/unit/test_schemas.py -v` — T-100 a T-108 todos verdes.

---

## Phase 3: User Story 1 — Modelo 3D básico desde formulario (Priority: P1) 🎯 MVP

**Goal**: La docente ingresa medidas en el formulario y obtiene archivos STL y STEP en el workspace.
Sin agujero, sin vistas. Generación < 10 s con indicador "Generando…".

**Independent Test**: `pytest -m mvp tests/unit/test_recipes_prisma.py tests/unit/test_recipes_cilindro.py tests/integration/test_export.py tests/e2e/test_formulario.py -v`

### Tests US1 (escribir PRIMERO — deben FALLAR antes de implementar)

- [ ] T014 [P] [US1] Escribir tests T-01, T-02, T-03 en tests/unit/test_recipes_prisma.py: nominal (largo=100,ancho=60,alto=40 → volumen=240000 mm³ isclose rel_tol=1e-6), parámetro=0, parámetro negativo — marcar `@pytest.mark.mvp`; docstrings `T-01 | 001/FR-004`, `T-02 | 001/FR-005`, `T-03 | 001/FR-005`
- [ ] T015 [P] [US1] Escribir test T-10 en tests/unit/test_recipes_cilindro.py: nominal (diámetro=50,alto=80 → volumen=157079.633 mm³ isclose rel_tol=1e-6) — marcar `@pytest.mark.mvp`; docstring `T-10 | 001/FR-004`
- [ ] T016 [P] [US1] Escribir tests T-110, T-111 en tests/integration/test_export.py: STL genera archivo > 0 bytes con volumen dentro de ±0.5% del teórico; STEP genera archivo > 0 bytes — marcar `@pytest.mark.mvp`; docstrings `T-110 | 001/FR-006`, `T-111 | 001/FR-006`
- [ ] T017 [P] [US1] Escribir tests T-150, T-151, T-152 en tests/e2e/test_formulario.py usando conector falso (fixture que devuelve JSON fijo): T-150 mismo hash STL; T-151 campo vacío lista faltantes; T-152 IA deshabilitada arranca vacío — marcar `@pytest.mark.mvp`; docstrings `T-150 | 001/FR-009`, `T-151 | 001/FR-001 | 001/FR-005`, `T-152 | 001/FR-009`

### Implementación US1

- [ ] T018 [P] [US1] Implementar src/recipes/prisma_rectangular.py::construir (base sin agujero): validar parámetros > 0 antes de CadQuery, construir `cq.Workplane("XY").box(largo, ancho, alto)` — hasta que T-01, T-02, T-03 pasen
- [ ] T019 [P] [US1] Implementar src/recipes/cilindro.py::construir (base sin agujero): validar parámetros > 0 antes de CadQuery, construir `cq.Workplane("XY").cylinder(alto, diametro/2)` — hasta que T-10 pase
- [ ] T020 [US1] Implementar src/export/solid.py: funciones `exportar_stl(solid, path)` y `exportar_step(solid, path)` usando `cadquery.exporters.export()` — hasta que T-110, T-111 pasen
- [ ] T021 [US1] Implementar src/ui/workspace.py: generar nombre de carpeta `<figura>_<YYYYMMDD_HHMMSS>` (solo `[a-z0-9_]`), crear carpeta, detectar si ya existe y retornar flag para confirmación (FR-010, FR-010b)
- [ ] T022 [US1] Implementar src/ui/app.py (formulario Gradio básico): selector de figura (prisma_rectangular | cilindro), campos de medidas, botón "Generar" con estado de carga "Generando…" bloqueante (FR-001, FR-012), diálogo de confirmación de overwrite (FR-010b), panel de resultado con rutas de archivos (FR-011) — hasta que T-150, T-151, T-152 pasen

**Checkpoint**: `pytest -m mvp -k "prisma or cilindro or export or formulario" -v` — todos verdes.
Validar manualmente: abrir app, generar prisma rectangular, verificar archivos en workspace.

---

## Phase 4: User Story 2 — Agujero pasante (Priority: P2)

**Goal**: La docente agrega un agujero pasante al prisma rectangular o cilindro, con validación
de parámetros inválidos antes de construir.

**Independent Test**: `pytest tests/unit/test_recipes_prisma.py tests/unit/test_recipes_cilindro.py -k "agujero" -v`

### Tests US2 (escribir PRIMERO — deben FALLAR antes de implementar)

- [ ] T023 [P] [US2] Escribir tests T-04, T-05, T-09 en tests/unit/test_recipes_prisma.py: T-04 agujero pasante centrado (d=20 → volumen=227433.629 mm³ isclose rel_tol=1e-6); T-05 diámetro=40 en ancho=40 → ValueError antes de construir; T-09 offset_x=50 sale de cara → ValueError — docstrings `T-04 | 001/FR-002`, `T-05 | 001/FR-005`, `T-09 | 001/FR-005`
- [ ] T024 [P] [US2] Escribir tests T-11, T-12 en tests/unit/test_recipes_cilindro.py: T-11 agujero coaxial pasante (d_agujero=20 → volumen=131946.891 mm³ isclose rel_tol=1e-6); T-12 d_agujero=50 en cilindro d=50 → ValueError — docstrings `T-11 | 001/FR-002`, `T-12 | 001/FR-005`

### Implementación US2

- [ ] T025 [P] [US2] Extender src/recipes/prisma_rectangular.py::construir con operación de agujero: validar `diametro < lado_menor(cara)`, validar que el círculo `(offset_x, offset_y, radio)` cabe en la cara, aplicar `.faces().workplane().center(offset_x, offset_y).hole(diametro)` — hasta que T-04, T-05, T-09 pasen
- [ ] T026 [P] [US2] Extender src/recipes/cilindro.py::construir con agujero coaxial: validar que cara es superior o inferior, validar `diametro_agujero < diametro_cilindro`, aplicar `.faces().workplane().hole(diametro_agujero)` — hasta que T-11, T-12 pasen
- [ ] T027 [US2] Agregar sección de agujero al formulario en src/ui/app.py: campos diámetro, cara (enum), offset_x/Y (opcionales, default 0) visibles solo cuando la figura lo admite (FR-002)

**Checkpoint**: `pytest tests/unit/test_recipes_prisma.py tests/unit/test_recipes_cilindro.py -v` — todos verdes incluyendo agujero.

---

## Phase 5: User Story 3 — Vistas IRAM → SVG + PNG (Priority: P3)

**Goal**: La docente activa "vistas IRAM" y recibe además de STL/STEP un SVG con planta/alzado/perfil
en disposición normalizada ISO E, exportable también como PNG.

**Independent Test**: `pytest tests/integration/test_views_iram.py tests/integration/test_export.py -k "svg or png or iram" -v`

### Tests US3 (escribir PRIMERO — deben FALLAR antes de implementar)

- [ ] T028 [P] [US3] Escribir tests T-120 a T-124 en tests/integration/test_views_iram.py: para prisma (100×60×40) verificar en el SVG compuesto — T-120 planta debajo del alzado; T-121 perfil a la derecha; T-122 ancho X alzado=planta ±0.001; T-123 altura Z alzado=perfil ±0.001; T-124 profundidad Y planta=perfil ±0.001 — marcar `@pytest.mark.mvp`; docstrings `T-12X | 001/FR-007`
- [ ] T029 [P] [US3] Escribir tests T-112, T-113 en tests/integration/test_export.py: T-112 SVG de vistas existe y tamaño > 0; T-113 PNG convertido desde SVG es válido con dimensiones > 0 — marcar `@pytest.mark.mvp`; docstrings `T-112 | 001/FR-007`, `T-113 | 001/FR-008`

### Implementación US3

- [ ] T030 [US3] Implementar src/views_iram/generator.py: generar tres proyecciones ortogonales (alzado dirección Y−, planta dirección Z−, perfil dirección X−) usando `cadquery.exporters.export(..., exportType="SVG")`, componer en SVG único con offsets ISO E (planta debajo del alzado, perfil a la derecha) — hasta que T-120 a T-124 pasen
- [ ] T031 [US3] Implementar src/export/views.py: `exportar_svg(vistas_svg, path)` y `svg_a_png(svg_path, png_path)` usando la librería validada en T002 — hasta que T-112, T-113 pasen
- [ ] T032 [US3] Agregar opción "vistas IRAM" al formulario en src/ui/app.py (checkbox; si marcado: generar y mostrar rutas SVG y PNG en panel de resultado — FR-003, FR-007, FR-008)

**Checkpoint**: `pytest -m mvp -v` — todos los tests del MVP verdes (T-01 a T-05 y T-10 a T-12, T-100 a T-108, T-110 a T-113, T-120 a T-124, T-150 a T-152).

---

## Phase 6: Polish & Arnés Anti-Mentiras

**Purpose**: Cierre del MVP con evidencia verificable y trazabilidad completa.

- [X] T037 [P] Guardar script de mutación manual en scripts/mutacion_manual.py con docstring — reproducir M2 survivor y guardar evidencia en docs/evidencia/fase1/mutacion-schemas-antes.txt y mutacion-schemas-despues.txt
- [X] T038 [P] Escribir test T-109 en tests/unit/test_pydantic_nan_behavior.py: verificar que Pydantic v2 acepta NaN e inf sin validator explícito — documenta por qué math.isfinite() es necesario — docstring `T-109 | 001/FR-005`
- [X] T039 [P] Crear scripts/evidencia.py: ejecuta pytest + cobertura + mutación + trazabilidad, guarda salidas en docs/evidencia/fase1/ con timestamp AAAA-MM-DD_HHMM_tipo.txt
- [X] T040 [P] Agregar hook gen-traceability a .pre-commit-config.yaml; actualizar .github/workflows/ci.yml con mutmut y artefactos
- [X] T041 Crear CLAUDE.md con reglas del arnés anti-mentiras: ejecutar evidencia.py antes de marcar tarea completa; nunca afirmar tests pasan sin output real; TDD estricto; no afirmar comportamiento de librerías sin test/doc
- [ ] T033 [P] Escribir test de rendimiento T-SC001 en tests/unit/test_recipes_prisma.py: verificar que construir prisma (100×60×40) + exportar STL completa en < 10 s (SC-001); marcar `@pytest.mark.perf` (excluido de CI; ejecutar manualmente con `pytest -m perf -v`) — docstring `T-SC001 | 001/SC-001`
- [ ] T033b [P] Ejecutar suite completa del MVP y guardar evidencia en docs/evidencia/fase1/: `pytest -m mvp --tb=short -v --cov=src --cov-report=term-missing` — cobertura de src/recipes/ y src/schemas/ al 100%
- [ ] T034 [P] Ejecutar tests de mutación sobre recetas: `mutmut run --paths-to-mutate src/recipes/`; documentar supervivientes en docs/evidencia/fase1/mutmut-YYYYMMDD.txt; supervivientes = 0 para considerar las recetas terminadas
- [ ] T035 Generar matriz trazabilidad docs/trazabilidad.md con script (requisito R-XX → tarea T-XXX → test T-XX); verificar que no hay requisitos sin test
- [ ] T036 [P] Verificar que ruff no reporta eval/exec en src/: `ruff check src/ --select S307,S102` debe salir con código 0

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 0 (Tarea 0)**: Sin dependencias — comenzar inmediatamente. **BLOQUEA todo lo demás.**
- **Phase 1 (Setup)**: Depende de Phase 0 completa.
- **Phase 2 (Foundational)**: Depende de Phase 1 completa. **BLOQUEA todas las US.**
- **Phase 3 (US1)**: Depende de Phase 2 completa.
- **Phase 4 (US2)**: Depende de Phase 3 completa (agujero extiende las recetas de US1).
- **Phase 5 (US3)**: Depende de Phase 3 completa (vistas usan el sólido de US1).
- **Phase 6 (Polish)**: Depende de Phase 3 + Phase 4 + Phase 5 completas.

### User Story Dependencies

- **US1 (P1)**: Bloquea US2 (agujero extiende recetas) y US3 (vistas usan el sólido).
- **US2 (P2)**: Puede trabajarse en paralelo con US3 una vez US1 esté completa.
- **US3 (P3)**: Puede trabajarse en paralelo con US2 una vez US1 esté completa.

### Dentro de cada User Story (TDD obligatorio)

```
Tests (escribir) → Tests FALLAN → Implementación → Tests PASAN → siguiente tarea
```

---

## Parallel Example: Phase 3 (US1)

```bash
# Tests: T014, T015, T016, T017 pueden escribirse en paralelo (archivos distintos)
T014: tests/unit/test_recipes_prisma.py    # T-01, T-02, T-03
T015: tests/unit/test_recipes_cilindro.py  # T-10
T016: tests/integration/test_export.py     # T-110, T-111
T017: tests/e2e/test_formulario.py         # T-150, T-151, T-152

# Implementaciones: T018, T019 en paralelo (archivos distintos, ambos fallan hasta acá)
T018: src/recipes/prisma_rectangular.py
T019: src/recipes/cilindro.py

# T020, T021 en secuencia (T020 usa sólidos de T018/T019; T021 prepara workspace para T022)
T020: src/export/solid.py
T021: src/ui/workspace.py
T022: src/ui/app.py  (integra todo)
```

---

## Implementation Strategy

### MVP mínimo demostrable (solo US1)

1. Completar Phase 0 (Tarea 0) ← **obligatorio siempre primero**
2. Completar Phase 1 (Setup)
3. Completar Phase 2 (Foundational — schemas)
4. Completar Phase 3 (US1 — prisma + cilindro + exportación + formulario)
5. **STOP y VALIDAR**: `pytest -m mvp -k "not iram and not agujero" -v` + abrir app manualmente
6. Demostrar MVP: formulario → prisma rectangular → STL + STEP en workspace

### Entrega incremental completa

```
Phase 0 → Phase 1 → Phase 2 → Phase 3 (MVP!) → Phase 4 → Phase 5 → Phase 6
```

Cada checkpoint es un estado demostrable y testeable de forma independiente.
