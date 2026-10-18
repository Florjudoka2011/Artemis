<!--
SYNC IMPACT REPORT (remove before committing)
=============================================
Version change: [placeholder] → 1.0.0
Added sections:
  - Core Principles (I–VI, all new)
  - Stack y Entorno
  - Flujo de Desarrollo
  - Governance
Modified principles: none (initial population)
Removed sections: none
TODOs deferred:
  - PROJECT_NAME: nombre definitivo no definido (docs/00-idea.md §21); se mantiene como TODO
  - RATIFICATION_DATE: primera constitución; se usa la fecha de hoy (2026-10-18)
-->

# Artemis — Constitution

## Core Principles

### I. Los principios no se negocian

Esta constitución rige sobre cualquier otra práctica del proyecto. Sus principios son
no-negociables: no pueden suspenderse por urgencia, conveniencia ni preferencia de turno.
Toda decisión de diseño, implementación o deuda técnica DEBE ser compatible con los
principios aquí enunciados. Las excepciones DEBEN documentarse como ADR con justificación
explícita y aprobación consciente, no como omisión silenciosa.

### II. La IA interpreta, el código calcula

La IA traduce el pedido del docente (texto y/o imagen) a un JSON estructurado validado por
Pydantic. Toda la geometría, proyecciones, cotas y cálculos los realiza **siempre** código
determinista. La IA NUNCA ejecuta código, NUNCA produce geometría directamente, y su única
salida posible al resto del sistema es ese JSON validado. Consecuencias:

- El conector de IA es intercambiable (GPU ROCm → Vulkan → CPU → API externa) sin tocar
  el núcleo del sistema.
- Si la IA falla o produce un JSON inválido, el sistema rechaza limpiamente; el docente
  completa el formulario a mano.
- "La IA alucinó medidas" NUNCA es un bug de producción: Pydantic rechaza, la receta
  rechaza, el docente corrige.

### III. Las recetas se construyen primero, con tests

Las recetas paramétricas son el núcleo del proyecto. Se construyen y testean **antes** que
la interfaz, el pipeline de exportación y la integración de IA. El orden es innegociable:

```
receta → test verde → siguiente receta → ... → interfaz → IA
```

- Cada receta es una función Python pura: parámetros → sólido CadQuery.
- La validación geométrica (coherencia de medidas) ocurre **dentro** de cada receta.
- Ninguna receta se considera terminada sin al menos: un test nominal, un test de borde
  en el límite exacto del rechazo, y un test de parámetro inválido (ver arnés A-06).
- TDD OBLIGATORIO para recetas: el test se escribe primero; el test falla; luego se
  implementa la receta.

### IV. Todo local

La aplicación corre exclusivamente en `127.0.0.1`. No hay exposición de red, no hay acceso
remoto, no hay multiusuario, no hay sincronización en la nube. En Fase 1:

- El modelo de IA corre localmente (Ollama / LM Studio).
- El workspace NO puede estar bajo OneDrive ni en rutas con espacios o tildes.
- La app no hace peticiones salientes durante el uso normal.

Escalar a más usuarios o API externa es decisión explícita de una fase posterior; no se
anticipan abstracciones para ello ahora.

### V. Todo trazable

Cada requisito DEBE tener al menos una tarea asociada y al menos un test que lo verifique.
La matriz `docs/trazabilidad.md` (requisito → tarea → test) se genera con script, no a
mano (regla A-03). Además:

- Cada pedido genera un log JSON: `pedido → interpretación → correcciones → resultado`.
  El log NO guarda imágenes (solo nombre y hash).
- Cada librería y modelo tiene entrada en `docs/fuentes.md` (link, versión, licencia).
- Cada decisión arquitectural importante tiene su ADR en `docs/ADR/`.
- Sin trazabilidad no hay entrega: un requisito sin test no es un requisito terminado.

### VI. El arnés anti-mentiras

Los tests DEBEN verificar algo real. Las reglas A-01–A-09 (definidas en
`docs/tests-fase1.md`) son ley:

- Cada test tiene ID único `T-XX` en su docstring (A-01).
- Cada test referencia el requisito `R-XX` que verifica (A-02).
- Ningún test importa ni llama a la IA real; todos los tests del núcleo son deterministas
  (A-07).
- Un test que pasa sin assertions explícitos FALLA en CI (A-08).
- Tests de mutación con `mutmut` sobre las recetas antes de cerrar Fase 1 (A-09).

"El test pasa" no es evidencia suficiente. La evidencia mínima es la salida de
`pytest --tb=short -v --cov=src --cov-report=term-missing` guardada en
`docs/evidencia/fase1/`.

## Stack y Entorno

El stack es fijo para Fase 1. No se introducen dependencias sin actualizar `docs/fuentes.md`
y verificar compatibilidad en el entorno de la Tarea 0:

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.11+ |
| Validación de esquemas | Pydantic (`extra="forbid"`) |
| Modelado 3D | CadQuery + cq_gears (Fase 1B+) |
| Interfaz | Gradio (reemplazable si el visor 3D no es suficiente) |
| Modelo de IA | Multimodal local — elegido en Tarea 0, registrado en ADR-001 |
| Runtime IA | Ollama (primera opción) / LM Studio (alternativa Vulkan) |
| Tests | pytest + cobertura + mutmut |
| Linting | ruff (reglas S307 y S102 habilitadas: prohibe `eval` y `exec` en `src/`) |
| Seguridad de commits | pre-commit + gitleaks |
| CI | GitHub Actions |

Hardware de referencia: AMD Ryzen 7 5700 / 32 GB RAM / AMD RX 6700 XT / Windows 11.
La Tarea 0 DEBE completarse y registrarse antes de escribir código de producción.

## Flujo de Desarrollo

El orden de construcción es innegociable (deriva del Principio III):

1. **Tarea 0** — validar entorno completo (GPU+ROCm, Vulkan, CPU fallback, stack Python,
   conversión SVG, workspace). Registrar en ADR.
2. **Recetas Fase 1A** — figuras geométricas básicas con sus tests. MVP primero (prisma
   rectangular + cilindro + agujero + vistas IRAM + exportación).
3. **Validación Pydantic** — esquemas de entrada con tests T-100–T-108.
4. **Exportación** — STL, STEP, SVG, conversión PNG/JPG/WebP con tests T-110–T-115.
5. **Representaciones** — invariantes IRAM, Monge, isométrica con tests T-120–T-141.
6. **Interfaz Gradio** — formulario, visor 3D, historial.
7. **Conector de IA** — integración del modelo elegido en Tarea 0.
8. **Recetas Fase 1B** — piezas mecánicas (eje → polea → riel → engranaje).

Ningún paso posterior se inicia si el anterior no tiene tests verdes y trazabilidad
completa.

## Governance

Esta constitución es el documento rector del proyecto. Toda práctica de desarrollo DEBE
ser compatible con ella.

**Enmiendas**: toda modificación a esta constitución DEBE:
1. Registrarse como nueva versión con bump semántico (MAJOR/MINOR/PATCH).
2. Incluir justificación explícita en el Sync Impact Report del PR.
3. Actualizar `docs/ADR/` si la enmienda implica una decisión arquitectural.

**Versionado semántico**:
- MAJOR: eliminación o redefinición incompatible de un principio.
- MINOR: principio nuevo o sección materialmente expandida.
- PATCH: clarificaciones, redacción, correcciones tipográficas.

**Cumplimiento**: cada PR DEBE verificar que los cambios son compatibles con los principios.
El CI ejecuta los tests con el arnés anti-mentiras; un PR con tests rojos no se fusiona.

**Referencia de desarrollo**: `docs/tests-fase1.md` contiene el catálogo de tests e
invariantes. `docs/trazabilidad.md` contiene la matriz requisito → tarea → test.

**Version**: 1.0.0 | **Ratified**: 2026-10-18 | **Last Amended**: 2026-10-18
