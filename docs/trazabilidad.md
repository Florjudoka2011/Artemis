# Matriz de Trazabilidad — Artemis MVP

_Generado automáticamente por `scripts/gen_traceability.py`_

| Test ID | Feature ID(s) | Archivo | Función |
|---------|---------------|---------|---------|
| T-01 | 001/FR-004 | tests/unit/test_recipes_prisma.py | `test_prisma_nominal` |
| T-02 | 001/FR-005 | tests/unit/test_recipes_prisma.py | `test_prisma_parametro_cero` |
| T-03 | 001/FR-005 | tests/unit/test_recipes_prisma.py | `test_prisma_parametro_negativo` |
| T-10 | 001/FR-004 | tests/unit/test_recipes_cilindro.py | `test_cilindro_nominal` |
| T-100a | 001/FR-005 | tests/unit/test_schemas.py | `test_prisma_valido_completo` |
| T-100b | 001/FR-005 | tests/unit/test_schemas.py | `test_cilindro_valido_completo` |
| T-101 | 001/FR-005 | tests/unit/test_schemas.py | `test_campo_faltante` |
| T-102 | 001/FR-005 | tests/unit/test_schemas.py | `test_tipo_incorrecto_largo` |
| T-103 | 001/FR-005 | tests/unit/test_schemas.py | `test_valor_negativo` |
| T-104 | 001/FR-005 | tests/unit/test_schemas.py | `test_nan_infinito_rechazado` |
| T-105 | 001/FR-005 | tests/unit/test_schemas.py | `test_valor_cero_rechazado` |
| T-106 | 001/FR-005 | tests/unit/test_schemas.py | `test_campo_extra_rechazado` |
| T-107 | 001/FR-005 | tests/unit/test_schemas.py | `test_figura_tipo_desconocida` |
| T-108 | 001/FR-005 | tests/unit/test_schemas.py | `test_cara_agujero_desconocida` |
| T-109 | 001/FR-005 | tests/unit/test_pydantic_nan_behavior.py | `test_pydantic_v2_acepta_valor_especial_sin_validator` |
| T-110 | 001/FR-006 | tests/integration/test_export.py | `test_exportar_stl` |
| T-111 | 001/FR-006 | tests/integration/test_export.py | `test_exportar_step` |
| T-150 | 001/FR-009 | tests/e2e/test_formulario.py | `test_stl_deterministico` |
| T-151 | 001/FR-001 | tests/e2e/test_formulario.py | `test_formulario_campo_vacio` |
| T-152 | 001/FR-009 | tests/e2e/test_formulario.py | `test_formulario_sin_ia` |
| T-153 | 001/FR-010 | tests/e2e/test_formulario.py | `test_crear_workspace_crea_directorio` |
| T-154 | 001/FR-011 | tests/e2e/test_formulario.py | `test_generar_prisma_valido_produce_archivos` |
| T-155 | 001/FR-004 | tests/e2e/test_formulario.py | `test_generar_cilindro_valido_produce_archivos` |
| T-156 | 001/FR-003 | tests/e2e/test_formulario.py | `test_formulario_tiene_checkbox_vistas_iram` |
| T-158 | 001/FR-003 | tests/e2e/test_formulario.py | `test_generar_acepta_vistas_iram` |
| T-159 | 001/FR-005 | tests/e2e/test_formulario.py | `test_generar_prisma_parametro_invalido_retorna_error` |
| T-160 | 001/FR-001 | tests/e2e/test_formulario.py | `test_formulario_cilindro_campo_vacio` |
| T-161 | 001/FR-005 | tests/e2e/test_formulario.py | `test_generar_cilindro_parametro_invalido_retorna_error` |
| T-162 | 001/FR-001 | tests/e2e/test_formulario.py | `test_generar_figura_desconocida_retorna_error` |
| T-173 | 001/FR-010 | tests/e2e/test_formulario.py | `test_iniciar_usa_host_y_puerto_seguros` |
| T-900 | 001/FR-005 | tests/fixtures/repo_ejemplo/tests/unit/test_schemas.py | `test_prisma_valido` |
| T-900 | 001/FR-006 | tests/fixtures/repo_ejemplo/tests/unit/test_schemas.py | `test_duplicado_mismo_tid` |
| T-901 | 001/FR-005 | tests/fixtures/repo_ejemplo/tests/unit/test_schemas.py | `test_campo_faltante` |
| T-902 | 001/FR-005 | tests/fixtures/repo_ejemplo/tests/unit/test_schemas.py | `test_valor_nan` |
| T-903 | 001/FR-001 | tests/fixtures/repo_ejemplo/tests/unit/test_schemas.py | `test_cubre_fr001` |
| T-904 | 001/FR-010 | tests/fixtures/repo_ejemplo/tests/unit/test_schemas.py | `test_fr010_distinto` |
| T-905 | 001/FR-011 | tests/fixtures/repo_ejemplo/tests/unit/test_schemas.py | `test_fr011_distinto` |
| T-906 | 001/FR-012 | tests/fixtures/repo_ejemplo/tests/unit/test_schemas.py | `test_fr012_distinto` |
| T-908 | 001/FR-001 | tests/fixtures/repo_ejemplo/tests/unit/test_schemas.py | `test_sin_linea_prueba` |

**Total tests trazados**: 39
**Feature IDs cubiertos**: 9

