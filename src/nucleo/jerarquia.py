"""Arbol de agregacion Sistema -> Tipo de institucion -> Institucion -> Carrera.

Es la estructura recursiva natural del dominio: una carrera pertenece a una
institucion, que pertenece a un tipo, que pertenece al sistema. Se implementa
con el patron Composite: cada ``NodoJerarquia`` tiene la misma interfaz sea
hoja o nodo interno, de modo que preguntar "cuantos titulados hay" o "cual es
la sobreduracion media" funciona igual en cualquier nivel, y la respuesta se
obtiene recorriendo recursivamente los hijos.

Recursion con memorizacion
--------------------------
El total de titulados de un nodo se calcula recursivamente sumando el de sus
hijos. Sin memorizacion, consultar el total en cada nivel del arbol recorre
las hojas repetidas veces; con ella, cada nodo recuerda su total hasta que se
inserta un nuevo titulado, momento en que invalida la cache propia y la de
sus ancestros. Es el mismo principio de ``functools.lru_cache`` aplicado a una
estructura mutable.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from typing import TYPE_CHECKING

import pandas as pd

from .dominio import Cohorte, Titulado

if TYPE_CHECKING:
    from .metricas import Metrica


class NodoJerarquia:
    """Nodo del arbol; contiene titulados (si es hoja) o hijos (si es interno)."""

    def __init__(self, nombre: str, nivel: str, padre: "NodoJerarquia | None" = None) -> None:
        self._nombre = str(nombre)
        self._nivel = str(nivel)
        self._padre = padre
        self._hijos: dict[str, NodoJerarquia] = {}
        self._titulados: list[Titulado] = []
        self._cache_total: int | None = None

    # --- propiedades ---------------------------------------------------------
    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def nivel(self) -> str:
        return self._nivel

    @property
    def padre(self) -> "NodoJerarquia | None":
        return self._padre

    @property
    def hijos(self) -> list["NodoJerarquia"]:
        return list(self._hijos.values())

    @property
    def es_hoja(self) -> bool:
        return not self._hijos

    def __len__(self) -> int:
        return len(self._hijos)

    def __iter__(self) -> Iterator["NodoJerarquia"]:
        return iter(self._hijos.values())

    def __getitem__(self, nombre: str) -> "NodoJerarquia":
        return self._hijos[nombre]

    def __contains__(self, nombre: object) -> bool:
        return nombre in self._hijos

    def __repr__(self) -> str:
        return f"NodoJerarquia({self._nivel}={self._nombre!r}, hijos={len(self)}, total={self.total()})"

    # --- construccion recursiva ----------------------------------------------
    def insertar(self, titulado: Titulado, ruta: Sequence[str], niveles: Sequence[str]) -> None:
        """Inserta un titulado siguiendo ``ruta`` (un nombre por nivel).

        Caso base: la ruta esta vacia y el titulado se guarda en este nodo.
        Caso recursivo: se obtiene (o crea) el hijo correspondiente al primer
        elemento de la ruta y se delega el resto. Cada insercion invalida la
        cache de totales desde este nodo hacia la raiz.
        """
        self._invalidar_cache()
        if not ruta:
            self._titulados.append(titulado)
            return
        nombre_hijo = str(ruta[0])
        if nombre_hijo not in self._hijos:
            self._hijos[nombre_hijo] = NodoJerarquia(nombre_hijo, niveles[0], padre=self)
        self._hijos[nombre_hijo].insertar(titulado, ruta[1:], niveles[1:])

    def _invalidar_cache(self) -> None:
        nodo: NodoJerarquia | None = self
        while nodo is not None and nodo._cache_total is not None:
            nodo._cache_total = None
            nodo = nodo._padre

    # --- consultas recursivas ------------------------------------------------
    def total(self) -> int:
        """Numero de titulados bajo este nodo (recursivo, memorizado)."""
        if self._cache_total is None:
            self._cache_total = len(self._titulados) + sum(h.total() for h in self._hijos.values())
        return self._cache_total

    def total_sin_cache(self) -> int:
        """Misma suma sin memorizar: termino de comparacion para el benchmark."""
        return len(self._titulados) + sum(h.total_sin_cache() for h in self._hijos.values())

    def titulados(self) -> Iterator[Titulado]:
        """Recorre en profundidad todos los titulados bajo el nodo (generador recursivo)."""
        yield from self._titulados
        for hijo in self._hijos.values():
            yield from hijo.titulados()

    def cohorte(self) -> Cohorte:
        return Cohorte(self.titulados(), nombre=self.ruta())

    def calcular(self, metrica: "Metrica") -> float:
        """Metrica sobre todos los titulados bajo el nodo (Strategy + Composite)."""
        return metrica.calcular(self.cohorte())

    def profundidad(self) -> int:
        """Altura del subarbol: 0 en una hoja."""
        if self.es_hoja:
            return 0
        return 1 + max(h.profundidad() for h in self._hijos.values())

    def ruta(self) -> str:
        """Camino desde la raiz, construido recursivamente hacia el padre."""
        if self._padre is None:
            return self._nombre
        return f"{self._padre.ruta()} > {self._nombre}"

    def hojas(self) -> list["NodoJerarquia"]:
        if self.es_hoja:
            return [self]
        return [hoja for h in self._hijos.values() for hoja in h.hojas()]

    def buscar(self, nombre: str) -> "NodoJerarquia | None":
        """Primer nodo con ese nombre en el subarbol (busqueda en profundidad)."""
        if self._nombre == nombre:
            return self
        for hijo in self._hijos.values():
            encontrado = hijo.buscar(nombre)
            if encontrado is not None:
                return encontrado
        return None

    def descender_por_maximo(self, metrica: "Metrica", minimo: int = 30) -> list["NodoJerarquia"]:
        """Camino desde este nodo hasta una hoja eligiendo, en cada nivel, el hijo
        con mayor valor de la metrica entre los que tienen al menos ``minimo``
        titulados. Responde "donde se concentra el rezago" bajando por el arbol.
        """
        camino = [self]
        candidatos = [h for h in self._hijos.values() if h.total() >= minimo]
        if not candidatos:
            return camino
        mejor = max(candidatos, key=lambda h: h.calcular(metrica))
        return camino + mejor.descender_por_maximo(metrica, minimo)

    # --- exportacion ---------------------------------------------------------
    def a_registros(
        self, metricas: Sequence["Metrica"], nivel_maximo: int | None = None, _prof: int = 0
    ) -> list[dict[str, object]]:
        """Aplana el arbol en registros (uno por nodo), recursivamente."""
        fila: dict[str, object] = {
            "nivel": self._nivel, "nombre": self._nombre, "ruta": self.ruta(),
            "profundidad": _prof, "total": self.total(),
        }
        if self.total() > 0:
            cohorte = self.cohorte()
            fila.update({m.nombre: round(m.calcular(cohorte), 3) for m in metricas})
        registros = [fila]
        if nivel_maximo is None or _prof < nivel_maximo:
            for hijo in self._hijos.values():
                registros.extend(hijo.a_registros(metricas, nivel_maximo, _prof + 1))
        return registros

    def a_dataframe(self, metricas: Sequence["Metrica"], nivel_maximo: int | None = None) -> pd.DataFrame:
        return pd.DataFrame(self.a_registros(metricas, nivel_maximo))


NIVELES_ESTANDAR: tuple[str, ...] = ("tipo_institucion", "institucion", "carrera")


def construir_jerarquia(
    cohorte: Cohorte, niveles: Sequence[str] = NIVELES_ESTANDAR, raiz: str = "Sistema"
) -> NodoJerarquia:
    """Construye el arbol insertando cada titulado por la ruta de sus atributos.

    Complejidad: O(n * d) con d = numero de niveles (profundidad del arbol).
    """
    arbol = NodoJerarquia(raiz, "sistema")
    for titulado in cohorte:
        ruta = [getattr(titulado, nivel) for nivel in niveles]
        arbol.insertar(titulado, ruta, list(niveles))
    return arbol
