"""Mediciones reproducibles de tiempo y memoria.

La rubrica exige mediciones formales: aqui se usa ``timeit`` (que desactiva el
recolector de basura y repite la medicion quedandose con el minimo, el
estimador mas estable del costo intrinseco) y ``tracemalloc`` para el pico de
memoria. Ademas de medir un tamano, ``curva_escalamiento`` mide varios y
``estimar_orden`` ajusta una recta en escala log-log: la pendiente es el
exponente empirico del crecimiento (1 para lineal, 2 para cuadratico, ~1,1
para n log n en los rangos habituales), lo que permite confrontar la cota
teorica de cada algoritmo con su comportamiento observado.
"""

from __future__ import annotations

import math
import timeit
import tracemalloc
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class Medicion:
    """Resultado inmutable de una medicion."""

    nombre: str
    n: int
    segundos: float
    memoria_pico_kb: float | None = None
    repeticiones: int = 1

    @property
    def microsegundos_por_elemento(self) -> float:
        return 1e6 * self.segundos / max(self.n, 1)


def medir_tiempo(
    funcion: Callable[..., Any], *args: Any, repeticiones: int = 5, numero: int = 1, **kwargs: Any
) -> float:
    """Tiempo minimo (en segundos) de ``repeticiones`` corridas de la funcion.

    Se reporta el minimo y no la media porque el ruido del sistema operativo
    solo puede *sumar* tiempo: el minimo es la mejor aproximacion al costo
    real del algoritmo (criterio recomendado por la documentacion de timeit).
    """
    tiempos = timeit.repeat(
        lambda: funcion(*args, **kwargs), repeat=repeticiones, number=numero
    )
    return min(tiempos) / numero


def medir_memoria(funcion: Callable[..., Any], *args: Any, **kwargs: Any) -> float:
    """Pico de memoria adicional (en KB) durante una ejecucion de la funcion."""
    tracemalloc.start()
    tracemalloc.reset_peak()
    try:
        funcion(*args, **kwargs)
        _, pico = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return pico / 1024


def medir(
    nombre: str,
    funcion: Callable[..., Any],
    *args: Any,
    n: int | None = None,
    repeticiones: int = 5,
    con_memoria: bool = True,
    **kwargs: Any,
) -> Medicion:
    """Mide tiempo y, opcionalmente, memoria de una llamada."""
    if n is None:
        n = len(args[0]) if args and hasattr(args[0], "__len__") else 0
    segundos = medir_tiempo(funcion, *args, repeticiones=repeticiones, **kwargs)
    memoria = medir_memoria(funcion, *args, **kwargs) if con_memoria else None
    return Medicion(nombre, n, segundos, memoria, repeticiones)


def comparar(
    implementaciones: dict[str, Callable[..., Any]],
    *args: Any,
    n: int | None = None,
    repeticiones: int = 5,
    con_memoria: bool = True,
    **kwargs: Any,
) -> pd.DataFrame:
    """Mide varias implementaciones con la misma entrada y las tabula.

    La tabla incluye la razon de tiempo respecto de la implementacion mas
    rapida, que es la cifra que sustenta la eleccion final del algoritmo.
    """
    mediciones = [
        medir(nombre, f, *args, n=n, repeticiones=repeticiones, con_memoria=con_memoria, **kwargs)
        for nombre, f in implementaciones.items()
    ]
    tabla = a_dataframe(mediciones)
    tabla["razon_vs_mejor"] = (tabla["segundos"] / tabla["segundos"].min()).round(1)
    return tabla.sort_values("segundos").reset_index(drop=True)


@dataclass
class CurvaEscalamiento:
    """Mediciones de una misma funcion para tamanos crecientes."""

    nombre: str
    mediciones: list[Medicion] = field(default_factory=list)

    @property
    def exponente(self) -> float:
        return estimar_orden(self.mediciones)

    def a_dataframe(self) -> pd.DataFrame:
        tabla = a_dataframe(self.mediciones)
        tabla["exponente_empirico"] = round(self.exponente, 2)
        return tabla


def curva_escalamiento(
    nombre: str,
    funcion: Callable[..., Any],
    generador: Callable[[int], tuple[Any, ...]],
    tamanos: Sequence[int],
    repeticiones: int = 3,
    con_memoria: bool = False,
) -> CurvaEscalamiento:
    """Mide ``funcion`` sobre entradas de tamano creciente.

    ``generador(n)`` debe devolver la tupla de argumentos para un tamano n; se
    invoca fuera de la region medida para no contaminar el tiempo del
    algoritmo con el de construir la entrada.
    """
    curva = CurvaEscalamiento(nombre)
    for n in tamanos:
        argumentos = generador(n)
        curva.mediciones.append(
            medir(nombre, funcion, *argumentos, n=n, repeticiones=repeticiones, con_memoria=con_memoria)
        )
    return curva


def estimar_orden(mediciones: Sequence[Medicion]) -> float:
    """Pendiente de log(tiempo) frente a log(n): exponente empirico de crecimiento.

    Ajuste por minimos cuadrados sobre los puntos (log n, log t). Con dos o mas
    tamanos distintos. Interpretacion: ~1 lineal, ~2 cuadratico, ~1,1 n log n
    en rangos de 10^3 a 10^6, ~0 constante o logaritmico.
    """
    puntos = [(math.log(m.n), math.log(m.segundos)) for m in mediciones if m.n > 0 and m.segundos > 0]
    if len(puntos) < 2:
        raise ValueError("se necesitan al menos dos mediciones con n > 0 y tiempo > 0")
    xs, ys = zip(*puntos)
    media_x, media_y = sum(xs) / len(xs), sum(ys) / len(ys)
    numerador = sum((x - media_x) * (y - media_y) for x, y in zip(xs, ys))
    denominador = sum((x - media_x) ** 2 for x in xs)
    if denominador == 0:
        raise ValueError("todos los tamanos son iguales; no se puede estimar el orden")
    return numerador / denominador


def a_dataframe(mediciones: Sequence[Medicion]) -> pd.DataFrame:
    """Tabla con una fila por medicion, lista para el informe."""
    return pd.DataFrame(
        [
            {
                "implementacion": m.nombre,
                "n": m.n,
                "segundos": round(m.segundos, 6),
                "us_por_elemento": round(m.microsegundos_por_elemento, 4),
                "memoria_pico_kb": None if m.memoria_pico_kb is None else round(m.memoria_pico_kb, 1),
                "repeticiones": m.repeticiones,
            }
            for m in mediciones
        ]
    )
