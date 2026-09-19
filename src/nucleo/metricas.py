"""Metricas intercambiables sobre una cohorte (patron Strategy).

``Metrica`` es una clase abstracta: define la interfaz (``calcular``) y el
comportamiento comun (nombre, representacion, invocacion), y deja a cada
subclase la formula concreta. Gracias al polimorfismo, ``Cohorte.calcular``
acepta cualquier subclase sin conocerla, y agregar una metrica nueva no exige
tocar la cohorte ni el resto del nucleo.

Las metricas de orden (mediana, percentil) usan ``quickselect`` del nucleo:
O(n) esperado en lugar de ordenar la cohorte completa.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from .algoritmos import mediana, quickselect

if TYPE_CHECKING:
    from .dominio import Cohorte


class Metrica(ABC):
    """Interfaz comun de toda metrica calculable sobre una cohorte."""

    #: Atributo público que cada subclase sobreescribe.
    nombre: str = "metrica"

    @abstractmethod
    def calcular(self, cohorte: "Cohorte") -> float:
        """Valor de la metrica para la cohorte. Lanza ValueError si esta vacia."""

    def __call__(self, cohorte: "Cohorte") -> float:
        return self.calcular(cohorte)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(nombre={self.nombre!r})"

    @staticmethod
    def _exigir_no_vacia(cohorte: "Cohorte") -> None:
        if len(cohorte) == 0:
            raise ValueError("no se puede calcular una metrica sobre una cohorte vacia")


class MediaSobreduracion(Metrica):
    """Promedio de semestres por sobre la duracion teorica. O(n)."""

    nombre = "sobreduracion_media"

    def calcular(self, cohorte: "Cohorte") -> float:
        self._exigir_no_vacia(cohorte)
        return sum(t.sobreduracion for t in cohorte) / len(cohorte)


class MedianaSobreduracion(Metrica):
    """Mediana de la sobreduracion mediante quickselect. O(n) esperado."""

    nombre = "sobreduracion_mediana"

    def __init__(self, semilla: int | None = 0) -> None:
        self._semilla = semilla

    def calcular(self, cohorte: "Cohorte") -> float:
        self._exigir_no_vacia(cohorte)
        return float(mediana(cohorte.valores("sobreduracion"), self._semilla))


class PercentilSobreduracion(Metrica):
    """Percentil p de la sobreduracion (metodo del elemento mas cercano). O(n)."""

    def __init__(self, p: float, semilla: int | None = 0) -> None:
        if not 0 <= p <= 100:
            raise ValueError(f"el percentil debe estar en [0, 100]; se recibio {p}")
        self._p = p
        self._semilla = semilla
        self.nombre = f"sobreduracion_p{int(p)}"

    def calcular(self, cohorte: "Cohorte") -> float:
        self._exigir_no_vacia(cohorte)
        valores = cohorte.valores("sobreduracion")
        k = min(len(valores) - 1, max(0, round(self._p / 100 * (len(valores) - 1))))
        return float(quickselect(valores, k, self._semilla))


class TasaOportuna(Metrica):
    """Porcentaje de titulados que egresan dentro del plazo teorico. O(n)."""

    nombre = "tasa_oportuna_pct"

    def calcular(self, cohorte: "Cohorte") -> float:
        self._exigir_no_vacia(cohorte)
        return 100.0 * sum(1 for t in cohorte if t.es_oportuna) / len(cohorte)


class IndiceDuracionMedio(Metrica):
    """Promedio de la razon duracion real / teorica. O(n)."""

    nombre = "indice_duracion_medio"

    def calcular(self, cohorte: "Cohorte") -> float:
        self._exigir_no_vacia(cohorte)
        return sum(t.indice_duracion for t in cohorte) / len(cohorte)


class TasaRezagoSevero(Metrica):
    """Porcentaje con rezago severo (mas de 4 semestres). O(n)."""

    nombre = "rezago_severo_pct"

    def calcular(self, cohorte: "Cohorte") -> float:
        self._exigir_no_vacia(cohorte)
        return 100.0 * sum(1 for t in cohorte if t.categoria_rezago == "Rezago severo") / len(cohorte)


def metricas_estandar() -> list[Metrica]:
    """Conjunto por defecto que usan los notebooks y el informe."""
    return [
        MediaSobreduracion(),
        MedianaSobreduracion(),
        PercentilSobreduracion(75),
        TasaOportuna(),
        TasaRezagoSevero(),
    ]
