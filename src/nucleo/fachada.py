"""Punto de entrada unico del nucleo (patron Facade).

El notebook de la Fase 3 no debe conocer los detalles de como se construye una
cohorte, se arma la jerarquia o se prepara la matriz de modelacion. La fachada
expone unas pocas operaciones de alto nivel y coordina internamente los
modulos del nucleo, lo que reduce el acoplamiento entre la capa de
presentacion (notebooks, informe) y la logica.

Tambien resuelve la carga de datos con degradacion controlada: usa el
dataset analitico completo de la Fase 2 si existe y, si no, la muestra
versionada de 5.000 registros, avisando de ello. Asi el notebook corre en un
equipo sin los CSV originales.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .. import config
from .dominio import Cohorte
from .jerarquia import NIVELES_ESTANDAR, NodoJerarquia, construir_jerarquia
from .metricas import Metrica, metricas_estandar
from .modelos import RegresionLinealCerrada, RegresionLinealGD, RegresionLogisticaGD
from .preparacion import PreparadorModelacion, dividir_entrenamiento_prueba

VARIABLES_NUMERICAS: tuple[str, ...] = ("dur_total_carr", "edad_ingreso")
VARIABLES_CATEGORICAS: tuple[str, ...] = ("genero", "tipo_inst_1", "area_conocimiento", "modalidad")
OBJETIVO_REGRESION: str = "sobreduracion_sem"
OBJETIVO_CLASIFICACION: str = "titulacion_oportuna"


def cargar_datos(preferir_completo: bool = True) -> tuple[pd.DataFrame, str]:
    """Dataset analitico de la Fase 2, o la muestra versionada como respaldo."""
    if preferir_completo and config.PARQUET_LIMPIO.exists():
        return pd.read_parquet(config.PARQUET_LIMPIO), "completo"
    if config.MUESTRA_CSV.exists():
        warnings.warn(
            "No se encontro el dataset analitico completo; se usa la muestra de 5.000 "
            "registros. Ejecute `python -m src.pipeline` para regenerarlo.",
            stacklevel=2,
        )
        df = pd.read_csv(config.MUESTRA_CSV)
        for col in ("genero", "tipo_inst_1", "area_conocimiento", "modalidad", "nomb_inst",
                    "nomb_carrera", "region_sede"):
            df[col] = df[col].astype("category")
        return df, "muestra"
    raise FileNotFoundError(
        f"No existe {config.PARQUET_LIMPIO} ni {config.MUESTRA_CSV}; ejecute la Fase 2 primero."
    )


@dataclass
class ResultadoModelacion:
    """Contenedor de los modelos ajustados y sus metricas."""

    columnas: list[str]
    n_entrenamiento: int
    n_prueba: int
    lineal_gd: RegresionLinealGD
    lineal_cerrada: RegresionLinealCerrada
    logistica: RegresionLogisticaGD
    metricas: dict[str, dict[str, float]] = field(default_factory=dict)
    umbrales: pd.DataFrame | None = None
    exactitud_base: float = float("nan")

    def coeficientes(self) -> pd.DataFrame:
        """Pesos de ambos modelos lineales lado a lado, para verificar convergencia."""
        return pd.DataFrame(
            {
                "variable": self.columnas,
                "descenso_gradiente": self.lineal_gd.pesos.round(4),
                "solucion_cerrada": self.lineal_cerrada.pesos.round(4),
                "logistica": self.logistica.pesos.round(4),
            }
        ).assign(diferencia_abs=lambda t: (t["descenso_gradiente"] - t["solucion_cerrada"]).abs().round(5))


def evaluar_umbrales(y: np.ndarray, probabilidades: np.ndarray, umbrales: tuple[float, ...]) -> pd.DataFrame:
    """Metricas de clasificacion para varios umbrales de decision."""
    from .modelos import metricas_clasificacion

    filas = []
    for u in umbrales:
        m = metricas_clasificacion(y, (probabilidades >= u).astype(int))
        filas.append({"umbral": u, **{k: round(v, 3) for k, v in m.items() if k in ("exactitud", "precision", "sensibilidad", "f1")}})
    return pd.DataFrame(filas)


class NucleoAnalitico:
    """Fachada: carga, cohorte, jerarquia, metricas y modelacion en pocas llamadas."""

    def __init__(self, limite_cohorte: int | None = 300_000, semilla: int = 42) -> None:
        self._limite = limite_cohorte
        self._semilla = semilla
        self._df: pd.DataFrame | None = None
        self._origen: str = ""
        self._cohorte: Cohorte | None = None
        self._jerarquia: NodoJerarquia | None = None
        self._metricas: list[Metrica] = metricas_estandar()

    # --- datos ---------------------------------------------------------------
    @property
    def datos(self) -> pd.DataFrame:
        if self._df is None:
            self._df, self._origen = cargar_datos()
        return self._df

    @property
    def origen_datos(self) -> str:
        _ = self.datos
        return self._origen

    @property
    def metricas(self) -> list[Metrica]:
        return list(self._metricas)

    # --- objetos del dominio -------------------------------------------------
    @property
    def cohorte(self) -> Cohorte:
        if self._cohorte is None:
            self._cohorte = Cohorte.desde_dataframe(
                self.datos, limite=self._limite, nombre="pregrado_2020_2025", semilla=self._semilla
            )
        return self._cohorte

    @property
    def jerarquia(self) -> NodoJerarquia:
        if self._jerarquia is None:
            self._jerarquia = construir_jerarquia(self.cohorte, NIVELES_ESTANDAR)
        return self._jerarquia

    def resumen_por(self, atributo: str, minimo: int = 30) -> pd.DataFrame:
        return self.cohorte.tabla_por(atributo, self._metricas, minimo)

    def concentracion_rezago(self, metrica: Metrica | None = None, minimo: int = 200) -> pd.DataFrame:
        """Camino de maximo rezago por el arbol, un registro por nivel."""
        metrica = metrica or self._metricas[0]
        camino = self.jerarquia.descender_por_maximo(metrica, minimo)
        return pd.DataFrame(
            [{"nivel": n.nivel, "nombre": n.nombre, "titulados": n.total(),
              metrica.nombre: round(n.calcular(metrica), 3)} for n in camino]
        )

    # --- modelacion ----------------------------------------------------------
    def preparar_modelacion(
        self, limite: int | None = 200_000, proporcion_prueba: float = 0.2
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, PreparadorModelacion]:
        """Matriz de diseno escalada y codificada, partida en entrenamiento y prueba.

        Devuelve (X_ent, X_pru, y_reg_ent, y_reg_pru, y_cla_ent, y_cla_pru, preparador).
        """
        columnas = list(VARIABLES_NUMERICAS) + list(VARIABLES_CATEGORICAS) + [OBJETIVO_REGRESION, OBJETIVO_CLASIFICACION]
        base = self.datos[columnas].dropna()
        if limite is not None and limite < len(base):
            base = base.sample(limite, random_state=self._semilla)
        base = base.reset_index(drop=True)

        idx_ent, idx_pru = dividir_entrenamiento_prueba(len(base), proporcion_prueba, self._semilla)
        preparador = PreparadorModelacion(VARIABLES_NUMERICAS, VARIABLES_CATEGORICAS)
        X_ent = preparador.ajustar_transformar(base.iloc[idx_ent])
        X_pru = preparador.transformar(base.iloc[idx_pru])
        y_reg = base[OBJETIVO_REGRESION].to_numpy(dtype="float64")
        y_cla = base[OBJETIVO_CLASIFICACION].to_numpy(dtype="float64")
        return X_ent, X_pru, y_reg[idx_ent], y_reg[idx_pru], y_cla[idx_ent], y_cla[idx_pru], preparador

    def ajustar_modelos(
        self, limite: int | None = 200_000, iteraciones: int = 1500, tasa: float = 0.5
    ) -> ResultadoModelacion:
        X_ent, X_pru, yr_ent, yr_pru, yc_ent, yc_pru, prep = self.preparar_modelacion(limite)

        lineal_gd = RegresionLinealGD(tasa_aprendizaje=tasa, iteraciones=iteraciones).ajustar(X_ent, yr_ent)
        lineal_cerrada = RegresionLinealCerrada().ajustar(X_ent, yr_ent)
        logistica = RegresionLogisticaGD(tasa_aprendizaje=tasa, iteraciones=iteraciones).ajustar(X_ent, yc_ent)

        resultado = ResultadoModelacion(
            columnas=prep.nombres_columnas,
            n_entrenamiento=len(yr_ent), n_prueba=len(yr_pru),
            lineal_gd=lineal_gd, lineal_cerrada=lineal_cerrada, logistica=logistica,
        )
        resultado.metricas = {
            "lineal_gd_entrenamiento": lineal_gd.evaluar(X_ent, yr_ent),
            "lineal_gd_prueba": lineal_gd.evaluar(X_pru, yr_pru),
            "lineal_cerrada_prueba": lineal_cerrada.evaluar(X_pru, yr_pru),
            "logistica_entrenamiento": logistica.evaluar(X_ent, yc_ent),
            "logistica_prueba": logistica.evaluar(X_pru, yc_pru),
        }
        # La clase positiva (titulacion oportuna) es minoritaria (~19 %): el umbral
        # de decision determina el equilibrio entre precision y sensibilidad, y se
        # reporta junto con la linea base de predecir siempre la clase mayoritaria.
        probabilidades = logistica.predecir_probabilidad(X_pru)
        resultado.umbrales = evaluar_umbrales(yc_pru, probabilidades, (0.5, 0.4, 0.3, round(float(yc_ent.mean()), 2)))
        resultado.exactitud_base = float(max(yc_pru.mean(), 1 - yc_pru.mean()))
        return resultado
