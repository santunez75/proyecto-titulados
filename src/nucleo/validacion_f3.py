"""Reglas de validacion del nucleo algoritmico.

Reutiliza el motor de reglas de la Fase 2 (``src.validacion``): ``Regla`` y
``ValidadorDataset`` son genericos respecto del objeto que evaluan, asi que
aqui reciben un diccionario con los artefactos de la Fase 3 (dataset, cohorte,
arbol, resultado de modelacion, matrices) en lugar de un DataFrame. Es un
ejemplo de reutilizacion por composicion entre fases.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from ..validacion import Regla, ValidadorDataset
from .metricas import MediaSobreduracion, TasaOportuna


def _regla_cohorte_y_arbol(ctx: dict[str, Any]) -> tuple[bool, str]:
    n_cohorte, n_arbol = len(ctx["cohorte"]), ctx["arbol"].total()
    return n_cohorte == n_arbol, f"cohorte={n_cohorte:,}, arbol.total()={n_arbol:,}"


def _regla_hojas_suman_total(ctx: dict[str, Any]) -> tuple[bool, str]:
    arbol = ctx["arbol"]
    suma = sum(h.total() for h in arbol.hojas())
    return suma == arbol.total(), f"suma de hojas={suma:,}, total={arbol.total():,}"


def _regla_metrica_composite(ctx: dict[str, Any]) -> tuple[bool, str]:
    media = MediaSobreduracion()
    a, b = ctx["arbol"].calcular(media), ctx["cohorte"].calcular(media)
    return abs(a - b) < 1e-9, f"media via arbol={a:.6f}, via cohorte={b:.6f}"


def _regla_tasa_oportuna_coherente(ctx: dict[str, Any]) -> tuple[bool, str]:
    tasa_objetos = ctx["cohorte"].calcular(TasaOportuna())
    tasa_df = 100 * float(ctx["df"]["titulacion_oportuna"].mean())
    return abs(tasa_objetos - tasa_df) < 1.0, (
        f"objetos={tasa_objetos:.2f} %, dataset completo={tasa_df:.2f} % (tolerancia 1 punto por muestreo)"
    )


def _regla_convergencia(ctx: dict[str, Any]) -> tuple[bool, str]:
    r = ctx["resultado"]
    dif = float(np.abs(r.lineal_gd.pesos - r.lineal_cerrada.pesos).max())
    return dif < 0.05, f"diferencia maxima GD vs. cerrada = {dif:.4f}"


def _regla_perdida_decrece(ctx: dict[str, Any]) -> tuple[bool, str]:
    h = ctx["resultado"].lineal_gd.historial_perdida
    return h[-1] < h[0], f"ECM inicial={h[0]:.4f}, final={h[-1]:.4f}, iteraciones={len(h)}"


def _regla_matrices(ctx: dict[str, Any]) -> tuple[bool, str]:
    X_ent, X_pru = ctx["X_ent"], ctx["X_pru"]
    ok = (not np.isnan(X_ent).any()) and (not np.isnan(X_pru).any()) and X_ent.shape[1] == X_pru.shape[1]
    return ok, f"entrenamiento {X_ent.shape}, prueba {X_pru.shape}, sin NaN={ok}"


def _regla_metricas_finitas(ctx: dict[str, Any]) -> tuple[bool, str]:
    m = ctx["resultado"].metricas
    valores = [v for d in m.values() for v in d.values()]
    return all(np.isfinite(valores)), f"{len(valores)} metricas, todas finitas={all(np.isfinite(valores))}"


def _regla_r2_positivo(ctx: dict[str, Any]) -> tuple[bool, str]:
    r2 = ctx["resultado"].metricas["lineal_gd_prueba"]["r2"]
    return r2 > 0, f"R2 en prueba = {r2:.4f}"


def validador_nucleo() -> ValidadorDataset:
    """Validador con las reglas de coherencia interna y con la Fase 2."""
    return ValidadorDataset(
        [
            Regla("cohorte_y_arbol", "La jerarquia contiene exactamente los titulados de la cohorte.", _regla_cohorte_y_arbol),
            Regla("hojas_suman_total", "Las hojas del arbol suman el total de la raiz (recursion correcta).", _regla_hojas_suman_total),
            Regla("metrica_composite", "Una metrica via el arbol coincide con la misma via la cohorte.", _regla_metrica_composite),
            Regla("tasa_oportuna_coherente", "La tasa de titulacion oportuna sobre objetos coincide con la de F2.", _regla_tasa_oportuna_coherente),
            Regla("convergencia_gd", "El descenso de gradiente converge a la solucion cerrada.", _regla_convergencia),
            Regla("perdida_decrece", "La perdida final es menor que la inicial.", _regla_perdida_decrece),
            Regla("matrices_modelacion", "Las matrices no tienen NaN y comparten columnas.", _regla_matrices),
            Regla("metricas_finitas", "Todas las metricas de desempeno son numeros finitos.", _regla_metricas_finitas),
            Regla("r2_positivo", "El modelo lineal explica varianza en el conjunto de prueba.", _regla_r2_positivo, critica=False),
        ]
    )
