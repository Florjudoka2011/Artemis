# Matriz de Trazabilidad — Artemis MVP

_Generado automáticamente por `scripts/gen_traceability.py`_

| Test ID | Feature ID(s) | Archivo | Función |
|---------|---------------|---------|---------|
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
| T-900 | 001/FR-005 | tests/fixtures/repo_ejemplo/tests/unit/test_schemas.py | `test_prisma_valido` |
| T-900 | 001/FR-006 | tests/fixtures/repo_ejemplo/tests/unit/test_schemas.py | `test_duplicado_mismo_tid` |
| T-901 | 001/FR-005 | tests/fixtures/repo_ejemplo/tests/unit/test_schemas.py | `test_campo_faltante` |
| T-902 | 001/FR-005 | tests/fixtures/repo_ejemplo/tests/unit/test_schemas.py | `test_valor_nan` |
| T-903 | 001/FR-001 | tests/fixtures/repo_ejemplo/tests/unit/test_schemas.py | `test_cubre_fr001` |
| T-904 | 001/FR-010 | tests/fixtures/repo_ejemplo/tests/unit/test_schemas.py | `test_fr010_distinto` |
| T-905 | 001/FR-011 | tests/fixtures/repo_ejemplo/tests/unit/test_schemas.py | `test_fr011_distinto` |
| T-906 | 001/FR-012 | tests/fixtures/repo_ejemplo/tests/unit/test_schemas.py | `test_fr012_distinto` |
| T-908 | 001/FR-001 | tests/fixtures/repo_ejemplo/tests/unit/test_schemas.py | `test_sin_linea_prueba` |

**Total tests trazados**: 20
**Feature IDs cubiertos**: 6

