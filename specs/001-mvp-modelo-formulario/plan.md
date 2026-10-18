# Implementation Plan: Artemis — MVP Modelo 3D desde Formulario

**Branch**: `001-mvp-modelo-formulario` | **Date**: 2026-10-18 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-mvp-modelo-formulario/spec.md`

## Summary

La docente completa un formulario (prisma rectangular o cilindro, con agujero pasante
opcional y opción de vistas IRAM), presiona "Generar", y obtiene archivos STL, STEP y
opcionalmente SVG/PNG en el workspace local. Sin IA activa. Recetas paramétricas
deterministas. Validación Pydantic de entrada. TDD estricto: test primero, luego receta.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: CadQuery (modelado 3D), Pydantic v2 (validación de esquemas),
Gradio (interfaz), pytest + pytest-cov + mutmut (tests), ruff (linting con S307/S102)

**Storage**: Sistema de archivos local — workspace configurable en ruta sin espacios ni
tildes, fuera de OneDrive. Una subcarpeta por generación: `<figura>_<YYYYMMDD_HHMMSS>`.

**Testing**: pytest; markers `@pytest.mark.mvp` para el subconjunto del MVP; cobertura con
`--cov=src --cov-report=term-missing`; evidencia guardada en `docs/evidencia/fase1/`

**Target Platform**: Windows 11, escritorio local, solo 127.0.0.1

**Project Type**: desktop-app (Gradio como servidor local, acceso solo desde localhost)

**Performance Goals**: generación CadQuery en < 10 segundos para las figuras del MVP

**Constraints**: sin `eval` / `exec` en `src/`; rutas de salida sin caracteres especiales;
sin exposición de red; workspace no bajo OneDrive

**Scale/Scope**: 1 usuario, 1 PC; volumen de figuras: prisma rectangular + cilindro en
MVP; catálogo completo en Fase 1A

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Estado | Notas |
|---|---|---|
| I. Los principios no se negocian | ✅ | Plan respeta todos los principios |
| II. La IA interpreta, el código calcula | ✅ | MVP sin IA; formulario → Pydantic → receta → exportación; ningún componente genera geometría de forma no-determinista |
| III. Recetas primero, con tests | ✅ GATE | **Orden de implementación obligatorio**: receta → test rojo → test verde → siguiente. Ninguna receta se entrega sin sus tests del arnés. Ver tasks.md para el orden. |
| IV. Todo local | ✅ | Sin red; workspace local; Gradio en 127.0.0.1 |
| V. Todo trazable | ✅ | Cada test referencia R-XX; matriz generada por script; ver `docs/trazabilidad.md` |
| VI. El arnés anti-mentiras | ✅ GATE | Tests T-01 a T-17, T-100 a T-108, T-110 a T-113, T-120 a T-124, T-150 a T-152 DEBEN pasar antes de considerar MVP completo; cada test con ID T-XX y R-XX en docstring |

**Violaciones**: ninguna.

## Project Structure

### Documentation (this feature)

```text
specs/001-mvp-modelo-formulario/
├── plan.md              # Este archivo
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── schema-figura.md
│   └── recipe-contract.md
└── tasks.md             # Phase 2 output (/speckit-tasks — no creado aún)
```

### Source Code (repository root)

```text
src/
├── recipes/
│   ├── __init__.py
│   ├── base.py              # clase base / protocolo de receta
│   ├── prisma_rectangular.py
│   └── cilindro.py
├── schemas/
│   ├── __init__.py
│   └── figuras.py           # modelos Pydantic de entrada
├── export/
│   ├── __init__.py
│   ├── solid.py             # STL y STEP desde sólido CadQuery
│   └── views.py             # SVG → PNG/JPG/WebP
├── views_iram/
│   ├── __init__.py
│   └── generator.py         # proyecciones IRAM desde sólido CadQuery
└── ui/
    ├── __init__.py
    └── app.py               # Gradio: formulario, estado de generación, resultado

tests/
├── conftest.py
├── unit/
│   ├── test_recipes_prisma.py    # T-01 a T-09 (MVP: T-01 a T-05)
│   ├── test_recipes_cilindro.py  # T-10 a T-14 (MVP: T-10 a T-12)
│   └── test_schemas.py           # T-100 a T-108
├── integration/
│   ├── test_export.py            # T-110 a T-115
│   └── test_views_iram.py        # T-120 a T-124
└── e2e/
    └── test_formulario.py        # T-150 a T-152

docs/
├── evidencia/fase1/              # salida de pytest --tb=short -v
├── ADR/
│   ├── 001-entorno.md            # (Tarea 0 — validación de entorno; MVP)
│   └── 001-modelo-ia.md          # (Fase 1 completa — elección del modelo de IA)
└── trazabilidad.md               # generado por script
```

**Structure Decision**: single-project. `src/` contiene el núcleo desacoplado de la
interfaz (recipes, schemas, export, views_iram son independientes de Gradio). `ui/` solo
orquesta. Permite reemplazar Gradio sin tocar el núcleo.

## Complexity Tracking

> Sin violaciones de constitución — sección vacía.
