# ADR 002 — Servidor MCP de trazabilidad (artemis-trazabilidad)

**Estado**: Aceptado
**Fecha**: 2026-10-20
**Autores**: Diego Saavedra

---

## Contexto

El proyecto Artemis tiene un arnés anti-mentiras que exige que toda afirmación técnica
sea respaldada por evidencia real (tests ejecutados, líneas de código citadas, archivos
concretos). Sin embargo, cuando una IA asiste en el desarrollo, tiende a responder desde
su contexto sin verificar el estado real del repositorio, generando afirmaciones que pueden
quedar desactualizadas o directamente ser incorrectas.

Se necesita un mecanismo que permita a la IA consultar el estado real del repositorio —
qué tests existen, qué requisitos cubren, cuál fue la última evidencia, qué huecos hay —
sin que esa consulta ejecute código arbitrario ni modifique nada.

---

## Decisión

Implementar un servidor MCP (Model Context Protocol) propio llamado `artemis-trazabilidad`
que expone 6 herramientas de solo lectura sobre el repositorio:

| Herramienta | Descripción |
|-------------|-------------|
| `buscar_test` | Localiza un test por su ID (ej: T-100) |
| `funcion_bajo_test` | Devuelve el código de la función que un test ejercita |
| `requisito` | Devuelve el texto de un requisito y los tests que lo cubren |
| `estado_tareas` | Lista tareas completadas y pendientes de tasks.md |
| `ultima_evidencia` | Devuelve el contenido del último archivo de evidencia |
| `huecos_trazabilidad` | Identifica requisitos sin tests y tests sin requisito |

El servidor vive en `mcp/artemis_trazabilidad/` y se registra en `.mcp.json`.
Usa el SDK oficial `mcp 2.3.0` con transporte `stdio`.

---

## Alternativas consideradas

### 1. Responder desde contexto (sin MCP)
La IA lee los archivos relevantes al inicio de cada sesión.
**Descartado**: el contexto se vuelve stale rápidamente; no hay forma de verificar que
lo que la IA "recuerda" refleja el estado actual del repo.

### 2. Scripts Python ad-hoc
Ejecutar scripts bajo demanda y leer su salida.
**Descartado**: requiere que el usuario los invoque manualmente; no permite que la IA
consulte en tiempo real durante una conversación.

### 3. Base de datos de trazabilidad (ej: SQLite)
Mantener una BD sincronizada con el repositorio.
**Descartado**: añade complejidad de sincronización; el repositorio ya es la fuente de
verdad; parsear en tiempo real es suficientemente rápido para este tamaño de proyecto.

---

## Consecuencias

### Positivas
- La IA puede citar `archivo:línea` en lugar de hacer afirmaciones desde memoria.
- Las 6 herramientas son de solo lectura: no pueden modificar el repositorio.
- El análisis usa `ast.parse()` en lugar de `import`: no ejecuta código del proyecto.
- Testeable sin levantar el servidor MCP (las funciones son puras, reciben `repo_root`).

### Negativas / limitaciones
- El directorio `mcp/` debe estar en `sys.path` para evitar colisión de nombres con el
  paquete instalado `mcp`. Se resuelve en `tests/conftest.py`.
- Las herramientas analizan el repositorio en tiempo real: si el repo es muy grande,
  podría haber latencia. Aceptable para el tamaño actual de Artemis.

---

## Implementación

- `mcp_servers/artemis_trazabilidad/tools.py`: funciones puras (sin efectos secundarios)
- `mcp_servers/artemis_trazabilidad/server.py`: envuelve las funciones con decoradores `@mcp.tool()`
- `mcp_servers/artemis_trazabilidad/__init__.py`: vacío (marca el paquete)
- `tests/unit/test_mcp_trazabilidad.py`: tests T-200 a T-222, todos `@pytest.mark.mvp`
- `tests/fixtures/repo_ejemplo/`: fixture con contenido conocido para tests deterministas
  - IDs en rango **T-9XX** para distinguirlos de tests reales (T-1XX a T-2XX)
- `.mcp.json`: registro del servidor para Claude Code

---

## Requisitos del MCP (`mcp/FR-XX`)

Los tests de este servidor usan el espacio de nombres `mcp/FR-XX`, separado de la
spec principal `001/FR-XX`. Esto evita falsos positivos en `huecos_trazabilidad()`.

| ID | Requisito |
|----|-----------|
| `mcp/FR-001` | El servidor puede importarse sin instancia MCP activa |
| `mcp/FR-002` | `buscar_test` localiza un test por T-ID y devuelve archivo y línea |
| `mcp/FR-003` | `funcion_bajo_test` devuelve el código de la función/clase bajo test |
| `mcp/FR-004` | `requisito` devuelve texto del requisito y tests que lo cubren |
| `mcp/FR-005` | `estado_tareas` clasifica tareas en hechas y pendientes |
| `mcp/FR-006` | `ultima_evidencia` devuelve el archivo de evidencia más reciente |
| `mcp/FR-007` | `huecos_trazabilidad` detecta brechas de cobertura y IDs duplicados |
| `mcp/FR-008` | El MCP excluye `tests/fixtures/` del recorrido para evitar contaminación |

### Exclusión de fixtures

`_iter_py_files()` acepta un parámetro `exclude_dirs` (default: `{"tests/fixtures"}`).
Esto evita que los tests del fixture de prueba sean tratados como tests reales del proyecto.
Configurable por llamada; el comportamiento por defecto protege el repositorio Artemis.

---

## Referencias

- [Model Context Protocol — Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [ADR 001 — Decisiones de entorno](./001-entorno.md)
- [CLAUDE.md — Arnés anti-mentiras](../../CLAUDE.md)
