# Spec: MVP Ejemplo

## Functional Requirements

### FR-005: Validación de parámetros de entrada

Los parámetros recibidos del formulario deben ser validados antes de construir el modelo.

- Los valores NaN e infinito deben ser rechazados
- Los campos obligatorios faltantes deben identificarse
- Los campos extra no definidos deben ser rechazados

### FR-004: Generación de modelo 3D

Dado un JSON válido, la aplicación genera un sólido 3D sin errores.
