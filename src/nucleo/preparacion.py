"""Preparacion de matrices para la modelacion: escalamiento y codificacion.

La Fase 2 dejo un dataset limpio y tipado; la modelacion exige ademas que las
variables numericas esten en escalas comparables (el descenso de gradiente
converge mal si una variable va de 1 a 24 y otra de 17 a 86) y que las
categoricas se conviertan en columnas numericas.

Todas las transformaciones comparten una interfaz (``Transformador``):
``ajustar`` aprende los parametros de los datos de entrenamiento y
``transformar`` los aplica. Esta separacion es lo que evita la fuga de
informacion: la media y la desviacion se calculan solo con el conjunto de
entrenamiento y luego se aplican, sin recalcular, al de prueba.

Herencia y polimorfismo son reales aqui: ``EscaladorEstandar`` y
``EscaladorMinMax`` heredan la validacion, la comprobacion de ajuste y
``ajustar_transformar`` de la clase base, y sobreescriben solo la formula.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

import numpy as np
import pandas as pd


class Transformador(ABC):
    """Interfaz comun: ajustar en entrenamiento, transformar en cualquier conjunto."""

    def __init__(self) -> None:
        self._ajustado = False
        self._n_columnas: int | None = None

    @property
    def ajustado(self) -> bool:
        return self._ajustado

    def ajustar(self, X: np.ndarray) -> "Transformador":
        X = self._validar(X, ajustando=True)
        self._aprender(X)
        self._n_columnas = X.shape[1]
        self._ajustado = True
        return self

    def transformar(self, X: np.ndarray) -> np.ndarray:
        if not self._ajustado:
            raise RuntimeError(f"{type(self).__name__} debe ajustarse antes de transformar")
        X = self._validar(X, ajustando=False)
        return self._aplicar(X)

    def ajustar_transformar(self, X: np.ndarray) -> np.ndarray:
        return self.ajustar(X).transformar(X)

    # --- ganchos que cada subclase implementa --------------------------------
    @abstractmethod
    def _aprender(self, X: np.ndarray) -> None: ...

    @abstractmethod
    def _aplicar(self, X: np.ndarray) -> np.ndarray: ...

    # --- comportamiento heredado ---------------------------------------------
    def _validar(self, X: np.ndarray, ajustando: bool) -> np.ndarray:
        X = np.asarray(X, dtype="float64")
        if X.ndim != 2:
            raise ValueError(f"se esperaba una matriz 2D; se recibio un arreglo de {X.ndim} dimensiones")
        if X.shape[0] == 0:
            raise ValueError("la matriz no tiene filas")
        if np.isnan(X).any():
            raise ValueError("la matriz contiene NaN; la limpieza de la Fase 2 debe aplicarse antes")
        if not ajustando and X.shape[1] != self._n_columnas:
            raise ValueError(
                f"se ajusto con {self._n_columnas} columnas y se intenta transformar {X.shape[1]}"
            )
        return X


class EscaladorEstandar(Transformador):
    """z = (x - media) / desviacion, por columna.

    Una columna constante tiene desviacion 0; se reemplaza por 1 para no dividir
    por cero (la columna queda en 0, que es la respuesta correcta: no aporta
    variacion).
    """

    def _aprender(self, X: np.ndarray) -> None:
        self.media_ = X.mean(axis=0)
        desviacion = X.std(axis=0)
        self.desviacion_ = np.where(desviacion == 0, 1.0, desviacion)

    def _aplicar(self, X: np.ndarray) -> np.ndarray:
        return (X - self.media_) / self.desviacion_

    def invertir(self, Z: np.ndarray) -> np.ndarray:
        """Recupera las unidades originales (util para interpretar coeficientes)."""
        if not self._ajustado:
            raise RuntimeError("el escalador no esta ajustado")
        return np.asarray(Z, dtype="float64") * self.desviacion_ + self.media_


class EscaladorMinMax(Transformador):
    """x' = (x - min) / (max - min), por columna, al intervalo [0, 1]."""

    def _aprender(self, X: np.ndarray) -> None:
        self.minimo_ = X.min(axis=0)
        rango = X.max(axis=0) - self.minimo_
        self.rango_ = np.where(rango == 0, 1.0, rango)

    def _aplicar(self, X: np.ndarray) -> np.ndarray:
        return (X - self.minimo_) / self.rango_


class CodificadorOneHot:
    """Convierte columnas categoricas en indicadoras 0/1.

    Aprende las categorias en ``ajustar``; en ``transformar`` una categoria no
    vista produce una fila de ceros (no un error), para que el conjunto de
    prueba pueda contener valores raros sin abortar. Con ``omitir_primera`` se
    descarta una categoria por variable para evitar la colinealidad perfecta
    con el intercepto en la regresion.
    """

    def __init__(self, omitir_primera: bool = True) -> None:
        self._omitir_primera = omitir_primera
        self._categorias: dict[str, list[str]] = {}
        self._ajustado = False

    @property
    def ajustado(self) -> bool:
        return self._ajustado

    @property
    def nombres_columnas(self) -> list[str]:
        if not self._ajustado:
            raise RuntimeError("el codificador no esta ajustado")
        return [f"{col}={cat}" for col, cats in self._categorias.items() for cat in cats]

    def ajustar(self, df: pd.DataFrame, columnas: Sequence[str]) -> "CodificadorOneHot":
        faltantes = set(columnas) - set(df.columns)
        if faltantes:
            raise ValueError(f"columnas inexistentes: {sorted(faltantes)}")
        self._categorias = {}
        for col in columnas:
            categorias = sorted(df[col].dropna().astype(str).unique().tolist())
            if self._omitir_primera and len(categorias) > 1:
                categorias = categorias[1:]
            self._categorias[col] = categorias
        self._ajustado = True
        return self

    def transformar(self, df: pd.DataFrame) -> np.ndarray:
        if not self._ajustado:
            raise RuntimeError("el codificador debe ajustarse antes de transformar")
        bloques = []
        for col, categorias in self._categorias.items():
            if col not in df.columns:
                raise ValueError(f"falta la columna {col!r}")
            valores = df[col].astype(str).to_numpy()
            # Comparacion vectorizada: matriz n x k de indicadoras.
            bloques.append((valores[:, None] == np.array(categorias)[None, :]).astype("float64"))
        return np.hstack(bloques) if bloques else np.empty((len(df), 0))

    def ajustar_transformar(self, df: pd.DataFrame, columnas: Sequence[str]) -> np.ndarray:
        return self.ajustar(df, columnas).transformar(df)


def dividir_entrenamiento_prueba(
    n: int, proporcion_prueba: float = 0.2, semilla: int = 42
) -> tuple[np.ndarray, np.ndarray]:
    """Indices de entrenamiento y prueba con permutacion aleatoria reproducible."""
    if not 0 < proporcion_prueba < 1:
        raise ValueError("la proporcion de prueba debe estar en (0, 1)")
    if n < 2:
        raise ValueError("se necesitan al menos dos observaciones")
    rng = np.random.default_rng(semilla)
    permutacion = rng.permutation(n)
    corte = max(1, int(round(n * proporcion_prueba)))
    return permutacion[corte:], permutacion[:corte]


class PreparadorModelacion:
    """Compone escalado de numericas y codificacion de categoricas en una matriz.

    Ejemplo de composicion sobre herencia: el preparador *tiene* un escalador y
    un codificador, y coordina que ambos se ajusten solo con entrenamiento.
    """

    def __init__(
        self,
        numericas: Sequence[str],
        categoricas: Sequence[str],
        escalador: Transformador | None = None,
    ) -> None:
        self._numericas = list(numericas)
        self._categoricas = list(categoricas)
        self._escalador = escalador if escalador is not None else EscaladorEstandar()
        self._codificador = CodificadorOneHot()
        self._ajustado = False

    @property
    def escalador(self) -> Transformador:
        return self._escalador

    @property
    def nombres_columnas(self) -> list[str]:
        if not self._ajustado:
            raise RuntimeError("el preparador no esta ajustado")
        return list(self._numericas) + self._codificador.nombres_columnas

    def ajustar(self, df: pd.DataFrame) -> "PreparadorModelacion":
        self._escalador.ajustar(df[self._numericas].to_numpy(dtype="float64"))
        self._codificador.ajustar(df, self._categoricas)
        self._ajustado = True
        return self

    def transformar(self, df: pd.DataFrame) -> np.ndarray:
        if not self._ajustado:
            raise RuntimeError("el preparador debe ajustarse antes de transformar")
        numericas = self._escalador.transformar(df[self._numericas].to_numpy(dtype="float64"))
        categoricas = self._codificador.transformar(df)
        return np.hstack([numericas, categoricas])

    def ajustar_transformar(self, df: pd.DataFrame) -> np.ndarray:
        return self.ajustar(df).transformar(df)
