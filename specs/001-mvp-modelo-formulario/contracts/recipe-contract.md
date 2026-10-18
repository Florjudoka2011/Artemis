# Contract: Protocolo de receta paramétrica

**Module**: `src/recipes/base.py`
**Date**: 2026-10-18

Todas las recetas del MVP siguen este protocolo. Una receta es una función Python pura:
recibe parámetros validados → devuelve un sólido CadQuery. Sin side-effects, sin I/O.

---

## Firma de protocolo

```python
from cadquery import Workplane
from typing import Protocol

class Receta(Protocol):
    def __call__(self, params: BaseModel) -> Workplane:
        """
        Recibe parámetros ya validados por Pydantic.
        Realiza validación geométrica interna.
        Devuelve el sólido CadQuery.
        Lanza ValueError con mensaje descriptivo si los parámetros son geométricamente
        inválidos (ej. agujero más grande que la pieza).
        Nunca produce side-effects (no escribe archivos, no llama a IA).
        """
        ...
```

---

## Contrato de comportamiento

| Condición | Comportamiento esperado |
|---|---|
| Parámetros válidos (Pydantic + geometría) | Devuelve `cq.Workplane` con el sólido; sin error |
| Parámetros geométricamente inválidos | Lanza `ValueError` con descripción del problema antes de llamar a CadQuery |
| Parámetros NaN / infinito | Pydantic los rechaza antes de llegar a la receta |
| Sólido CadQuery inválido (error interno OCC) | La excepción de CadQuery se propaga; el caller maneja |

---

## Recetas del MVP

| Módulo | Función | Figuras | Tests |
|---|---|---|---|
| `src/recipes/prisma_rectangular.py` | `construir(params: PrismaRectangularParams)` | Prisma rectangular + agujero opcional | T-01 a T-09 |
| `src/recipes/cilindro.py` | `construir(params: CilindroParams)` | Cilindro + agujero opcional | T-10 a T-14 |

---

## Validaciones geométricas internas (por receta)

### prisma_rectangular.construir

```
1. Verificar largo, ancho, alto > 0  (redundante con Pydantic, defensive)
2. Si agujero:
   a. Determinar lado_menor(cara) según la cara seleccionada
   b. Si diametro >= lado_menor → ValueError("Agujero demasiado grande para la cara")
   c. Calcular si el círculo (offset_x, offset_y, radio) cabe en la cara
      → Si no cabe → ValueError("Agujero sale fuera de la cara")
3. Construir sólido base
4. Si agujero: aplicar operación de agujero
5. Devolver sólido
```

### cilindro.construir

```
1. Verificar diametro, alto > 0  (redundante con Pydantic, defensive)
2. Si agujero:
   a. Verificar cara es superior o inferior → si no → ValueError("Cara no válida para cilindro")
   b. Si diametro_agujero >= diametro_cilindro → ValueError("Agujero igual o mayor que el cilindro")
3. Construir sólido base
4. Si agujero: aplicar operación de agujero coaxial
5. Devolver sólido
```

---

## Invariante de volumen para tests

Los tests usan `math.isclose(actual, expected, rel_tol=1e-6)` sobre el volumen del sólido
resultante (no del STL exportado). Los valores esperados están en `docs/tests-fase1.md`.
