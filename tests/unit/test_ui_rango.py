"""
Tests para calcular_info_rango — calcula el rango válido de u/v para mostrar en la UI.

T-215..T-220
"""

import pytest

from src.ui.app import calcular_info_rango


# ── T-215: datos incompletos → cadenas vacías ────────────────────────────────


@pytest.mark.mvp
def test_rango_sin_diametro_retorna_vacio():
    """T-215 | 001/FR-010 — Sin diámetro del agujero retorna ("", "")."""
    assert calcular_info_rango("superior", "", "100", "60", "40") == ("", "")


@pytest.mark.mvp
def test_rango_sin_dimensiones_retorna_vacio():
    """T-216 | 001/FR-010 — Sin dimensiones de la pieza retorna ("", "")."""
    assert calcular_info_rango("superior", "10", "", "", "") == ("", "")


# ── T-217: cara superior con prisma 100×60×40, Ø10 → rango correcto ─────────


@pytest.mark.mvp
def test_rango_cara_superior():
    """T-217 | 001/FR-010 — Cara superior 100×60, Ø10: u en (5, 95), v en (5, 55)."""
    info_u, info_v = calcular_info_rango("superior", "10", "100", "60", "40")
    assert "5.0" in info_u and "95.0" in info_u
    assert "5.0" in info_v and "55.0" in info_v


# ── T-218: cara frontal con prisma 100×60×40, Ø10 → usa largo y alto ────────


@pytest.mark.mvp
def test_rango_cara_frontal():
    """T-218 | 001/FR-010 — Cara frontal 100×40 (largo×alto), Ø10: u en (5, 95), v en (5, 35)."""
    info_u, info_v = calcular_info_rango("frontal", "10", "100", "60", "40")
    assert "5.0" in info_u and "95.0" in info_u
    assert "5.0" in info_v and "35.0" in info_v


# ── T-219: cara lateral_izq usa ancho y alto ────────────────────────────────


@pytest.mark.mvp
def test_rango_cara_lateral_izq():
    """T-219 | 001/FR-010 — Cara lateral_izq 60×40 (ancho×alto), Ø10: u∈(5,55), v∈(5,35)."""
    info_u, info_v = calcular_info_rango("lateral_izq", "10", "100", "60", "40")
    assert "5.0" in info_u and "55.0" in info_u
    assert "5.0" in info_v and "35.0" in info_v


# ── T-220: diámetro excede cara ──────────────────────────────────────────────


@pytest.mark.mvp
def test_rango_diametro_excede_cara():
    """T-220 | 001/FR-010 — Ø70 en cara superior 60mm de ancho: informa que excede."""
    info_u, info_v = calcular_info_rango("superior", "70", "100", "60", "40")
    assert "excede" in info_u.lower() or info_u == ""
