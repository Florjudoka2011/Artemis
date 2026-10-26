# Evidencia E2E — US2 Posición de Agujero (coordenadas de borde)

**Fecha:** 2026-10-26
**Intérprete:** `.venv\Scripts\python.exe` → Python 3.12.0
**Rama:** us2-agujero-posicion
**Commit:** c15c4197 (feat: tests T-215..T-220 para calcular_info_rango + cobertura 90%)

---

## Caso de prueba: bug original del spec

**Parámetros:** prisma 200×67×200, cara frontal, Ø10, u=100, v=190

**Antes del fix (comportamiento incorrecto):**
- El agujero aparecía cerca de z=90 en vez de z=190
- La validación fallaba en v≈94 aunque había espacio físico

**Después del fix (esperado):**
- El agujero debe estar en z=190 (v=190 desde la base)
- u=100 en cara frontal de 200mm de largo → x=0 (centro)

---

## Paso 1 — Generación de la pieza

```
Comando: src.ui.app.generar(largo='200', ancho='67', alto='200',
         tiene_agujero=True, diametro_agujero='10',
         cara_agujero='frontal', u_agujero='100', v_agujero='190',
         tipo_agujero='pasante')

Salida:
  Mensaje: Generado: C:\Artemis\workspace\prisma_rectangular_20261026_092459\prisma_rectangular.stl, ...
  STL: C:\Artemis\workspace\prisma_rectangular_20261026_092459\prisma_rectangular.stl
```

## Paso 2 — Verificación geométrica

```
Comando:
  solido.val().isInside(cq.Vector(0, 0, 190))  # eje del agujero en z=190
  solido.val().isInside(cq.Vector(7, 0, 190))  # punto adyacente (radio=5, a 7mm del eje)

Salida:
  Punto (0,0,190) en agujero (esperado=False): False  ✓
  Punto (7,0,190) en solido  (esperado=True ): True   ✓
  OK
```

**Resultado:** El agujero queda exactamente en z=190, no en z=90 como antes del fix.

## Paso 3 — Suite MVP completa

```
Comando: .venv\Scripts\python.exe -m pytest -m mvp -q --tb=no
Salida:  140 passed, 1 deselected, 1 warning in 20.29s
```

## Paso 4 — evidencia.py (todas las etapas)

```
pytest:      140 passed — OK
cobertura:   90.52% ≥ 90% — OK
mutacion:    0 supervivientes (4/4 mutantes muertos) — OK
trazabilidad: 91 tests trazados, 12 feature IDs — OK
```

---

## UI — Nuevas etiquetas y rangos

La interfaz muestra:
- Label: **"u — desde borde izquierdo (mm)"** (antes: "Desplazamiento u (mm)")
- Label: **"v — desde base (mm)"** (antes: "Desplazamiento v (mm)")
- Info dinámica bajo cada campo: **"Rango válido: X.X – Y.Y mm"**
  (calculado en tiempo real al cambiar cara, diámetro o dimensiones de la pieza)

---

## Confirmación visual pendiente

El usuario debe confirmar en pantalla (http://127.0.0.1:7860) que:
1. Al ingresar largo=200, ancho=67, alto=200, cara=frontal, Ø=10, u=100, v=190,
   los rangos válidos aparecen bajo u y v
2. El modelo 3D muestra el agujero cerca del tope de la cara frontal (z≈190)
3. La validación acepta v=190 sin error (antes fallaba en v≈94)

**Ruta STL generado:** C:\Artemis\workspace\prisma_rectangular_20261026_092459\prisma_rectangular.stl
