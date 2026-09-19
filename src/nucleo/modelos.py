"""Modelos implementados desde primeros principios (patron Template Method).

``ModeloGradiente`` define el algoritmo de entrenamiento completo —inicializar
parametros, iterar, calcular prediccion y gradiente, actualizar, registrar la
perdida— y deja como ganchos abstractos las tres piezas que cambian entre un
modelo y otro: la funcion de enlace, la perdida y el gradiente. La regresion
lineal y la logistica heredan el esqueleto y sobreescriben solo esas piezas.
Ese es el patron Template Method, y es lo que hace que agregar un tercer
modelo (por ejemplo, Poisson) no exija duplicar el bucle de optimizacion.

El descenso de gradiente es un algoritmo de optimizacion iterativo: en cada
paso mueve los parametros en la direccion que mas reduce la perdida. Su
complejidad es O(iteraciones * n * p) en tiempo y O(n * p) en espacio para la
matriz de diseno. La regresion lineal tambien admite una solucion cerrada
(``RegresionLinealCerrada``, ecuaciones normales, O(n * p^2 + p^3)), que se
usa como referencia para verificar que el descenso converge al optimo.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np


def _validar_xy(X: np.ndarray, y: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray | None]:
    X = np.asarray(X, dtype="float64")
    if X.ndim != 2:
        raise ValueError(f"X debe ser una matriz 2D; tiene {X.ndim} dimensiones")
    if X.shape[0] == 0:
        raise ValueError("X no tiene filas")
    if np.isnan(X).any():
        raise ValueError("X contiene NaN")
    if y is None:
        return X, None
    y = np.asarray(y, dtype="float64").ravel()
    if y.shape[0] != X.shape[0]:
        raise ValueError(f"X tiene {X.shape[0]} filas e y tiene {y.shape[0]} valores")
    if np.isnan(y).any():
        raise ValueError("y contiene NaN")
    return X, y


class ModeloGradiente(ABC):
    """Esqueleto del entrenamiento por descenso de gradiente (Template Method)."""

    def __init__(
        self, tasa_aprendizaje: float = 0.1, iteraciones: int = 500, tolerancia: float = 1e-8
    ) -> None:
        if tasa_aprendizaje <= 0:
            raise ValueError("la tasa de aprendizaje debe ser positiva")
        if iteraciones <= 0:
            raise ValueError("el numero de iteraciones debe ser positivo")
        self._tasa = float(tasa_aprendizaje)
        self._iteraciones = int(iteraciones)
        self._tolerancia = float(tolerancia)
        self._pesos: np.ndarray | None = None
        self._sesgo: float = 0.0
        self._historial: list[float] = []

    # --- estado encapsulado --------------------------------------------------
    @property
    def ajustado(self) -> bool:
        return self._pesos is not None

    @property
    def pesos(self) -> np.ndarray:
        self._exigir_ajustado()
        return self._pesos.copy()  # copia: nadie modifica el estado interno

    @property
    def sesgo(self) -> float:
        self._exigir_ajustado()
        return self._sesgo

    @property
    def historial_perdida(self) -> list[float]:
        return list(self._historial)

    @property
    def iteraciones_realizadas(self) -> int:
        return len(self._historial)

    def _exigir_ajustado(self) -> None:
        if self._pesos is None:
            raise RuntimeError(f"{type(self).__name__} no esta ajustado; llame a ajustar(X, y)")

    # --- el algoritmo completo, fijo para todas las subclases ----------------
    def ajustar(self, X: np.ndarray, y: np.ndarray) -> "ModeloGradiente":
        X, y = _validar_xy(X, y)
        n, p = X.shape
        self._pesos = np.zeros(p)
        self._sesgo = 0.0
        self._historial = []
        for _ in range(self._iteraciones):
            prediccion = self._enlace(X @ self._pesos + self._sesgo)
            residuo = prediccion - y
            # Gradiente del promedio de la perdida respecto de pesos y sesgo.
            gradiente_pesos = (X.T @ residuo) / n
            gradiente_sesgo = residuo.mean()
            self._pesos -= self._tasa * gradiente_pesos
            self._sesgo -= self._tasa * gradiente_sesgo
            perdida = self._perdida(y, prediccion)
            # Con una tasa demasiado alta el descenso oscila y explota: se detecta
            # y se informa con claridad en vez de devolver pesos infinitos o NaN.
            if not np.isfinite(perdida) or (self._historial and perdida > 1e6 * max(self._historial[0], 1e-12)):
                raise RuntimeError(
                    f"{type(self).__name__}: el descenso de gradiente divergio en la iteracion "
                    f"{len(self._historial) + 1} (tasa={self._tasa}); reduzca la tasa de aprendizaje"
                )
            if self._historial and abs(self._historial[-1] - perdida) < self._tolerancia:
                self._historial.append(perdida)
                break
            self._historial.append(perdida)
        return self

    def predecir(self, X: np.ndarray) -> np.ndarray:
        self._exigir_ajustado()
        X, _ = _validar_xy(X)
        if X.shape[1] != self._pesos.shape[0]:
            raise ValueError(f"el modelo se ajusto con {self._pesos.shape[0]} variables y recibe {X.shape[1]}")
        return self._salida(self._enlace(X @ self._pesos + self._sesgo))

    # --- ganchos que definen cada modelo -------------------------------------
    @abstractmethod
    def _enlace(self, z: np.ndarray) -> np.ndarray:
        """Transforma la combinacion lineal en la prediccion (identidad, sigmoide...)."""

    @abstractmethod
    def _perdida(self, y: np.ndarray, prediccion: np.ndarray) -> float:
        """Perdida promedio que el gradiente minimiza."""

    def _salida(self, prediccion: np.ndarray) -> np.ndarray:
        """Post-procesa la prediccion (por defecto, la devuelve tal cual)."""
        return prediccion

    @abstractmethod
    def evaluar(self, X: np.ndarray, y: np.ndarray) -> dict[str, float]:
        """Metricas de desempeno sobre un conjunto."""

    def __repr__(self) -> str:
        estado = f"iteraciones={self.iteraciones_realizadas}" if self.ajustado else "sin ajustar"
        return f"{type(self).__name__}(tasa={self._tasa}, {estado})"


class RegresionLinealGD(ModeloGradiente):
    """Regresion lineal por descenso de gradiente sobre el error cuadratico medio."""

    def _enlace(self, z: np.ndarray) -> np.ndarray:
        return z

    def _perdida(self, y: np.ndarray, prediccion: np.ndarray) -> float:
        return float(np.mean((prediccion - y) ** 2))

    def evaluar(self, X: np.ndarray, y: np.ndarray) -> dict[str, float]:
        X, y = _validar_xy(X, y)
        return metricas_regresion(y, self.predecir(X))


class RegresionLogisticaGD(ModeloGradiente):
    """Regresion logistica por descenso de gradiente sobre la entropia cruzada."""

    def __init__(self, tasa_aprendizaje: float = 0.1, iteraciones: int = 500,
                 tolerancia: float = 1e-8, umbral: float = 0.5) -> None:
        super().__init__(tasa_aprendizaje, iteraciones, tolerancia)
        if not 0 < umbral < 1:
            raise ValueError("el umbral de decision debe estar en (0, 1)")
        self._umbral = umbral

    def _enlace(self, z: np.ndarray) -> np.ndarray:
        # Sigmoide numericamente estable: evita overflow en exp para |z| grande.
        return np.where(z >= 0, 1 / (1 + np.exp(-np.clip(z, -500, 500))),
                        np.exp(np.clip(z, -500, 500)) / (1 + np.exp(np.clip(z, -500, 500))))

    def _perdida(self, y: np.ndarray, prediccion: np.ndarray) -> float:
        eps = 1e-12
        p = np.clip(prediccion, eps, 1 - eps)
        return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))

    def predecir_probabilidad(self, X: np.ndarray) -> np.ndarray:
        self._exigir_ajustado()
        X, _ = _validar_xy(X)
        return self._enlace(X @ self._pesos + self._sesgo)

    def _salida(self, prediccion: np.ndarray) -> np.ndarray:
        return (prediccion >= self._umbral).astype(int)

    def evaluar(self, X: np.ndarray, y: np.ndarray) -> dict[str, float]:
        X, y = _validar_xy(X, y)
        return metricas_clasificacion(y.astype(int), self.predecir(X))


class RegresionLinealCerrada:
    """Solucion exacta por ecuaciones normales: referencia para verificar el descenso.

    Comparte la interfaz publica (``ajustar``, ``predecir``, ``evaluar``,
    ``pesos``, ``sesgo``) sin heredar de ``ModeloGradiente``: es un ejemplo de
    polimorfismo por interfaz (*duck typing*), suficiente para que el notebook
    trate a ambos modelos de la misma forma.
    """

    def __init__(self) -> None:
        self._pesos: np.ndarray | None = None
        self._sesgo: float = 0.0

    @property
    def ajustado(self) -> bool:
        return self._pesos is not None

    @property
    def pesos(self) -> np.ndarray:
        if self._pesos is None:
            raise RuntimeError("el modelo no esta ajustado")
        return self._pesos.copy()

    @property
    def sesgo(self) -> float:
        if self._pesos is None:
            raise RuntimeError("el modelo no esta ajustado")
        return self._sesgo

    def ajustar(self, X: np.ndarray, y: np.ndarray) -> "RegresionLinealCerrada":
        X, y = _validar_xy(X, y)
        X_aum = np.hstack([np.ones((X.shape[0], 1)), X])
        # lstsq resuelve (X'X) b = X'y de forma numericamente estable.
        coeficientes, *_ = np.linalg.lstsq(X_aum, y, rcond=None)
        self._sesgo = float(coeficientes[0])
        self._pesos = coeficientes[1:]
        return self

    def predecir(self, X: np.ndarray) -> np.ndarray:
        if self._pesos is None:
            raise RuntimeError("el modelo no esta ajustado")
        X, _ = _validar_xy(X)
        return X @ self._pesos + self._sesgo

    def evaluar(self, X: np.ndarray, y: np.ndarray) -> dict[str, float]:
        X, y = _validar_xy(X, y)
        return metricas_regresion(y, self.predecir(X))


# ---------------------------------------------------------------------------
# Metricas de desempeno (funciones puras)
# ---------------------------------------------------------------------------


def metricas_regresion(y: np.ndarray, prediccion: np.ndarray) -> dict[str, float]:
    y = np.asarray(y, dtype="float64")
    prediccion = np.asarray(prediccion, dtype="float64")
    residuo = y - prediccion
    sct = float(np.sum((y - y.mean()) ** 2))
    r2 = 1 - float(np.sum(residuo**2)) / sct if sct > 0 else float("nan")
    return {
        "rmse": float(np.sqrt(np.mean(residuo**2))),
        "mae": float(np.mean(np.abs(residuo))),
        "r2": r2,
    }


def metricas_clasificacion(y: np.ndarray, prediccion: np.ndarray) -> dict[str, float]:
    y = np.asarray(y).astype(int)
    prediccion = np.asarray(prediccion).astype(int)
    vp = int(np.sum((y == 1) & (prediccion == 1)))
    vn = int(np.sum((y == 0) & (prediccion == 0)))
    fp = int(np.sum((y == 0) & (prediccion == 1)))
    fn = int(np.sum((y == 1) & (prediccion == 0)))
    precision = vp / (vp + fp) if vp + fp else 0.0
    sensibilidad = vp / (vp + fn) if vp + fn else 0.0
    f1 = 2 * precision * sensibilidad / (precision + sensibilidad) if precision + sensibilidad else 0.0
    return {
        "exactitud": (vp + vn) / len(y),
        "precision": precision,
        "sensibilidad": sensibilidad,
        "f1": f1,
        "vp": vp, "vn": vn, "fp": fp, "fn": fn,
    }
