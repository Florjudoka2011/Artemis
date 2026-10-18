# Feature Specification: Artemis — MVP Modelo 3D desde Formulario

**Feature Branch**: `001-mvp-modelo-formulario`

**Created**: 2026-10-18

**Status**: Draft

**Input**: User description: "Especificá solo el MVP como primera funcionalidad, no la
fase 1 completa."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Generar modelo 3D desde formulario (Priority: P1)

La docente abre la aplicación, completa un formulario con el tipo de figura (prisma
rectangular o cilindro) y sus medidas, y obtiene un modelo 3D que puede exportar en STL y
STEP. No requiere ningún componente de IA activo.

**Why this priority**: Es el núcleo absoluto del MVP. Sin esto no existe demostrable. Toda
la cadena de valor — descripción → parámetros → sólido → archivo — pasa por aquí.

**Independent Test**: Se puede probar completamente ingresando medidas en el formulario,
presionando "Generar" y verificando que los archivos STL y STEP se crean en el workspace.
No depende de vistas, IA ni historial.

**Acceptance Scenarios**:

1. **Given** el formulario vacío con tipo "prisma rectangular",
   **When** la docente ingresa largo=100, ancho=60, alto=40 y presiona "Generar",
   **Then** la app produce un sólido válido y los archivos STL y STEP aparecen en el
   workspace, con el volumen correcto (240 000 mm³ ±0,5%).

2. **Given** el formulario con tipo "cilindro",
   **When** la docente ingresa diámetro=50, alto=80 y presiona "Generar",
   **Then** la app produce un cilindro sólido válido y los archivos STL y STEP aparecen
   en el workspace.

3. **Given** la app recién abierta,
   **When** la docente no completa uno o más campos obligatorios y presiona "Generar",
   **Then** la app no genera nada y lista los campos faltantes con un mensaje claro.

---

### User Story 2 — Agregar agujero pasante al prisma rectangular (Priority: P2)

La docente selecciona "agujero pasante" en el formulario del prisma rectangular, especifica
diámetro, cara de entrada y posición (centrado por defecto), y obtiene el sólido modificado.

**Why this priority**: El agujero es la operación de modificación más frecuente en dibujo
técnico. Junto con el prisma base, cubre la mayor parte de los ejercicios del nivel. Sin
agujero el MVP es demasiado limitado para ser útil en el aula.

**Independent Test**: Se puede probar sobre el prisma rectangular ya generado en US1:
ingresar diámetro=20, cara=superior, centrado, y verificar que el STL resultante tiene el
volumen correcto (227 434 mm³ ±0,5%).

**Acceptance Scenarios**:

1. **Given** un prisma rectangular (100×60×40) con agujero configurado,
   **When** la docente especifica diámetro=20, cara=superior, posición=centrado,
   **Then** el sólido tiene un agujero pasante cilíndrico y el volumen reducido es
   correcto.

2. **Given** un prisma rectangular (100×60×40),
   **When** la docente especifica diámetro=40 (igual al lado menor = ancho),
   **Then** la app rechaza la operación con un mensaje claro antes de intentar construir
   el sólido.

3. **Given** un prisma rectangular,
   **When** la docente especifica un offset que hace que el agujero salga parcialmente de
   la cara,
   **Then** la app rechaza la operación con un mensaje claro.

---

### User Story 3 — Generar y exportar vistas IRAM del modelo (Priority: P3)

La docente marca "vistas IRAM" en el formulario, genera el modelo, y recibe además de STL y
STEP un archivo SVG con las tres vistas normalizadas (planta, alzado, perfil) en disposición
correcta según norma IRAM/ISO E. Puede exportar el SVG también como PNG.

**Why this priority**: Las vistas son el segundo entregable clave del MVP según los
criterios de aceptación definidos en la documentación del proyecto. Son necesarias para el
criterio 3 del MVP. Dependen de tener el sólido generado (US1), por eso van después.

**Independent Test**: Con el prisma rectangular (100×60×40) generado en US1, activar
"vistas IRAM" y verificar que el SVG exportado contiene tres vistas con la disposición
correcta: planta debajo del alzado, perfil a la derecha del alzado, con dimensiones
compartidas consistentes.

**Acceptance Scenarios**:

1. **Given** el prisma rectangular generado (100×60×40) con "vistas IRAM" activado,
   **When** la docente exporta,
   **Then** el SVG contiene planta, alzado y perfil; la planta está debajo del alzado;
   el perfil está a la derecha del alzado; alzado y planta comparten el mismo ancho (X);
   alzado y perfil comparten la misma altura (Z); planta y perfil comparten la misma
   profundidad (Y).

2. **Given** las vistas IRAM generadas,
   **When** la docente elige "exportar como PNG",
   **Then** se genera un archivo PNG válido con dimensiones mayores a cero.

3. **Given** el formulario sin "vistas IRAM" marcado,
   **When** la docente genera,
   **Then** no se genera ningún archivo SVG ni PNG de vistas (solo STL y STEP).

---

### Edge Cases

- ¿Qué pasa si el workspace configurado no existe o no tiene permisos de escritura?
  → La app informa el error antes de intentar generar; no deja el proceso a medias.
- ¿Qué pasa si se ingresa cero o negativo en cualquier medida?
  → La app rechaza el valor con mensaje claro antes de construir.
- ¿Qué pasa si el diámetro del cilindro es mayor que el alto?
  → Geometría válida — la app lo acepta y genera correctamente.
- ¿Qué pasa si el modelo falla internamente durante la construcción?
  → La app muestra un mensaje de error sin dejar archivos parciales en el workspace.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE ofrecer un formulario con los campos necesarios para definir
  un prisma rectangular (largo, ancho, alto) o un cilindro (diámetro, alto).
- **FR-002**: El sistema DEBE ofrecer una operación opcional de agujero pasante para el
  prisma rectangular, con campos: diámetro, cara de entrada, posición (centrado por defecto;
  offset X/Y opcional desde el centro).
- **FR-003**: El sistema DEBE permitir marcar la opción "vistas IRAM" en el formulario para
  solicitar vistas normalizadas junto con el modelo 3D.
- **FR-004**: El sistema DEBE generar el modelo 3D con las medidas exactas indicadas, con
  tolerancia geométrica de 0,001 mm.
- **FR-005**: El sistema DEBE rechazar cualquier combinación de parámetros inválidos
  (medida ≤ 0, diámetro de agujero ≥ lado menor de la cara, agujero fuera del área de la
  cara) con un mensaje que identifique el problema específico, antes de iniciar la
  construcción.
- **FR-006**: El sistema DEBE exportar el modelo en STL y STEP al workspace configurado.
- **FR-007**: Si se solicitaron vistas IRAM, el sistema DEBE exportar un SVG con planta,
  alzado y perfil en disposición normalizada (ISO E / IRAM): planta debajo del alzado,
  perfil a la derecha del alzado; con las extensiones compartidas correctas entre vistas.
- **FR-008**: El sistema DEBE ofrecer conversión del SVG de vistas a PNG.
- **FR-009**: El sistema DEBE funcionar completamente sin ningún componente de IA activo.
- **FR-010**: Los nombres de los archivos exportados DEBEN ser generados por la app, libres
  de caracteres especiales, tildes, espacios o secuencias de path traversal. El nombre de
  carpeta de cada proyecto incluye el tipo de figura y un timestamp (ej.
  `prisma_rectangular_20261018_143022`); si ya existe una carpeta con ese nombre, la app
  DEBE preguntar a la docente antes de sobreescribir, dándole la opción de cancelar o
  confirmar.
- **FR-011**: El sistema DEBE informar el resultado de cada generación: éxito con rutas de
  archivos, o error con descripción del problema.
- **FR-012**: Durante la construcción del sólido, el sistema DEBE mostrar un indicador
  visual (mensaje "Generando…" o equivalente) y bloquear la interfaz hasta completar o
  fallar.

### Key Entities

- **Figura**: tipo (prisma_rectangular | cilindro) + parámetros dimensionales + operaciones
  de modificación opcionales.
- **Operación de modificación**: tipo (agujero_pasante) + parámetros propios (diámetro,
  cara, posición).
- **Solicitud de vistas**: flag booleano + sistema de representación (IRAM en el MVP).
- **Proyecto generado**: figura + sólido resultante + archivos exportados + ruta en
  workspace.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: La docente completa el formulario y obtiene los archivos STL y STEP en menos
  de 10 segundos desde que presiona "Generar" (excluye tiempo de IA, que no aplica en el
  MVP).
- **SC-002**: El volumen del STL exportado difiere del volumen teórico en no más de 0,5%
  para cualquier figura del MVP.
- **SC-003**: Las vistas IRAM generadas cumplen los cinco invariantes geométricos de
  disposición (planta/alzado/perfil con extensiones compartidas correctas) en el 100% de
  los casos.
- **SC-004**: El 100% de los parámetros inválidos documentados es rechazado con mensaje
  identificatorio antes de intentar construir.
- **SC-005**: Todos los tests del MVP definidos en `docs/tests-fase1.md` (recetas T-01 a
  T-05 y T-10 a T-12, Pydantic T-100 a T-108, exportación T-110 a T-113, vistas IRAM
  T-120 a T-124, formulario T-150 a T-152) pasan en CI.
- **SC-006**: El modo formulario sin IA produce archivos STL bit-a-bit idénticos para los
  mismos parámetros en ejecuciones sucesivas (determinismo).

---

## Clarifications

### Session 2026-10-18

- Q: Cuando la docente genera el mismo modelo dos veces, ¿qué hace la app con los archivos anteriores? → A: La app pregunta antes de sobreescribir; la docente elige cancelar o confirmar. (incorporado en FR-010)
- Q: Mientras la app construye el sólido, ¿necesita mostrar indicador visual de progreso? → A: Sí, mostrar mensaje "Generando…" o spinner; interfaz bloqueada hasta completar.
- Q: ¿El log JSON por pedido (exigido por la constitución) está en el alcance del MVP? → A: No; se difiere a cuando se integre el conector de IA.

---

## Assumptions

- La aplicación corre en la PC de la docente (Windows 11, hardware conocido); no se
  considera soporte multi-plataforma en esta etapa.
- El workspace configurado existe y tiene permisos de escritura; la configuración del
  workspace se realizó previamente (fuera del alcance del MVP).
- El visor 3D rotativo en pantalla queda fuera del alcance del MVP; el resultado visible
  es el conjunto de archivos exportados.
- El historial de proyectos queda fuera del alcance del MVP.
- La integración de IA queda completamente fuera del alcance del MVP; el formulario se
  completa manualmente en su totalidad.
- La validación de esquema de entrada (Pydantic) es parte del MVP como capa de seguridad
  interna, aunque la docente no interactúa con ella directamente.
- Unidades: milímetros exclusivamente en esta etapa.
- El MVP cubre solo las figuras prisma rectangular y cilindro; las demás figuras del
  catálogo (Fase 1A completa) son trabajo posterior.
- El log JSON por pedido (constitución §V) se implementa cuando se integre el conector de
  IA; queda fuera del alcance del MVP.
