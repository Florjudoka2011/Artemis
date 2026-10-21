# Catálogo de tests — Fase 1

> Referenciado desde `docs/00-idea.md` sección 15.
> Convención de ejes: X = ancho, Y = profundidad, Z = altura.
> Evidencia de ejecución: `docs/evidencia/fase1/`

---

## Arnés anti-mentiras — Reglas A-XX

| ID | Regla |
|---|---|
| A-01 | Cada test tiene un ID único en formato `T-XX` en su docstring |
| A-02 | Cada test incluye el ID del requisito que verifica (formato `R-XX` de `docs/trazabilidad.md`) |
| A-03 | Los renglones de la matriz de trazabilidad se generan con un script, no a mano |
| A-04 | La evidencia de ejecución se guarda en `docs/evidencia/fase1/` con `pytest --tb=short -v` |
| A-05 | El reporte de cobertura incluye líneas no cubiertas: `pytest --cov=src --cov-report=term-missing` |
| A-06 | Cada receta tiene al menos un test de borde: parámetro en el límite exacto del rechazo (por ejemplo, radio = mitad_arista - 0,001 pasa; radio = mitad_arista falla) |
| A-07 | Ningún test importa ni llama a la IA real; todos los tests del núcleo son deterministas |
| A-08 | Un test que pasa sin assertions falla en CI (usar `assert` explícitos; nunca dejar `pass`) |
| A-09 | Tests de mutación con `mutmut` sobre las recetas paramétricas antes de considerar Fase 1 completa |

---

## Tests de recetas — figuras geométricas (Fase 1A)

> Tolerancias: volumen del sólido CadQuery se verifica con `math.isclose(actual, expected, rel_tol=1e-6)` (tolerancia relativa de 1 ppm).
> El ±0,5 % solo aplica a exportaciones STL (triangulación de curvas).
> Convención de ejes: X = largo, Y = ancho/profundidad, Z = alto/altura.

### Prisma rectangular

| ID | Caso | Parámetros | Resultado esperado |
|---|---|---|---|
| T-01 | Nominal | largo=100, ancho=60, alto=40 | Volumen = 240 000 mm³; `isclose(actual, 240000, rel_tol=1e-6)` |
| T-02 | Parámetro cero | largo=0, ancho=60, alto=40 | Error antes de construir |
| T-03 | Parámetro negativo | largo=−10, ancho=60, alto=40 | Error antes de construir |
| T-04 | Agujero pasante centrado | diámetro=20, cara=superior, pasante (profundidad=alto=40) | Volumen = 240 000 − π×10²×40 = 227 433,629 mm³; `isclose(actual, 227433.629, rel_tol=1e-6)` |
| T-05 | Agujero inválido (diámetro ≥ lado menor) | diámetro=40, cara=superior (lado menor = ancho = 40) | Rechazado con mensaje claro |
| T-06 | Chaflán en todas las aristas | distancia=5 | Sólido válido; volumen < 240 000; caja contenedora = 100×60×40 sin cambios |
| T-07 | Redondeo válido | radio=19, aristas de 40 mm (límite: radio < 20) | Sólido válido; volumen < 240 000 |
| T-08 | Redondeo inválido (radio = mitad arista) | radio=20, aristas de 40 mm | Rechazado: arista más corta = 40 mm → límite = 20 mm (exclusivo) |
| T-09 | Agujero desplazado fuera de cara | diámetro=20, offset_x=50 (sale del área largo=100) | Rechazado con mensaje claro |

### Prisma cuadrado

| ID | Caso | Parámetros | Resultado esperado |
|---|---|---|---|
| T-15 | Nominal | lado=50, alto=70 | Volumen = 175 000,000 mm³ ±0,001 |
| T-16 | Agujero pasante centrado | diámetro=20, cara=superior, pasante (profundidad=alto=70) | Volumen = 175 000 − π×10²×70 = 153 008,851 mm³; `isclose(actual, 153008.851, rel_tol=1e-6)` |
| T-17 | Agujero inválido (diámetro ≥ lado) | diámetro=50 | Rechazado con mensaje claro |
| T-18 | Redondeo inválido (radio ≥ mitad arista) | radio=25, arista de 50 mm | Rechazado con mensaje claro |

### Cilindro

| ID | Caso | Parámetros | Resultado esperado |
|---|---|---|---|
| T-10 | Nominal | diámetro=50, alto=80 | Volumen = π×25²×80 = 157 079,633 mm³; `isclose(actual, 157079.633, rel_tol=1e-6)` |
| T-11 | Agujero coaxial pasante | diámetro_agujero=20, cara=superior, profundidad=80 (pasante) | Volumen = π×(25²−10²)×80 = 131 946,891 mm³; `isclose(actual, 131946.891, rel_tol=1e-6)` |
| T-12 | Agujero inválido (diámetro ≥ diámetro cilindro) | diámetro_agujero=50 | Rechazado con mensaje claro |
| T-13 | Chaflán en borde circular superior | distancia=3 | Sólido válido; volumen < 157 079,633 |
| T-14 | Redondeo en borde circular superior | radio=3 | Sólido válido; volumen < 157 079,633 |

### Prisma hexagonal

| ID | Caso | Parámetros | Resultado esperado |
|---|---|---|---|
| T-20 | Nominal | diámetro_inscrito=60, alto=50 | Volumen = (√3/2)×60²×50 = 155 884,573 mm³; `isclose(actual, 155884.573, rel_tol=1e-6)` |
| T-21 | Agujero en cara superior centrado | diámetro=20, pasante | Sólido válido; volumen < T-20 |
| T-22 | Chaflán en todas las aristas | distancia=4 | Sólido válido; volumen < T-20 |

### Pirámide cuadrada

| ID | Caso | Parámetros | Resultado esperado |
|---|---|---|---|
| T-30 | Nominal | lado_base=80, alto=60 | Volumen = 80²×60/3 = 128 000,000 mm³; `isclose(actual, 128000.0, rel_tol=1e-6)` |
| T-31 | Agujero en cara inferior (base) centrado | diámetro=30, profundidad=10, cara=inferior | Sólido válido; volumen < T-30 |
| T-32 | Agujero en cara lateral | cara=lateral | Rechazado: solo admite cara inferior en Fase 1 |
| T-33 | Chaflán en aristas de la base | distancia=5 | Sólido válido; volumen < T-30 |
| T-34 | Redondeo en aristas laterales (hacia vértice superior) | radio=5 | Rechazado: no aplica en aristas que convergen en el vértice |

### Cono

| ID | Caso | Parámetros | Resultado esperado |
|---|---|---|---|
| T-40 | Nominal | diámetro_base=60, alto=80 | Volumen = π×30²×80/3 = 75 398,224 mm³; `isclose(actual, 75398.224, rel_tol=1e-6)` |
| T-41 | Agujero en cara inferior (base) centrado | diámetro=20, profundidad=10, cara=inferior | Sólido válido; volumen < T-40 |
| T-42 | Chaflán | cualquier parámetro | Rechazado con mensaje claro |
| T-43 | Redondeo | cualquier parámetro | Rechazado con mensaje claro |

### Esfera

| ID | Caso | Parámetros | Resultado esperado |
|---|---|---|---|
| T-50 | Nominal | diámetro=60 | Volumen = (4/3)×π×30³ = 113 097,336 mm³; `isclose(actual, 113097.336, rel_tol=1e-6)` |
| T-51 | Agujero | cualquier parámetro | Rechazado: esfera no admite agujeros en Fase 1 |
| T-52 | Chaflán | cualquier parámetro | Rechazado con mensaje claro |
| T-53 | Redondeo | cualquier parámetro | Rechazado con mensaje claro |

---

## Tests de recetas — piezas mecánicas (Fase 1B)

| ID | Pieza | Caso | Resultado esperado |
|---|---|---|---|
| T-60 | Eje | Nominal: diámetro=30, largo=120 | Sólido cilíndrico sin error |
| T-61 | Eje | Chaflán en ambos extremos | Sólido válido; volumen < cilindro nominal |
| T-70 | Polea | Nominal: diámetro_ext=80, diámetro_int=20, ancho=30, prof_ranura=8 | Sólido con perfil de revolución sin error |
| T-71 | Polea | Ranura más profunda que el radio disponible | Rechazado con mensaje claro |
| T-80 | Riel | Nominal: perfil=T, largo=200 | Sólido extruido sin error |
| T-90 | Engranaje | Nominal: módulo=2, dientes=20, ancho=15 | Sólido generado por cq_gears sin error |
| T-91 | Engranaje | Dientes < 17 (mínimo sin socavado: z_min = 2/sin²(20°) ≈ 17,1 — geometría del perfil evolvente) | Rechazado con mensaje que indica z_min=17 y cita la fórmula |

---

## Tests de validación de JSON (Pydantic)

> Regla A-01: cada ID es único. T-100a/T-100b usan sufijo de letra porque sus assertions
> difieren (campo `agujero`/`vistas_iram` en prisma vs campos propios de cilindro).
> T-101, T-103, T-104, T-105, T-106 y T-109 usan `@pytest.mark.parametrize`.

| ID | Caso | Resultado esperado |
|---|---|---|
| T-100a | JSON válido completo — prisma | Pasa validación; `agujero=None`, `vistas_iram=False` |
| T-100b | JSON válido completo — cilindro | Pasa validación; campos numéricos correctos |
| T-101 | Campo obligatorio faltante (prisma y cilindro) | Rechazado con campo identificado (parametrize) |
| T-102 | Tipo incorrecto (string en campo numérico) | Rechazado con campo identificado |
| T-103 | Valor negativo en campo numérico (prisma y cilindro) | Rechazado antes de construir (parametrize) |
| T-104 | Valor NaN o infinito (prisma, agujero, cilindro) | Rechazado antes de construir (parametrize) |
| T-105 | Valor cero en dimensión (prisma y agujero) | Rechazado antes de construir (parametrize) |
| T-106 | Campos extra no definidos (prisma y agujero) | Rechazado (extra='forbid', parametrize) |
| T-107 | Figura desconocida | Rechazado antes de construir |
| T-108 | Sistema de representación desconocido | Rechazado antes de construir |
| T-109 | Pydantic v2 acepta NaN/inf/-inf sin validator | Acepta sin error (parametrize) |

---

## Tests de exportación

| ID | Caso | Resultado esperado |
|---|---|---|
| T-110 | Exportar STL de prisma rectangular | Archivo `.stl` válido, tamaño > 0, volumen dentro de ±0,5 % de 240 000 mm³ |
| T-111 | Exportar STEP de prisma rectangular | Archivo `.step` válido, tamaño > 0 |
| T-112 | Exportar SVG de vistas IRAM | Archivo `.svg` con tres vistas, tamaño > 0 |
| T-113 | Convertir SVG a PNG | Archivo `.png` válido, dimensiones > 0 |
| T-114 | Convertir SVG a JPG | Archivo `.jpg` válido |
| T-115 | Convertir SVG a WebP | Archivo `.webp` válido |

---

## Tests de representaciones — invariantes geométricos

### Vistas IRAM (ISO E)

| ID | Invariante | Verificación |
|---|---|---|
| T-120 | Planta debajo del alzado | origen_Y(planta) > origen_Y(alzado) + alto_alzado en el SVG |
| T-121 | Perfil a la derecha del alzado | origen_X(perfil) > origen_X(alzado) + ancho_alzado en el SVG |
| T-122 | Alzado y planta comparten ancho (X) | extensión_X(alzado) = extensión_X(planta) ±0,001 |
| T-123 | Alzado y perfil comparten altura (Z) | extensión_Z(alzado) = extensión_Z(perfil) ±0,001 |
| T-124 | Planta y perfil comparten profundidad (Y) | extensión_Y(planta) = extensión_Y(perfil) ±0,001 |

### Sistema de Monge

| ID | Invariante | Verificación |
|---|---|---|
| T-130 | Línea de tierra presente | elemento SVG `id="linea-tierra"` existe |
| T-131 | Alzado arriba, planta abajo | origen_Y(alzado) < origen_Y(planta) en el SVG |
| T-132 | Líneas de referencia perpendiculares | ángulo de cada línea de referencia con la línea de tierra = 90° ±0,1° |
| T-133 | Distancia a línea de tierra = Z (cota en alzado) | para prisma de alto=40: distancia medida en SVG = 40 unidades ±0,001 |
| T-134 | Distancia a línea de tierra = Y (alejamiento en planta) | para prisma con ancho=60 (Y=60): distancia medida en SVG = 60 unidades; `isclose(medido, 60, rel_tol=1e-6)` |

### Isométrica

| ID | Invariante | Verificación |
|---|---|---|
| T-140 | Ejes a 120° entre sí | ángulo entre cada par de ejes = 120° ±0,5° |
| T-141 | Escala 1:1 | arista conocida de 100 mm representada como 100 unidades SVG ±0,001 |

---

## Tests de sinónimos de sistemas de representación

| ID | Caso | Resultado esperado |
|---|---|---|
| T-145 | "Monge" | Resuelve a sistema de Monge |
| T-146 | "Monje" | Resuelve a sistema de Monge |
| T-147 | "diédrico" | Resuelve a sistema de Monge |
| T-148 | "vistas" | Resuelve a vistas IRAM |
| T-149 | "isométrica" | Resuelve a isométrica |

---

## Tests del formulario sin IA

> Estos tests usan un **conector falso** que devuelve un JSON fijo (no la IA real), para cumplir con A-07.

| ID | Caso | Resultado esperado |
|---|---|---|
| T-150 | JSON del conector falso y JSON ingresado manualmente con los mismos parámetros producen el mismo STL | Archivos STL idénticos (mismo hash) |
| T-151 | Formulario con campo vacío obligatorio | No genera; lista los campos faltantes |
| T-152 | Formulario con IA deshabilitada (conector nulo) | Funciona igual; formulario arranca vacío |

---

## Tests del historial

| ID | Caso | Resultado esperado |
|---|---|---|
| T-160 | Guardar proyecto | Aparece en la lista de historial |
| T-161 | Reabrir proyecto | Carga parámetros y archivos del proyecto correctamente |
| T-162 | Borrar proyecto | Pide confirmación explícita; tras confirmar, el proyecto se mueve a la Papelera de Windows (no borrado permanente); desaparece de la lista |

---

## Tests de seguridad

| ID | Caso | Resultado esperado |
|---|---|---|
| T-170 | Archivo renombrado (.exe con extensión .png) | Rechazado al verificar contenido real (no solo extensión) |
| T-171 | Imagen que supera el tamaño máximo | Rechazada con mensaje claro antes de enviar a la IA |
| T-172 | Nombre de archivo de salida con path traversal (`../../etc/passwd`) | La app genera su propio nombre; el input del docente no afecta la ruta |
| T-173 | App escucha solo en 127.0.0.1 | Una petición desde otra IP (o desde 0.0.0.0) es rechazada o no llega |
| T-174 | Log JSON no guarda imagen | El log del pedido contiene nombre y hash de imagen, no los bytes |
| T-175 | No existe `eval` ni `exec` en el código fuente del núcleo | Ruff con reglas S307 (`eval`) y S102 (`exec`) habilitadas no reporta ningún hallazgo en `src/` |

---

## Lista de tests del MVP

Los siguientes tests deben pasar para considerar el MVP completo:

**Recetas**: T-01, T-02, T-03, T-04, T-05, T-10, T-11, T-12

**Pydantic**: T-100, T-101, T-102, T-103, T-104, T-105, T-107, T-108

**Exportación**: T-110, T-111, T-112, T-113

**Representaciones IRAM**: T-120, T-121, T-122, T-123, T-124

**Formulario**: T-150, T-151, T-152

---

## Notas de ejecución

Los tests del MVP se marcan con `@pytest.mark.mvp` en el código. Registrar el marker en `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = ["mvp: tests requeridos para el primer hito demostrable"]
```

```bash
# Ejecutar todos los tests con cobertura
pytest tests/ --tb=short -v --cov=src --cov-report=term-missing

# Solo el MVP
pytest -m mvp --tb=short -v

# Tests de mutación (antes de cerrar Fase 1)
mutmut run
mutmut results
```
