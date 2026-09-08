"""Motor de validacion del dataset analitico.

La verificacion no se deja a inspecciones visuales sueltas: se implementa como
un pequeno motor de reglas orientado a objetos. Cada regla es un objeto con
nombre, descripcion, severidad y una funcion que recibe el DataFrame y devuelve
un veredicto con su detalle. El validador las ejecuta todas y entrega una tabla
de resultados, que es la evidencia de verificacion de la Fase 2.

Uso tipico
----------
>>> validador = validador_estandar()
>>> reporte = validador.ejecutar(df)
>>> validador.aprobado
True
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import pandas as pd

from . import config

# Una regla recibe el DataFrame y devuelve (cumple, detalle legible).
FuncionRegla = Callable[[pd.DataFrame], tuple[bool, str]]


@dataclass
class Regla:
    """Regla de validacion individual.

    Atributos
    ---------
    nombre : str
        Identificador corto de la regla.
    descripcion : str
        Que se esta comprobando, en lenguaje natural.
    funcion : FuncionRegla
        Comprobacion propiamente tal.
    critica : bool
        Si es ``True``, su incumplimiento invalida el dataset; si es ``False``,
        se reporta como advertencia y el pipeline puede continuar.
    """

    nombre: str
    descripcion: str
    funcion: FuncionRegla
    critica: bool = True

    def evaluar(self, df: pd.DataFrame) -> dict[str, object]:
        """Ejecuta la regla capturando cualquier excepcion como incumplimiento."""
        try:
            cumple, detalle = self.funcion(df)
        except Exception as exc:  # la validacion nunca debe abortar el pipeline
            cumple, detalle = False, f"Error al evaluar: {type(exc).__name__}: {exc}"
        return {
            "regla": self.nombre,
            "descripcion": self.descripcion,
            "severidad": "critica" if self.critica else "advertencia",
            "estado": "PASA" if cumple else ("FALLA" if self.critica else "ADVIERTE"),
            "detalle": detalle,
        }


class ValidadorDataset:
    """Coleccion ejecutable de reglas de validacion."""

    def __init__(self, reglas: list[Regla] | None = None) -> None:
        self.reglas: list[Regla] = list(reglas) if reglas else []
        self.reporte: pd.DataFrame | None = None

    def registrar(self, regla: Regla) -> "ValidadorDataset":
        """Anade una regla y devuelve el propio validador (encadenable)."""
        self.reglas.append(regla)
        return self

    def ejecutar(self, df: pd.DataFrame) -> pd.DataFrame:
        """Evalua todas las reglas y guarda el reporte resultante."""
        self.reporte = pd.DataFrame([regla.evaluar(df) for regla in self.reglas])
        return self.reporte

    @property
    def aprobado(self) -> bool:
        """Verdadero si ninguna regla critica fallo."""
        if self.reporte is None:
            raise RuntimeError("Debe ejecutar el validador antes de consultar el estado.")
        return not (self.reporte["estado"] == "FALLA").any()

    def resumen(self) -> str:
        """Texto de una linea con el balance de la ejecucion."""
        if self.reporte is None:
            raise RuntimeError("Debe ejecutar el validador antes de pedir el resumen.")
        conteo = self.reporte["estado"].value_counts()
        return (
            f"{conteo.get('PASA', 0)} reglas aprobadas, "
            f"{conteo.get('ADVIERTE', 0)} advertencias, "
            f"{conteo.get('FALLA', 0)} fallas criticas."
        )


# --- Reglas concretas ------------------------------------------------------


def _regla_no_vacio(df: pd.DataFrame) -> tuple[bool, str]:
    return len(df) > 0, f"{len(df):,} filas en el dataset analitico."


def _regla_columnas_derivadas(df: pd.DataFrame) -> tuple[bool, str]:
    esperadas = {
        "duracion_real_sem",
        "sobreduracion_sem",
        "indice_duracion",
        "titulacion_oportuna",
        "categoria_rezago",
        "edad_titulacion",
        "genero",
    }
    faltantes = esperadas - set(df.columns)
    return not faltantes, (
        "Todas las variables derivadas presentes."
        if not faltantes
        else f"Faltan: {sorted(faltantes)}"
    )


def _regla_sin_nulos_criticos(df: pd.DataFrame) -> tuple[bool, str]:
    criticas = ["duracion_real_sem", "sobreduracion_sem", "dur_total_carr", "cat_periodo"]
    nulos = {c: int(df[c].isna().sum()) for c in criticas if c in df.columns}
    con_nulos = {c: n for c, n in nulos.items() if n}
    return not con_nulos, (
        "Sin nulos en las columnas criticas." if not con_nulos else f"Nulos: {con_nulos}"
    )


def _regla_rango_duracion(df: pd.DataFrame) -> tuple[bool, str]:
    fuera = int(
        (~df["duracion_real_sem"].between(
            config.DURACION_REAL_MIN, config.DURACION_REAL_MAX
        )).sum()
    )
    return fuera == 0, (
        f"Duracion real dentro de [{config.DURACION_REAL_MIN}, "
        f"{config.DURACION_REAL_MAX}] semestres; {fuera} fuera de rango."
    )


def _regla_rango_edad(df: pd.DataFrame) -> tuple[bool, str]:
    fuera = int((~df["edad_titulacion"].between(config.EDAD_MIN, config.EDAD_MAX)).sum())
    return fuera == 0, (
        f"Edad de titulacion dentro de [{config.EDAD_MIN}, {config.EDAD_MAX}]; "
        f"{fuera} fuera de rango."
    )


def _regla_dominio_genero(df: pd.DataFrame) -> tuple[bool, str]:
    valores = set(df["genero"].dropna().unique())
    validos = set(config.MAPA_GENERO.values())
    return valores <= validos, f"Valores observados: {sorted(valores)}"


def _regla_coherencia_aritmetica(df: pd.DataFrame) -> tuple[bool, str]:
    reconstruida = df["sobreduracion_sem"] + df["dur_total_carr"]
    discrepancias = int((reconstruida != df["duracion_real_sem"]).sum())
    return discrepancias == 0, (
        f"sobreduracion + duracion teorica = duracion real en "
        f"{len(df) - discrepancias:,} de {len(df):,} filas."
    )


def _regla_cobertura_anios(df: pd.DataFrame) -> tuple[bool, str]:
    presentes = sorted(int(a) for a in df["cat_periodo"].unique())
    faltantes = sorted(set(config.ANIOS) - set(presentes))
    return not faltantes, f"Anios presentes: {presentes}"


def _regla_titulo_posterior_ingreso(df: pd.DataFrame) -> tuple[bool, str]:
    invalidos = int((df["anio_titulo"] < df["anio_ing_carr_ori"]).sum())
    return invalidos == 0, f"{invalidos} titulos con fecha anterior al ingreso."


def _regla_periodo_igual_anio_titulo(df: pd.DataFrame) -> tuple[bool, str]:
    diferencias = int((df["cat_periodo"] != df["anio_titulo"]).sum())
    porcentaje = round(100 * diferencias / max(len(df), 1), 2)
    return diferencias == 0, (
        f"{diferencias:,} filas ({porcentaje}%) donde el anio del proceso no "
        "coincide con el anio de la fecha del titulo."
    )


def _regla_sin_duplicados(df: pd.DataFrame) -> tuple[bool, str]:
    claves = ["cat_periodo", "mrun", "cod_carrera", "fecha_obtencion_titulo"]
    presentes = [c for c in claves if c in df.columns]
    base = df.dropna(subset=["mrun"]) if "mrun" in df.columns else df
    duplicados = int(base.duplicated(subset=presentes).sum())
    return duplicados == 0, f"{duplicados} duplicados sobre {' + '.join(presentes)}."


def validador_estandar() -> ValidadorDataset:
    """Construye el validador con el conjunto de reglas del proyecto."""
    return ValidadorDataset(
        [
            Regla("dataset_no_vacio", "El dataset contiene registros.", _regla_no_vacio),
            Regla(
                "columnas_derivadas",
                "Existen todas las variables construidas en la transformacion.",
                _regla_columnas_derivadas,
            ),
            Regla(
                "sin_nulos_criticos",
                "Las columnas indispensables no tienen valores faltantes.",
                _regla_sin_nulos_criticos,
            ),
            Regla(
                "rango_duracion_real",
                "La duracion real reconstruida es plausible.",
                _regla_rango_duracion,
            ),
            Regla(
                "rango_edad",
                "La edad de titulacion es plausible.",
                _regla_rango_edad,
            ),
            Regla(
                "dominio_genero",
                "La variable genero solo toma los valores del esquema SIES.",
                _regla_dominio_genero,
            ),
            Regla(
                "coherencia_aritmetica",
                "La sobreduracion es consistente con sus componentes.",
                _regla_coherencia_aritmetica,
            ),
            Regla(
                "cobertura_anios",
                "Estan representados los seis anios de la ventana de analisis.",
                _regla_cobertura_anios,
            ),
            Regla(
                "titulo_posterior_ingreso",
                "Ningun titulo antecede al ingreso a la carrera.",
                _regla_titulo_posterior_ingreso,
            ),
            Regla(
                "sin_duplicados",
                "No hay registros repetidos de estudiante-carrera-fecha.",
                _regla_sin_duplicados,
            ),
            Regla(
                "periodo_igual_anio_titulo",
                "El anio del proceso coincide con el anio de la fecha del titulo.",
                _regla_periodo_igual_anio_titulo,
                critica=False,
            ),
        ]
    )
