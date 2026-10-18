# Data Model: MVP — Modelo 3D desde Formulario

**Date**: 2026-10-18 | **Branch**: `001-mvp-modelo-formulario`

---

## Entidades

### FiguraTipo

Enumeración. Valores válidos en el MVP:

| Valor | Descripción |
|---|---|
| `prisma_rectangular` | Prisma con base rectangular |
| `cilindro` | Cilindro recto |

---

### PrismaRectangularParams

Parámetros de entrada del prisma rectangular. Todos en milímetros.

| Campo | Tipo | Restricción | Descripción |
|---|---|---|---|
| `largo` | float | > 0 | Dimensión en X |
| `ancho` | float | > 0 | Dimensión en Y |
| `alto` | float | > 0 | Dimensión en Z |
| `agujero` | `AgujeroParams \| None` | opcional | Agujero pasante (si se solicita) |
| `vistas_iram` | bool | default False | Solicitar vistas IRAM |

---

### CilindroParams

Parámetros de entrada del cilindro. Todos en milímetros.

| Campo | Tipo | Restricción | Descripción |
|---|---|---|---|
| `diametro` | float | > 0 | Diámetro de la base |
| `alto` | float | > 0 | Altura en Z |
| `agujero` | `AgujeroParams \| None` | opcional | Agujero coaxial pasante |
| `vistas_iram` | bool | default False | Solicitar vistas IRAM |

---

### AgujeroParams

Parámetros del agujero pasante (opcional en ambas figuras del MVP).

| Campo | Tipo | Restricción | Descripción |
|---|---|---|---|
| `diametro` | float | > 0 | Diámetro del agujero |
| `cara` | `CaraAgujero` | enum | Cara de entrada |
| `offset_x` | float | default 0.0 | Offset desde el centro en X (mm) |
| `offset_y` | float | default 0.0 | Offset desde el centro en Y (mm) |

---

### CaraAgujero

Enumeración de caras válidas para agujero. La receta verifica compatibilidad con la figura.

| Valor | Aplicable a |
|---|---|
| `superior` | prisma_rectangular, cilindro |
| `inferior` | prisma_rectangular, cilindro |
| `frontal` | prisma_rectangular |
| `trasera` | prisma_rectangular |
| `lateral_izq` | prisma_rectangular |
| `lateral_der` | prisma_rectangular |

---

### SolicitudGeneracion

Objeto raíz que entra al sistema desde el formulario. Campo discriminante: `tipo`.

| Campo | Tipo | Descripción |
|---|---|---|
| `tipo` | `FiguraTipo` | Discrimina qué schema de parámetros se usa |
| `params` | `PrismaRectangularParams \| CilindroParams` | Parámetros según `tipo` |

Validado con Pydantic antes de llegar a cualquier receta. Campos extra → rechazo (`extra="forbid"`).

---

### ResultadoGeneracion

Objeto de retorno del sistema tras una generación exitosa.

| Campo | Tipo | Descripción |
|---|---|---|
| `carpeta` | str | Ruta absoluta de la subcarpeta creada en el workspace |
| `stl` | str | Ruta absoluta del archivo .stl |
| `step` | str | Ruta absoluta del archivo .step |
| `svg_vistas` | `str \| None` | Ruta del SVG de vistas IRAM (si se solicitó) |
| `png_vistas` | `str \| None` | Ruta del PNG convertido desde SVG (si se solicitó) |

---

## Reglas de validación geométrica

Estas reglas se aplican **dentro de las recetas**, no en Pydantic. Son la segunda capa de
validación (Pydantic valida estructura; la receta valida coherencia geométrica).

### Prisma rectangular

| Regla | Condición de error |
|---|---|
| Parámetros positivos | largo, ancho, alto ≤ 0 → error antes de construir |
| Agujero: diámetro < lado menor de la cara | diámetro ≥ lado_menor(cara) → error |
| Agujero: posición dentro de la cara | el círculo (offset_x, offset_y, radio) debe caber completamente en la cara → error si sale |

### Cilindro

| Regla | Condición de error |
|---|---|
| Parámetros positivos | diámetro, alto ≤ 0 → error antes de construir |
| Agujero: diámetro < diámetro del cilindro | diámetro_agujero ≥ diámetro_cilindro → error |
| Agujero: solo cara superior o inferior | cualquier otra cara → error |

---

## Invariantes de representación IRAM (para views_iram/generator.py)

| Invariante | Verificación |
|---|---|
| Planta debajo del alzado | origen_Y(planta) > origen_Y(alzado) + alto_alzado en el SVG compuesto |
| Perfil a la derecha del alzado | origen_X(perfil) > origen_X(alzado) + ancho_alzado |
| Alzado y planta: mismo ancho X | extensión_X(alzado) = extensión_X(planta) ± 0,001 |
| Alzado y perfil: misma altura Z | extensión_Z(alzado) = extensión_Z(perfil) ± 0,001 |
| Planta y perfil: misma profundidad Y | extensión_Y(planta) = extensión_Y(perfil) ± 0,001 |

---

## Estados del sistema (ciclo de vida de una generación)

```
IDLE
  → (docente completa formulario y presiona Generar)
VALIDATING
  → (Pydantic + validación geométrica)
  → error: IDLE (con mensaje de error)
GENERATING
  → (CadQuery construye el sólido; UI muestra "Generando…")
  → error interno: IDLE (con mensaje de error; sin archivos parciales)
EXPORTING
  → (STL + STEP + SVG/PNG si se pidió)
  → error de escritura: IDLE (con mensaje de error)
DONE
  → (UI muestra rutas de archivos; docente puede generar otro)
  → si carpeta ya existe: CONFIRMING_OVERWRITE
CONFIRMING_OVERWRITE
  → (docente cancela) → IDLE
  → (docente confirma) → GENERATING
```
