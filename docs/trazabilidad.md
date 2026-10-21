# Matriz de Trazabilidad — Artemis MVP

_Generado automáticamente por `scripts/gen_traceability.py`_

| Test ID | Feature ID(s) | Archivo | Función |
|---------|---------------|---------|---------|
| T-100 | 001/FR-005 | tests/fixtures/repo_ejemplo/tests/unit/test_schemas.py | `test_prisma_valido` |
| T-100 | 001/FR-005 | tests/unit/test_schemas.py | `test_prisma_valido_completo` |
| T-100 | 001/FR-005 | tests/unit/test_schemas.py | `test_cilindro_valido_completo` |
| T-101 | 001/FR-005 | tests/fixtures/repo_ejemplo/tests/unit/test_schemas.py | `test_campo_faltante` |
| T-101 | 001/FR-005 | tests/unit/test_schemas.py | `test_campo_faltante_prisma` |
| T-101 | 001/FR-005 | tests/unit/test_schemas.py | `test_campo_faltante_cilindro` |
| T-102 | 001/FR-005 | tests/unit/test_schemas.py | `test_tipo_incorrecto_largo` |
| T-103 | 001/FR-005 | tests/unit/test_schemas.py | `test_valor_negativo_largo` |
| T-103 | 001/FR-005 | tests/unit/test_schemas.py | `test_valor_negativo_diametro` |
| T-104 | 001/FR-005 | tests/fixtures/repo_ejemplo/tests/unit/test_schemas.py | `test_valor_nan` |
| T-104 | 001/FR-005 | tests/unit/test_schemas.py | `test_valor_nan` |
| T-104 | 001/FR-005 | tests/unit/test_schemas.py | `test_valor_infinito` |
| T-104 | 001/FR-005 | tests/unit/test_schemas.py | `test_valor_nan_agujero_diametro` |
| T-104 | 001/FR-005 | tests/unit/test_schemas.py | `test_valor_nan_cilindro` |
| T-105 | 001/FR-005 | tests/unit/test_schemas.py | `test_valor_cero_alto` |
| T-105 | 001/FR-005 | tests/unit/test_schemas.py | `test_valor_cero_diametro_agujero` |
| T-106 | 001/FR-005 | tests/unit/test_schemas.py | `test_campo_extra_prisma` |
| T-106 | 001/FR-005 | tests/unit/test_schemas.py | `test_campo_extra_agujero` |
| T-107 | 001/FR-005 | tests/unit/test_schemas.py | `test_figura_tipo_desconocida` |
| T-108 | 001/FR-005 | tests/unit/test_schemas.py | `test_cara_agujero_desconocida` |
| T-109 | 001/FR-005 | tests/unit/test_pydantic_nan_behavior.py | `test_pydantic_v2_acepta_nan_sin_validator` |
| T-109 | 001/FR-005 | tests/unit/test_pydantic_nan_behavior.py | `test_pydantic_v2_acepta_inf_sin_validator` |
| T-109 | 001/FR-005 | tests/unit/test_pydantic_nan_behavior.py | `test_pydantic_v2_acepta_neg_inf_sin_validator` |
| T-201 | 001/FR-MCP | tests/unit/test_mcp_trazabilidad.py | `test_buscar_test_retorna_archivo_y_linea` |
| T-201b | 001/FR-MCP | tests/unit/test_mcp_trazabilidad.py | `test_buscar_test_retorna_ruta_relativa` |
| T-202 | 001/FR-MCP | tests/unit/test_mcp_trazabilidad.py | `test_buscar_test_id_inexistente` |
| T-203 | 001/FR-MCP | tests/unit/test_mcp_trazabilidad.py | `test_buscar_test_sin_id_en_docstring` |
| T-204 | 001/FR-MCP | tests/unit/test_mcp_trazabilidad.py | `test_funcion_bajo_test_usa_linea_prueba` |
| T-204b | 001/FR-MCP | tests/unit/test_mcp_trazabilidad.py | `test_funcion_bajo_test_sin_linea_prueba_devuelve_no_determinable` |
| T-205 | 001/FR-MCP | tests/unit/test_mcp_trazabilidad.py | `test_funcion_bajo_test_id_inexistente` |
| T-205b | 001/FR-MCP | tests/unit/test_mcp_trazabilidad.py | `test_funcion_bajo_test_ruta_relativa` |
| T-206 | 001/FR-MCP | tests/unit/test_mcp_trazabilidad.py | `test_requisito_formato_spec_kit` |
| T-206b | 001/FR-MCP | tests/unit/test_mcp_trazabilidad.py | `test_requisito_coincidencia_exacta_no_prefijo` |
| T-206c | 001/FR-MCP | tests/unit/test_mcp_trazabilidad.py | `test_requisito_busca_solo_en_su_spec` |
| T-207 | 001/FR-MCP | tests/unit/test_mcp_trazabilidad.py | `test_requisito_inexistente` |
| T-207b | 001/FR-MCP | tests/unit/test_mcp_trazabilidad.py | `test_requisito_ruta_relativa` |
| T-208 | 001/FR-MCP | tests/unit/test_mcp_trazabilidad.py | `test_estado_tareas_agrupa_correctamente` |
| T-208b | 001/FR-MCP | tests/unit/test_mcp_trazabilidad.py | `test_estado_tareas_sin_estado_bloqueado_fantasma` |
| T-208c | 001/FR-MCP | tests/unit/test_mcp_trazabilidad.py | `test_estado_tareas_incluye_criterio_en_resultado` |
| T-209 | 001/FR-MCP | tests/unit/test_mcp_trazabilidad.py | `test_ultima_evidencia_retorna_contenido` |
| T-209b | 001/FR-MCP | tests/unit/test_mcp_trazabilidad.py | `test_ultima_evidencia_considera_solo_archivos_con_fecha` |
| T-210 | 001/FR-MCP | tests/unit/test_mcp_trazabilidad.py | `test_ultima_evidencia_sin_archivos` |
| T-210b | 001/FR-MCP | tests/unit/test_mcp_trazabilidad.py | `test_ultima_evidencia_ruta_relativa` |
| T-211 | 001/FR-MCP | tests/unit/test_mcp_trazabilidad.py | `test_huecos_trazabilidad_detecta_test_sin_id` |
| T-212 | 001/FR-MCP | tests/unit/test_mcp_trazabilidad.py | `test_huecos_trazabilidad_detecta_req_sin_test` |
| T-212b | 001/FR-MCP | tests/unit/test_mcp_trazabilidad.py | `test_huecos_trazabilidad_detecta_formato_spec_kit` |
| T-212c | 001/FR-MCP | tests/unit/test_mcp_trazabilidad.py | `test_huecos_trazabilidad_control_global_explicito` |
| T-212d | 001/FR-MCP | tests/unit/test_mcp_trazabilidad.py | `test_huecos_trazabilidad_rutas_relativas` |

**Total tests trazados**: 48
**Feature IDs cubiertos**: 2

