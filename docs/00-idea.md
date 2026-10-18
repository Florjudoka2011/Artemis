# Idea de proyecto — Aplicación de modelado 3D para docentes

> Documento generado a partir de sesión de definición — 2026-10-18
> Base para: constitución, especificación, plan y tareas (Spec Kit)

---

## 1. Descripción general

Aplicación de escritorio para docentes de **dibujo técnico** y **educación tecnológica** (Lenguajes Tecnológicos, Sistemas Tecnológicos). El docente describe un objeto por texto y/o imagen de referencia, indica medidas exactas, y la app genera el modelo 3D de la pieza y su representación técnica en el sistema solicitado.

- **Usuario**: una sola docente, en una PC de escritorio. Sin multiusuario ni acceso remoto.
- **Prioridad**: funcional, simple de usar, entregas de calidad profesional.
- **Estética de interfaz**: no es prioridad en esta etapa.

---

## 2. Hardware y entorno

| Componente | Detalle |
|---|---|
| CPU | AMD Ryzen 7 5700 |
| RAM | 32 GB |
| GPU | AMD RX 6700 XT (12 GB VRAM) |
| OS | Windows 11 |
| Acceso | Solo local (127.0.0.1) |
| Inicio | Doble clic en acceso directo (.bat) en el escritorio |

---

## 3. Flujo de uso

```
Entrada (texto + imagen opcional)
        ↓
Panel formulario (pre-completado por IA con lo que pudo extraer, campos vacíos si no alcanza)
  → El docente completa o corrige: tipo de objeto, medidas, sistema de representación
        ↓
Generar (recetas paramétricas deterministas)
        ↓
Paso de exportación (el docente elige formatos)
        ↓
Archivos guardados en workspace
```

### Modos de entrada

| Modo | Comportamiento |
|---|---|
| Texto + imagen | La IA interpreta ambos y pre-completa el formulario |
| Solo texto | La IA pre-completa lo que puede; campos sin datos quedan vacíos para completar manualmente |
| Formulario directo | El docente completa el formulario sin IA |

El panel formulario es único para los tres modos. La IA es una ayuda para completarlo — nunca una dependencia. Si falla o no tiene suficiente información, el docente completa manualmente los campos vacíos.

> **Descartado para Fase 1**: modo entrevista guiada con preguntas una a una. Agrega complejidad sin ser imprescindible. Se evalúa en una fase posterior.

### Imágenes aceptadas

- Foto de objeto real, boceto a mano alzada, captura de pantalla, imagen de internet
- Formatos aceptados (lista cerrada): **JPG, PNG, WebP**
- HEIC (iPhone): fuera del alcance por ahora; se evalúa al escalar a más usuarios
- Límites de seguridad (ver sección 14): tamaño máximo, resolución máxima, verificación de contenido real
- La imagen nunca llega sola: siempre acompaña una descripción textual
- Si la IA no identifica el objeto, pre-completa lo que puede del texto y deja el resto vacío

---

## 4. Arquitectura de decisiones clave

### 4.1 Enfoque paramétrico, no generativo
Las representaciones deben ser exactas. No se usan generadores de imágenes. Todo lo que se muestra es calculado por código determinista.

### 4.2 "La IA interpreta, el código calcula"
La IA traduce el pedido (texto y/o imagen) a un JSON estructurado. Las medidas, proyecciones y cálculos los realiza siempre código determinista. La IA nunca ejecuta código.

### 4.3 Recetas paramétricas — el núcleo del proyecto
Cada tipo de pieza tiene una **receta**: función Python pura que recibe parámetros y devuelve un sólido CadQuery.

```
parámetros → receta → sólido CadQuery → STL / STEP / vistas
```

- Las recetas se construyen y testean **antes que cualquier otra cosa**
- La validación geométrica (coherencia de medidas) ocurre dentro de cada receta
- Son independientes de la IA, la interfaz y el pipeline de exportación

### 4.4 Validación con Pydantic
El JSON generado por la IA se valida con Pydantic antes de construir nada. Si no es válido, se rechaza y se informa. Pydantic valida **estructura**; la receta valida **coherencia geométrica**.

### 4.5 Conector de IA intercambiable
La IA se conecta a través de un conector con interfaz definida. Se puede cambiar de modelo o proveedor (local GPU → local CPU → API externa) sin tocar el resto del sistema.

### 4.6 Lógica separada de la interfaz
La lógica de negocio está desacoplada de Gradio para poder reemplazar la interfaz si el proyecto escala.

---

## 5. Modelo de IA

| Decisión | Detalle |
|---|---|
| Tipo | Un único modelo multimodal (texto + imagen) |
| Candidato inicial | A definir en Tarea 0 (Qwen2-VL u otro disponible al momento) |
| Runtime | Ollama (primera opción) / LM Studio (alternativa) |
| Aceleración principal | GPU AMD RX 6700 XT vía ROCm/HIP |
| Aceleración intermedia | Vulkan (LM Studio lo soporta; opción entre GPU ROCm y CPU puro) |
| Fallback | CPU (con 32 GB RAM) |
| API externa | Fuera del alcance por ahora; se evalúa al escalar |

### Tiempos

| Escenario | Tiempo esperado | Aceptable |
|---|---|---|
| GPU con ROCm | < 30 segundos | Sí |
| Vulkan | 30–120 segundos | Sí |
| CPU con 32 GB RAM | 2–10 minutos | Sí, con indicador de progreso |
| Cualquier escenario | > 10 minutos | No — revisar configuración |

La app muestra **indicador de progreso** y **botón de cancelar** en cualquier escenario. Un tiempo de espera sin feedback no es aceptable.

> **Tarea 0 — innegociable**: validar el entorno completo antes de arrancar el desarrollo (ver sección 16).

---

## 6. Sistemas de representación

| Sistema | Fase | Notas |
|---|---|---|
| Vistas normalizadas IRAM (planta, alzado, perfil) | 1A | Método europeo ISO E, normas IRAM |
| Sistema de Monge / diédrico (planta + alzado con línea de tierra) | 1A | Dos proyecciones; sin tercera proyección ni nomenclatura A', A'' en Fase 1 |
| Isométrica | 1A | Dibujo isométrico a escala 1:1 (no proyección reducida ×0,816) |
| Perspectiva caballera, cortes, tercera proyección | Posterior | — |

- Se generan **solo si el docente los solicita**; si no, la app genera únicamente el modelo 3D
- La app reconoce variantes textuales: "Monge", "Monje", "diédrico", "vistas", "isométrica", etc.
- Unidades: milímetros, método europeo (ISO E) según normas IRAM

### Cotas
Opcionales por solicitud explícita. Se activan en el panel de confirmación o en el paso de exportación.

> **Nota**: la cotación automática correcta según IRAM es compleja. Se evalúa mover a una fase posterior si el esfuerzo no está justificado en Fase 1.

---

## 7. Exportación

El docente elige los formatos **antes** de exportar (paso explícito en el flujo).

| Formato | Contenido |
|---|---|
| STL | Modelo 3D (impresión 3D) |
| STEP | Modelo 3D (programas CAD) |
| SVG | Vistas o proyecciones (si se pidió sistema de representación) |
| PNG / JPG / WebP | Conversión desde SVG |

> **Fuera del alcance en Fase 1**: PDF con lámina y rótulo IRAM (planificado para una fase posterior).

---

## 8. Visor 3D en pantalla

Vista 3D girable con ángulo completo desde todos los lados. Implementado en Gradio (si no es suficientemente funcional, se reemplaza por componente con Three.js u otro).

---

## 9. Workspace y historial

| Decisión | Detalle |
|---|---|
| Workspace por defecto | Carpeta configurable — **no** usar `Documentos` por defecto (puede estar en OneDrive en Windows 11) |
| Ruta recomendada | `C:\[NombreApp]\` o ruta sin espacios ni tildes |
| Por proyecto | Subcarpeta con nombre automático (objeto + fecha/hora, sin caracteres especiales) |
| Historial | Lista de proyectos anteriores dentro de la app, reabibles y borrables |

---

## 10. Catálogo de figuras

### Fase 1A — figuras geométricas básicas

**MVP mínimo** (primer hito funcional):
- Prisma rectangular + cilindro + agujero pasante
- Vistas IRAM
- Exportación STL / STEP / SVG
- Modo formulario sin IA

**Catálogo completo Fase 1A**:

| Figura | Parámetros |
|---|---|
| Prisma rectangular | largo, ancho, alto |
| Prisma cuadrado | lado, alto |
| Cilindro | diámetro, alto |
| Prisma hexagonal | **diámetro entre caras** (inscrito), alto |
| Pirámide cuadrada | lado base, alto |
| Cono | diámetro base, alto |
| Esfera | diámetro |

**Operaciones de modificación**:

| Operación | Parámetros |
|---|---|
| Agujero cilíndrico (pasante o ciego) | diámetro, profundidad, cara destino, posición (centrado por defecto; offset X/Y opcional desde el centro) |
| Chaflán | distancia, aristas (o "todas las disponibles") |
| Redondeo (fillet) | radio, aristas (o "todas las disponibles") |

Si el docente no especifica aristas para chaflán o redondeo, se aplica a **todas las aristas disponibles** de esa figura.

**Compatibilidad figura/operación** — la receta rechaza combinaciones inválidas con mensaje claro:

| Figura | Agujero | Caras disponibles para agujero | Chaflán | Redondeo |
|---|---|---|---|---|
| Prisma rectangular | ✓ | superior, inferior, laterales | ✓ todas las aristas | ✓ todas las aristas |
| Prisma cuadrado | ✓ | superior, inferior, laterales | ✓ todas las aristas | ✓ todas las aristas |
| Cilindro | ✓ | superior, inferior | ✓ bordes circulares sup/inf | ✓ bordes circulares sup/inf |
| Prisma hexagonal | ✓ | superior, inferior, laterales | ✓ todas las aristas | ✓ todas las aristas |
| Pirámide cuadrada | ✓ | inferior (base) | ✓ solo aristas de la base | ✓ solo aristas de la base |
| Cono | ✓ | inferior (base) | ✗ | ✗ |
| Esfera | ✗ | — | ✗ | ✗ |

Regla de validación para redondeo: **radio < mitad de la arista más corta involucrada** (radio igual a la mitad consume la cara entera y hace fallar a CadQuery).

### Fase 1B — piezas mecánicas estáticas

Piezas sueltas, sin ensamble. Orden de construcción (menor a mayor complejidad):

1. **Eje** — cilindro con chaflanes opcionales
2. **Polea** — perfil de revolución
3. **Riel** — perfil extruido
4. **Engranaje** — vía `cq_gears`

---

## 11. Convención de ejes

| Eje | Dimensión | Parámetro en el prisma rectangular |
|---|---|---|
| X | Largo | `largo` |
| Y | Ancho / Profundidad | `ancho` |
| Z | Altura | `alto` |

Esta convención aplica al modelo 3D (CadQuery) y a las vistas generadas. Los invariantes de representación usan esta nomenclatura. En las vistas IRAM: la planta muestra X e Y; el alzado muestra X y Z; el perfil muestra Y y Z.

## 12. Tolerancias

| Contexto | Tolerancia |
|---|---|
| Geometría (CadQuery) | 0,001 mm |
| Volumen en STL | ±0,5 % (las curvas se triangularizan) |

> "Tolerancia cero" no existe en aritmética de punto flotante ni en la exportación STL. Los cálculos son deterministas dentro de estas tolerancias definidas.

---

## 13. Roadmap

| Fase | Contenido |
|---|---|
| **1A** | Figuras geométricas básicas → panel formulario → modelo 3D + vistas + exportación. MVP primero, luego catálogo completo. |
| **1B** | Piezas mecánicas simples estáticas: eje, polea, riel, engranaje (piezas sueltas) |
| **2** | Entrada por voz (faster-whisper) |
| **3** | Ensambles: piezas montadas con restricciones de posición |
| **4** | Mecanismos con movimiento y simulación |

---

## 14. Seguridad

- **Acceso**: solo `127.0.0.1`, sin exposición de red
- **Imágenes de entrada**:
  - Tamaño máximo: a definir en Tarea 0 (candidato: 10 MB)
  - Resolución máxima: a definir (candidato: 4096×4096 px)
  - Verificación de contenido real del archivo (no solo extensión)
- **Texto de entrada**: la protección real es arquitectural — la IA no tiene herramientas ni ejecuta código, y su única salida posible es un JSON validado por Pydantic. No existe un filtro de texto infalible; la arquitectura es el arnés.
- **Nombres de archivo de salida**: generados por la app, sin caracteres especiales ni secuencias de path traversal
- **Log JSON**: no guarda imágenes, solo referencias (nombre, hash). No guarda datos sensibles.
- **Commits**: pre-commit + gitleaks para evitar secretos en el repositorio

---

## 15. Estrategia de tests

El catálogo completo de tests con IDs, invariantes y evidencia requerida se documenta en `docs/tests-fase1.md`.

### Tests imprescindibles (Fase 1)

| Tipo | Qué cubre |
|---|---|
| Tests de recetas | Cada receta con parámetros válidos produce un sólido sin errores |
| Tests de validación geométrica | Parámetros inválidos (agujero > pieza, radio > arista, operación no soportada por figura) son rechazados con error claro |
| Tests de Pydantic | JSONs inválidos son rechazados antes de llegar a las recetas |
| Tests de exportación | STL, STEP y SVG se generan y son archivos válidos |
| Tests de formulario | El modo formulario sin IA produce el mismo resultado que con IA para los mismos parámetros |
| **Tests de representaciones** | Las vistas generadas cumplen los invariantes geométricos de cada sistema |

**Invariantes de representación a verificar**:

| Sistema | Invariantes |
|---|---|
| Vistas IRAM (ISO E) | Planta debajo del alzado; perfil a la derecha del alzado; alzado y planta comparten la misma extensión en X (ancho); alzado y perfil comparten la misma extensión en Z (altura); planta y perfil comparten la misma extensión en Y (profundidad) |
| Sistema de Monge | Línea de tierra presente; líneas de referencia perpendiculares a la línea de tierra; alzado arriba, planta abajo; la distancia de cada punto a la línea de tierra es su Z (cota) en el alzado y su Y (alejamiento) en la planta |
| Isométrica | Los tres ejes principales a 120° entre sí; escala 1:1 (no proyección reducida ×0,816) |

### Tests para después

- Tests de interpretación de IA (no deterministas, requieren estrategia aparte)
- Tests de interfaz Gradio
- Tests de performance de generación

### Arnés anti-mentiras
Ver `docs/tests-fase1.md` para: reglas del arnés (formato A-XX), IDs de tests (formato T-XX), renglones generados por script, evidencia de pytest, cobertura con líneas faltantes, valores calculados a mano como referencia.

### Trazabilidad
Matriz requisito → tarea → test en `docs/trazabilidad.md`.
Log JSON por pedido: pedido → interpretación → correcciones del docente → resultado.

---

## 16. Tarea 0 — validación del entorno

Debe completarse antes de escribir código de producción. Registrar resultados en un ADR.

1. **GPU + ROCm**: ¿corre un modelo multimodal 7B con aceleración en la RX 6700 XT en Windows? Tiempo de respuesta para un JSON de ~200 tokens.
2. **Vulkan**: si ROCm falla, probar aceleración Vulkan vía LM Studio como opción intermedia.
3. **CPU fallback**: medir tiempo de respuesta en CPU puro para el mismo modelo.
4. **Elección de modelo**: con los resultados anteriores, elegir el modelo multimodal más adecuado disponible al momento y registrarlo en `docs/ADR/001-modelo-ia.md`.
5. **Stack Python**: verificar que Python 3.11 + CadQuery + Gradio funcionan juntos en Windows 11 sin conflictos de versiones.
6. **Conversión SVG**: validar que la librería elegida (cairosvg u alternativa) convierte SVG a PNG/JPG/WebP en Windows sin dependencias externas problemáticas.
7. **Workspace**: verificar que la ruta de workspace elegida no está bajo OneDrive y no tiene espacios ni tildes.

---

## 17. Riesgos y mitigaciones

| # | Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|---|
| 1 | ROCm no funciona en RX 6700 XT en Windows | Alta | Alto | Tarea 0 item 1–2; fallback Vulkan → CPU |
| 2 | JSON de IA geométricamente inválido pasa Pydantic | Media | Alto | Validación geométrica dentro de cada receta |
| 3 | Complejidad subestimada de recetas mecánicas | Alta | Alto | Construir y testear recetas antes que todo; orden eje → polea → riel → engranaje |
| 4 | Gradio insuficiente para visor 3D girable | Media | Medio | Si no es funcional, reemplazar por Three.js u otro |
| 5 | cairosvg u otras librerías de conversión SVG problemáticas en Windows | Media | Medio | Validar en Tarea 0 item 6; tener alternativa identificada |
| 6 | Conflicto de versiones Python + CadQuery + Gradio | Media | Alto | Validar entorno completo en Tarea 0 item 5 |
| 7 | Carpeta Documentos redirigida a OneDrive (espacios, tildes, sync) | Media | Medio | No usar Documentos por defecto; workspace en ruta sin espacios |

---

## 18. Stack técnico

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.11+ |
| Validación de esquemas | Pydantic |
| Modelado 3D | CadQuery + cq_gears (Fase 1B+) |
| Interfaz | Gradio |
| Modelo de IA | Multimodal local — a elegir en Tarea 0 |
| Runtime IA | Ollama / LM Studio |
| Voz (Fase 2) | faster-whisper |
| Tests | pytest + cobertura |
| Linting | ruff |
| Seguridad de commits | pre-commit + gitleaks |
| CI | GitHub Actions |

---

## 19. Documentación esperada

- `README.md` — documentado paso a paso
- `CHANGELOG.md`
- `docs/ADR/` — un registro por cada decisión arquitectural importante
- `docs/fuentes.md` — cada librería y modelo con link, versión y licencia
- `docs/trazabilidad.md` — matriz requisito → tarea → test
- Log JSON por pedido: pedido → interpretación → correcciones del docente → resultado (sin imágenes)

---

## 20. Criterios de aceptación — Fase 1 completa

### Criterios del MVP (primer hito demostrable)

1. Prisma rectangular + cilindro generados correctamente desde el formulario
2. Agujero pasante en prisma rectangular funciona y es rechazado con mensaje claro si el diámetro es mayor o igual al lado menor (diámetro igual = pared de espesor cero)
3. Vistas IRAM generadas y exportables en SVG/PNG con los invariantes correctos (planta debajo del alzado, perfil a la derecha)
4. Exportación STL y STEP sin errores
5. Modo formulario funciona sin IA activa

### Criterios de Fase 1 completa

1. Dado texto + imagen (o solo texto) de una figura, el panel de confirmación se pre-completa y el docente puede completar manualmente lo que falta
2. **Interpretación por IA**: tiempo ≤ 10 minutos en cualquier escenario; siempre con indicador de progreso y botón cancelar
3. **Generación por CadQuery**: tiempo en segundos; se reporta por separado del tiempo de IA
4. Dado el panel completo, genera modelo 3D exportable en STL y STEP sin errores, con tolerancia geométrica de 0,001 mm
5. Si se solicita sistema de representación, genera vistas con invariantes correctos (ver sección 15 y `docs/tests-fase1.md`), exportables en SVG/PNG/JPG/WebP
6. El modo formulario funciona sin IA activa y produce el mismo resultado que con IA para los mismos parámetros
7. El historial guarda, recupera y borra proyectos
8. Las piezas mecánicas de Fase 1B (eje, polea, riel, engranaje) se generan correctamente con parámetros dados
9. Parámetros inválidos y operaciones no soportadas por la figura son rechazados con mensaje de error claro antes de intentar construir

---

## 21. Puntos pendientes

- Nombre definitivo del proyecto (provisional: a definir)
- Formato exacto del rótulo IRAM (para cuando se implemente el PDF de lámina, fase posterior)
- Elección de modelo de IA (se resuelve en Tarea 0, se registra en ADR)
- Tamaño y resolución máxima de imágenes de entrada (se decide en Tarea 0)
- Decisión final sobre cotas automáticas en Fase 1 vs. fase posterior
