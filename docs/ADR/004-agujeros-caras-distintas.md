# ADR-004 — Agujeros en caras distintas pueden cruzarse sin error

**Estado:** Aceptado
**Fecha:** 2026-10-26
**Contexto:** US2 — Varios agujeros por pieza

## Decisión

La regla de distancia mínima entre agujeros (`dist > r₁ + r₂ + 1 mm`) se aplica
**únicamente entre agujeros en la misma cara**. Agujeros en caras distintas pueden
coexistir aunque sus cilindros se crucen geométricamente en el interior del sólido.

## Justificación

1. **Operaciones legítimas en fabricación.** Dos agujeros perforados desde caras
   perpendiculares y que se cruzan internamente son una operación común en
   mecanizado (p.ej., agujero de purga + agujero de fijación). CadQuery los aplica
   como operaciones de corte secuenciales y produce un sólido válido.

2. **La validación por cara es suficiente y manejable.** Detectar intersecciones
   volumétricas en 3D requeriría cálculos de geometría computacional costosos
   (distancia entre ejes en el espacio). La heurística 2D por cara es simple,
   comprensible para la docente y cubre el caso de error más común (dos agujeros
   en la misma cara que se solapan).

3. **El modelo geométrico producido es válido.** Como demuestra el test T-207,
   cuando los ejes se cruzan el punto de cruce queda fuera del sólido (ambos
   cilindros lo eliminan), lo que es el comportamiento esperado y correcto.

## Consecuencias

- Dos agujeros en caras distintas con ejes que se cruzan son aceptados por el
  esquema y por la receta.
- El usuario es responsable de definir agujeros en caras distintas con sentido
  geométrico para su pieza.
- Si en el futuro se necesita una validación inter-caras, se deberá extender el
  `model_validator` de `PrismaRectangularParams` con un check de distancia
  entre ejes en 3D.
