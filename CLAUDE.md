# CLAUDE.md — Reglas de trabajo para Artemis

Este archivo define reglas no negociables para la IA que asiste en este proyecto.
Se aplican en toda sesión, sin excepción.

---

## Reglas del arnés anti-mentiras

### 1. Evidencia antes de cerrar una tarea

Antes de marcar una tarea como completada (`[X]` en tasks.md), ejecutar:

```
.venv\Scripts\python.exe scripts/evidencia.py
```

Verificar que no haya fallos. Si alguna etapa falla, la tarea NO está completa.

### 2. Nunca afirmar que los tests pasan sin haberlos ejecutado

Toda afirmación de la forma "los tests pasan", "16/16 passed", "0 fallos" debe ir
acompañada de la salida real del comando. Citar el número de tests, la línea de resumen
(`N passed in X.XXs`) y la fecha/hora de ejecución.

### 3. Tests antes que implementación (TDD estricto)

El orden es fijo e innegociable:
1. Escribir el test → confirmarlo en ROJO (falla con ImportError o AssertionError)
2. Commitear los tests en rojo
3. Implementar hasta que el test pase
4. Commitear la implementación con los tests en verde

No existe ninguna circunstancia en que la implementación se escriba antes del test.

### 5. Nunca usar --no-verify

`git commit --no-verify` y `git push --no-verify` están **prohibidos**.

Bypasean todos los hooks (ruff, gitleaks, format, secrets) y destruyen la trazabilidad
del arnés anti-mentiras. No existe circunstancia que lo justifique.

Si un hook falla legítimamente (ej: `no-commit-to-branch` por política de rama),
usar `SKIP=hook-id` para saltear ÚNICAMENTE ese hook nombrado, nunca `--no-verify`.
Documentar el motivo en el mensaje del commit.

### 7. Toda afirmación de "verificado" debe incluir el intérprete y la salida real

Cualquier afirmación de la forma "verificado", "confirmado", "funciona", "instalado" debe ir
acompañada de:
1. El comando exacto ejecutado
2. El intérprete usado: `.venv\Scripts\python --version` (salida real, no desde memoria)
3. La salida real del comando

Ejemplo incorrecto: "CadQuery está instalado y los tests pasan (verificado)."
Ejemplo correcto: "`.venv\Scripts\python.exe -m pytest -m mvp -v` con
`.venv\Scripts\python --version` → `Python 3.12.0` → `77 passed in 10.95s` (2026-10-25 19:50)."

### 8. Una historia de usuario no se cierra sin prueba manual de punta a punta

Antes de declarar una historia de usuario como completa, se debe documentar en la evidencia
una prueba manual de punta a punta que incluya:
1. Versión del intérprete (`.venv\Scripts\python --version`)
2. Pasos ejecutados por el usuario real (no por tests automatizados)
3. Salida observada (capturas de terminal o descripción exacta)
4. Ruta del archivo de evidencia generado

Sin este registro, la historia **no está cerrada**, aunque todos los tests pasen.

### 4. No hacer afirmaciones técnicas sin verificación

No afirmar el comportamiento de ninguna librería (Pydantic, CadQuery, skia-python,
etc.) sin respaldarlo con:
- Un test que lo demuestre (preferido), o
- Una cita directa de la documentación oficial con URL.

Ejemplo incorrecto: "Pydantic rechaza NaN por defecto."
Ejemplo correcto: "Según el test `test_pydantic_v2_acepta_nan_sin_validator`
(tests/unit/test_pydantic_nan_behavior.py), Pydantic v2 acepta NaN sin validator
explícito. Por eso se usa `math.isfinite()` en los schemas."

### 6. Usar herramientas MCP para responder sobre el estado del proyecto

Para responder sobre tests, requisitos o tareas del proyecto, usar las herramientas
del servidor MCP `artemis-trazabilidad` y citar `archivo:línea`.

No afirmar el estado del proyecto desde memoria. Siempre verificar con:
- `buscar_test("T-XXX")` para localizar un test por ID
- `requisito("FR-XXX")` para ver qué tests cubren un requisito
- `estado_tareas()` para ver tareas completadas y pendientes
- `huecos_trazabilidad()` para identificar brechas de cobertura
- `ultima_evidencia()` para ver la última ejecución verificada

Ejemplo incorrecto: "El test T-100 está en la línea 15 de test_schemas.py."
Ejemplo correcto: invocar `buscar_test("T-100")` → citar el `archivo:linea` devuelto.

---

## Stack y decisiones de entorno

Ver `docs/ADR/001-entorno.md` para las decisiones de entorno validadas.

- Python: 3.12.0
- CadQuery: 2.8.0
- Pydantic: v2 (acepta NaN/inf por defecto — usar `math.isfinite()` explícito)
- SVG→PNG: skia-python 144.0 (cairosvg falla en Windows sin libcairo-2.dll)
- Workspace: `C:\Artemis\`

---

## Comandos útiles

```bash
# Correr suite MVP
.venv\Scripts\python.exe -m pytest -m mvp -v

# Correr evidencia completa
.venv\Scripts\python.exe scripts/evidencia.py

# Generar trazabilidad
.venv\Scripts\python.exe scripts/gen_traceability.py

# Mutación manual
.venv\Scripts\python.exe scripts/mutacion_manual.py

# Lint
.venv\Scripts\python.exe -m ruff check src/
```
