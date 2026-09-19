"""Algoritmos estructurados y recursivos del nucleo.

Cada funcion declara su complejidad temporal y espacial en la docstring y esta
escrita sin dependencias externas, de modo que la cota teorica pueda
contrastarse con la medicion empirica de ``benchmark.py``. Las versiones
"ingenuas" (insercion, agrupacion por barrido repetido, busqueda lineal) se
conservan deliberadamente: son el termino de comparacion que hace visible la
diferencia de orden de crecimiento.

Convenciones
------------
* Ninguna funcion modifica la secuencia que recibe.
* Las funciones recursivas tienen profundidad acotada: O(log n) en merge sort,
  O(log n) esperada en quickselect con pivote aleatorio, O(log n) en busqueda
  binaria. Ninguna alcanza el limite de recursion de Python con los volumenes
  del proyecto (1,25 millones de registros).
"""

from __future__ import annotations

import random
from collections.abc import Hashable, Sequence
from typing import Any

# ---------------------------------------------------------------------------
# Agregacion
# ---------------------------------------------------------------------------


def agrupar_media(claves: Sequence[Hashable], valores: Sequence[float]) -> dict[Hashable, float]:
    """Media de ``valores`` por cada clave, en una sola pasada.

    Complejidad: tiempo O(n), espacio O(k) con k grupos distintos. Es el
    equivalente de ``groupby(...).mean()`` implementado con dos diccionarios
    acumuladores.

    Lanza ``ValueError`` si las secuencias no tienen el mismo largo.

    >>> agrupar_media(["a", "b", "a"], [1.0, 4.0, 3.0])
    {'a': 2.0, 'b': 4.0}
    """
    if len(claves) != len(valores):
        raise ValueError(
            f"claves ({len(claves)}) y valores ({len(valores)}) deben tener el mismo largo"
        )
    suma: dict[Hashable, float] = {}
    cuenta: dict[Hashable, int] = {}
    for clave, valor in zip(claves, valores):
        suma[clave] = suma.get(clave, 0.0) + valor
        cuenta[clave] = cuenta.get(clave, 0) + 1
    return {clave: suma[clave] / cuenta[clave] for clave in suma}


def agrupar_media_ingenua(
    claves: Sequence[Hashable], valores: Sequence[float]
) -> dict[Hashable, float]:
    """Misma media por grupo, recorriendo la secuencia completa una vez por grupo.

    Complejidad: tiempo O(n * k). Con pocos grupos (k = 10 areas) el costo es
    tolerable; con miles de carreras se vuelve prohibitivo. Se conserva como
    termino de comparacion para el analisis de eficiencia.
    """
    if len(claves) != len(valores):
        raise ValueError("claves y valores deben tener el mismo largo")
    resultado: dict[Hashable, float] = {}
    for grupo in set(claves):
        seleccion = [v for c, v in zip(claves, valores) if c == grupo]
        resultado[grupo] = sum(seleccion) / len(seleccion)
    return resultado


# ---------------------------------------------------------------------------
# Ordenamiento
# ---------------------------------------------------------------------------


def ordenar_merge(datos: Sequence[Any]) -> list[Any]:
    """Merge sort recursivo (divide y venceras).

    Complejidad: tiempo O(n log n) en todos los casos; espacio O(n) por las
    listas auxiliares de la mezcla; profundidad de recursion O(log n).
    Funciona con cualquier tipo que implemente ``<`` (numeros u objetos con
    ``__lt__``, como ``Titulado``). Es estable.

    >>> ordenar_merge([5, 1, 4, 1, 3])
    [1, 1, 3, 4, 5]
    """
    n = len(datos)
    if n <= 1:
        return list(datos)
    mitad = n // 2
    izquierda = ordenar_merge(datos[:mitad])
    derecha = ordenar_merge(datos[mitad:])
    return _mezclar(izquierda, derecha)


def _mezclar(izquierda: list[Any], derecha: list[Any]) -> list[Any]:
    """Mezcla dos listas ordenadas en O(len(izquierda) + len(derecha))."""
    resultado: list[Any] = []
    i = j = 0
    while i < len(izquierda) and j < len(derecha):
        # ``<=`` conserva el orden relativo de los iguales: estabilidad.
        if izquierda[i] <= derecha[j]:
            resultado.append(izquierda[i])
            i += 1
        else:
            resultado.append(derecha[j])
            j += 1
    resultado.extend(izquierda[i:])
    resultado.extend(derecha[j:])
    return resultado


def ordenar_insercion(datos: Sequence[Any]) -> list[Any]:
    """Ordenamiento por insercion.

    Complejidad: tiempo O(n^2) en el caso promedio y peor, O(n) si la entrada
    ya esta ordenada; espacio O(1) adicional. Solo es competitivo con n muy
    pequeno; se incluye como cota inferior de eficiencia en las mediciones.
    """
    resultado = list(datos)
    for i in range(1, len(resultado)):
        actual = resultado[i]
        j = i - 1
        while j >= 0 and resultado[j] > actual:
            resultado[j + 1] = resultado[j]
            j -= 1
        resultado[j + 1] = actual
    return resultado


# ---------------------------------------------------------------------------
# Seleccion (estadisticos de orden)
# ---------------------------------------------------------------------------


def quickselect(datos: Sequence[float], k: int, semilla: int | None = None) -> float:
    """k-esimo menor elemento (k desde 0) sin ordenar la secuencia completa.

    Complejidad: tiempo O(n) esperado con pivote aleatorio, O(n^2) en el peor
    caso (probabilidad despreciable); espacio O(n) por las particiones;
    profundidad de recursion O(log n) esperada.

    Lanza ``IndexError`` si k esta fuera de [0, n) y ``ValueError`` si la
    secuencia esta vacia.

    >>> quickselect([9, 1, 8, 2, 7], 2, semilla=0)
    7
    """
    if len(datos) == 0:
        raise ValueError("no se puede seleccionar en una secuencia vacia")
    if not 0 <= k < len(datos):
        raise IndexError(f"k={k} fuera de rango para {len(datos)} elementos")
    return _quickselect(list(datos), k, random.Random(semilla))


def _quickselect(datos: list[float], k: int, rng: random.Random) -> float:
    if len(datos) == 1:
        return datos[0]
    pivote = datos[rng.randrange(len(datos))]
    menores = [x for x in datos if x < pivote]
    iguales = [x for x in datos if x == pivote]
    mayores = [x for x in datos if x > pivote]
    if k < len(menores):
        return _quickselect(menores, k, rng)
    if k < len(menores) + len(iguales):
        return pivote
    return _quickselect(mayores, k - len(menores) - len(iguales), rng)


def mediana(datos: Sequence[float], semilla: int | None = None) -> float:
    """Mediana mediante quickselect: O(n) esperado frente al O(n log n) de ordenar.

    Con n par promedia los dos elementos centrales, como ``statistics.median``.

    >>> mediana([3, 1, 2])
    2
    >>> mediana([4, 1, 3, 2])
    2.5
    """
    n = len(datos)
    if n == 0:
        raise ValueError("la mediana de una secuencia vacia no esta definida")
    if n % 2 == 1:
        return quickselect(datos, n // 2, semilla)
    inferior = quickselect(datos, n // 2 - 1, semilla)
    superior = quickselect(datos, n // 2, semilla)
    return (inferior + superior) / 2


def mediana_ordenando(datos: Sequence[float]) -> float:
    """Mediana ordenando toda la secuencia: O(n log n). Termino de comparacion."""
    n = len(datos)
    if n == 0:
        raise ValueError("la mediana de una secuencia vacia no esta definida")
    ordenados = sorted(datos)
    if n % 2 == 1:
        return ordenados[n // 2]
    return (ordenados[n // 2 - 1] + ordenados[n // 2]) / 2


# ---------------------------------------------------------------------------
# Busqueda
# ---------------------------------------------------------------------------


def busqueda_binaria(
    ordenados: Sequence[float], objetivo: float, inicio: int = 0, fin: int | None = None
) -> int:
    """Indice de ``objetivo`` en una secuencia ordenada, o -1 si no esta.

    Implementacion recursiva: tiempo O(log n), profundidad O(log n), espacio
    O(1) adicional por nivel. Precondicion: ``ordenados`` esta en orden
    ascendente (no se verifica, seria O(n)).

    >>> busqueda_binaria([1, 3, 5, 7, 9], 7)
    3
    >>> busqueda_binaria([1, 3, 5, 7, 9], 4)
    -1
    """
    if fin is None:
        fin = len(ordenados) - 1
    if inicio > fin:
        return -1
    medio = (inicio + fin) // 2
    if ordenados[medio] == objetivo:
        return medio
    if ordenados[medio] < objetivo:
        return busqueda_binaria(ordenados, objetivo, medio + 1, fin)
    return busqueda_binaria(ordenados, objetivo, inicio, medio - 1)


def busqueda_lineal(datos: Sequence[float], objetivo: float) -> int:
    """Indice de la primera aparicion de ``objetivo`` o -1. Tiempo O(n)."""
    for i, valor in enumerate(datos):
        if valor == objetivo:
            return i
    return -1


def primer_indice_mayor_igual(
    ordenados: Sequence[float], umbral: float, inicio: int = 0, fin: int | None = None
) -> int:
    """Primer indice cuyo valor es >= ``umbral`` (cota inferior), recursivo.

    Devuelve ``len(ordenados)`` si ningun elemento alcanza el umbral. Con ella,
    contar cuantos titulados superan un umbral de rezago cuesta O(log n) en vez
    de O(n).

    >>> primer_indice_mayor_igual([0, 1, 1, 4, 6], 1)
    1
    >>> primer_indice_mayor_igual([0, 1, 1, 4, 6], 5)
    4
    """
    if fin is None:
        fin = len(ordenados)
    if inicio >= fin:
        return inicio
    medio = (inicio + fin) // 2
    if ordenados[medio] < umbral:
        return primer_indice_mayor_igual(ordenados, umbral, medio + 1, fin)
    return primer_indice_mayor_igual(ordenados, umbral, inicio, medio)


def primer_indice_mayor(
    ordenados: Sequence[float], umbral: float, inicio: int = 0, fin: int | None = None
) -> int:
    """Primer indice cuyo valor es > ``umbral`` (cota superior), recursivo, O(log n).

    Junto con ``primer_indice_mayor_igual`` permite contar cuantos elementos son
    iguales a un valor sin recorrerlos: la sobreduracion toma valores enteros
    con miles de repeticiones, asi que un avance lineal sobre los iguales
    degradaria el conteo a O(n).

    >>> primer_indice_mayor([0, 1, 1, 4, 6], 1)
    3
    """
    if fin is None:
        fin = len(ordenados)
    if inicio >= fin:
        return inicio
    medio = (inicio + fin) // 2
    if ordenados[medio] <= umbral:
        return primer_indice_mayor(ordenados, umbral, medio + 1, fin)
    return primer_indice_mayor(ordenados, umbral, inicio, medio)


def contar_sobre_umbral(ordenados: Sequence[float], umbral: float) -> int:
    """Cantidad de elementos estrictamente mayores que ``umbral``, O(log n).

    >>> contar_sobre_umbral([0, 1, 1, 4, 6], 1)
    2
    """
    return len(ordenados) - primer_indice_mayor(ordenados, umbral)


def contar_en_rango(ordenados: Sequence[float], desde: float, hasta: float) -> int:
    """Cantidad de elementos en el intervalo (desde, hasta], O(log n).

    Es la operacion que define las categorias de rezago: 'leve' es (0, 2],
    'moderado' es (2, 4], y asi sucesivamente.

    >>> contar_en_rango([0, 1, 1, 4, 6], 0, 2)
    2
    """
    return primer_indice_mayor(ordenados, hasta) - primer_indice_mayor(ordenados, desde)
