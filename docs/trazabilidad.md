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
| T-180 | 001/FR-010 | tests/e2e/test_formulario.py | `test_generar_usa_workspace_configurado` |
| T-181 | 001/FR-001 | tests/e2e/test_formulario.py | `test_formulario_campos_dinamicos_por_figura` |
| T-182 | 001/FR-013 | tests/e2e/test_formulario.py | `test_visor_3d_recibe_ruta_stl_valida` |
| T-183 | 001/FR-013 | tests/e2e/test_formulario.py | `test_formulario_tiene_visor_3d` |
| T-184 | 001/FR-001 | tests/e2e/test_formulario.py | `test_actualizar_campos_visibilidad_por_figura` |
| T-185 | 001/FR-013 | tests/e2e/test_formulario.py | `test_iniciar_autoriza_workspace_en_allowed_paths` |
| T-186 | 001/FR-013 | tests/e2e/test_formulario.py | `test_interfaz_usa_visor_html_threejs` |
| T-187 | 001/FR-013 | tests/e2e/test_formulario.py | `test_make_viewer_html_contiene_ruta_stl` |
| T-188 | 001/FR-013 | tests/e2e/test_formulario.py | `test_make_viewer_html_usa_iframe_srcdoc` |
| T-190 | 001/FR-013 | tests/e2e/test_formulario.py | `test_make_viewer_html_usa_urls_absolutas` |
| T-191 | 001/FR-013 | tests/e2e/test_formulario.py | `test_iniciar_llama_set_static_paths` |
| T-193 | 001/FR-014 | tests/e2e/test_proyecto.py | `test_generar_guarda_proyecto_json` |
| T-194 | 001/FR-014 | tests/e2e/test_proyecto.py | `test_interfaz_tiene_descarga_stl_step` |
| T-195 | 001/FR-014 | tests/e2e/test_proyecto.py | `test_cargar_proyecto_json_devuelve_params` |
| T-196 | 001/FR-014 | tests/e2e/test_proyecto.py | `test_round_trip_proyecto_mismo_hash` |
| T-197 | 001/FR-004 | tests/unit/test_recipes_prisma.py | `test_prisma_zmin_es_cero` |
| T-198 | 001/FR-004 | tests/unit/test_recipes_cilindro.py | `test_cilindro_zmin_es_cero` |
| T-200 | 001/FR-020 | tests/unit/test_varios_agujeros.py | `test_t200_operaciones_lista_vacia` |
| T-201 | 001/FR-020 | tests/unit/test_varios_agujeros.py | `test_t201_limite_21_operaciones` |
| T-202 | 001/FR-020 | tests/unit/test_varios_agujeros.py | `test_t202_compatibilidad_formato_viejo` |
| T-203 | 001/FR-020 | tests/unit/test_varios_agujeros.py | `test_t203_dos_agujeros_sin_superposicion` |
| T-204 | 001/FR-020 | tests/unit/test_varios_agujeros.py | `test_t204_dos_agujeros_superpuestos_rechazado` |
| T-205 | 001/FR-020 | tests/unit/test_varios_agujeros.py | `test_t205_agujeros_caras_distintas_aceptado` |
| T-206 | 001/FR-020 | tests/unit/test_varios_agujeros.py | `test_t206_volumen_dos_agujeros_pasantes` |
| T-207 | 001/FR-020 | tests/unit/test_varios_agujeros.py | `test_t207_cruce_ejes_no_dentro_del_solido` |
| T-208 | 001/FR-020 | tests/unit/test_varios_agujeros.py | `test_t208_interfaz_tiene_tabla_agujeros` |
| T-209 | 001/FR-020 | tests/unit/test_varios_agujeros.py | `test_t209_tabla_a_operaciones_convierte_filas` |
| T-210 | 001/FR-020 | tests/unit/test_varios_agujeros.py | `test_t210_agregar_y_quitar_fila` |
| T-211 | 001/FR-020 | tests/unit/test_varios_agujeros.py | `test_t211_compatibilidad_cara_frontal` |
| T-212 | 001/FR-020 | tests/unit/test_varios_agujeros.py | `test_t212_generar_con_operaciones` |
| T-900 | 001/FR-005 | tests/fixtures/repo_ejemplo/tests/unit/test_schemas.py | `test_prisma_valido` |
| T-900 | 001/FR-006 | tests/fixtures/repo_ejemplo/tests/unit/test_schemas.py | `test_duplicado_mismo_tid` |
| T-901 | 001/FR-005 | tests/fixtures/repo_ejemplo/tests/unit/test_schemas.py | `test_campo_faltante` |
| T-902 | 001/FR-005 | tests/fixtures/repo_ejemplo/tests/unit/test_schemas.py | `test_valor_nan` |
| T-903 | 001/FR-001 | tests/fixtures/repo_ejemplo/tests/unit/test_schemas.py | `test_cubre_fr001` |
| T-904 | 001/FR-010 | tests/fixtures/repo_ejemplo/tests/unit/test_schemas.py | `test_fr010_distinto` |
| T-905 | 001/FR-011 | tests/fixtures/repo_ejemplo/tests/unit/test_schemas.py | `test_fr011_distinto` |
| T-906 | 001/FR-012 | tests/fixtures/repo_ejemplo/tests/unit/test_schemas.py | `test_fr012_distinto` |
| T-908 | 001/FR-001 | tests/fixtures/repo_ejemplo/tests/unit/test_schemas.py | `test_sin_linea_prueba` |

**Total tests trazados**: 69
**Feature IDs cubiertos**: 12
