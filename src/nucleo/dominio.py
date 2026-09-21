"""Modelo de dominio: ``Titulado`` y ``Cohorte``.

En la Fase 2 cada titulado era una fila de un DataFrame y las reglas del
dominio (que la sobreduracion es la diferencia entre duracion real y teorica,
que una duracion no puede ser negativa) vivian dispersas en funciones. Aqui se
encapsulan en objetos: los atributos son privados, se validan al construirse y
las magnitudes derivadas se exponen como propiedades de solo lectura, de modo
que un ``Titulado`` no puede quedar en un estado incoherente.

``Cohorte`` es una coleccion de titulados que implementa el protocolo de
secuencia de Python (``len``, iteracion, indexacion, ``in``) y delega el
calculo de indicadores en objetos ``Metrica`` intercambiables (patron
Strategy): la cohorte no sabe *como* se calcula una metrica, solo *que* puede
pedirsela a cualquier objeto que cumpla la interfaz.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from typing import TYPE_CHECKING, Any

import pandas as pd

from .. import config
from .algoritmos import ordenar_merge

if TYPE_CHECKING:  # evita la importacion circular en tiempo de ejecucion
    from .metricas import Metrica


class Titulado:
    """Un titulo obtenido por un estudiante, con sus atributos validados.

    Los atributos se guardan con prefijo ``_`` y se exponen mediante
    propiedades: quien usa la clase no puede asignar una duracion negativa ni
    cambiar el identificador despues de construir el objeto. ``__slots__``
    evita el diccionario por instancia y reduce la memoria a la mitad, lo que
    importa cuando se instancian cientos de miles de objetos.
    """

    __slots__ = (
        "_mrun", "_genero", "_area", "_tipo_institucion", "_institucion",
        "_carrera", "_modalidad", "_region", "_anio_titulo",
        "_duracion_teorica", "_duracion_real", "_edad_titulacion",
    )

    def __init__(
        self,
        mrun: int,
        genero: str,
        area: str,
        tipo_institucion: str,
        institucion: str,
        carrera: str,
        modalidad: str,
        region: str,
        anio_titulo: int,
        duracion_teorica: int,
        duracion_real: int,
        edad_titulacion: int,
    ) -> None:
        self._mrun = int(mrun)
        self._genero = str(genero)
        self._area = str(area)
        self._tipo_institucion = str(tipo_institucion)
        self._institucion = str(institucion)
        self._carrera = str(carrera)
        self._modalidad = str(modalidad)
        self._region = str(region)
        self._anio_titulo = int(anio_titulo)
        # Las duraciones pasan por los setters, que validan.
        self.duracion_teorica = duracion_teorica
        self.duracion_real = duracion_real
        self.edad_titulacion = edad_titulacion

    # --- atributos de identidad: solo lectura --------------------------------
    @property
    def mrun(self) -> int:
        return self._mrun

    @property
    def genero(self) -> str:
        return self._genero

    @property
    def area(self) -> str:
        return self._area

    @property
    def tipo_institucion(self) -> str:
        return self._tipo_institucion

    @property
    def institucion(self) -> str:
        return self._institucion

    @property
    def carrera(self) -> str:
        return self._carrera

    @property
    def modalidad(self) -> str:
        return self._modalidad

    @property
    def region(self) -> str:
        return self._region

    @property
    def anio_titulo(self) -> int:
        return self._anio_titulo

    # --- atributos validados -------------------------------------------------
    @property
    def duracion_teorica(self) -> int:
        return self._duracion_teorica

    @duracion_teorica.setter
    def duracion_teorica(self, valor: int) -> None:
        valor = int(valor)
        if valor <= 0:
            raise ValueError(f"la duracion teorica debe ser positiva; se recibio {valor}")
        self._duracion_teorica = valor

    @property
    def duracion_real(self) -> int:
        return self._duracion_real

    @duracion_real.setter
    def duracion_real(self, valor: int) -> None:
        valor = int(valor)
        if valor < config.DURACION_REAL_MIN:
            raise ValueError(
                f"la duracion real debe ser >= {config.DURACION_REAL_MIN}; se recibio {valor}"
            )
        self._duracion_real = valor

    @property
    def edad_titulacion(self) -> int:
        return self._edad_titulacion

    @edad_titulacion.setter
    def edad_titulacion(self, valor: int) -> None:
        valor = int(valor)
        if not config.EDAD_MIN <= valor <= config.EDAD_MAX:
            raise ValueError(
                f"la edad de titulacion debe estar en [{config.EDAD_MIN}, {config.EDAD_MAX}]; "
                f"se recibio {valor}"
            )
        self._edad_titulacion = valor

    # --- magnitudes derivadas: siempre coherentes con el estado ---------------
    @property
    def sobreduracion(self) -> int:
        """Semestres por sobre la duracion teorica del plan."""
        return self._duracion_real - self._duracion_teorica

    @property
    def indice_duracion(self) -> float:
        return self._duracion_real / self._duracion_teorica

    @property
    def es_oportuna(self) -> bool:
        return self.sobreduracion <= 0

    @property
    def categoria_rezago(self) -> str:
        """Categoria ordinal segun los umbrales de ``config.UMBRALES_REZAGO``."""
        for etiqueta, umbral in config.UMBRALES_REZAGO:
            if self.sobreduracion <= umbral:
                return etiqueta
        return config.ETIQUETA_REZAGO_SEVERO

    # --- metodos especiales --------------------------------------------------
    def __repr__(self) -> str:
        return (
            f"Titulado(mrun={self._mrun}, carrera={self._carrera!r}, "
            f"real={self._duracion_real}, teorica={self._duracion_teorica}, "
            f"sobreduracion={self.sobreduracion:+d})"
        )

    def __eq__(self, otro: object) -> bool:
        """Dos titulados son el mismo registro si coinciden estudiante y carrera."""
        if not isinstance(otro, Titulado):
            return NotImplemented
        return (self._mrun, self._carrera, self._anio_titulo) == (
            otro._mrun, otro._carrera, otro._anio_titulo
        )

    def __hash__(self) -> int:
        return hash((self._mrun, self._carrera, self._anio_titulo))

    def __lt__(self, otro: "Titulado") -> bool:
        """Orden natural por sobreduracion: permite ``sorted`` y ``ordenar_merge``."""
        if not isinstance(otro, Titulado):
            return NotImplemented
        return self.sobreduracion < otro.sobreduracion

    def __le__(self, otro: "Titulado") -> bool:
        if not isinstance(otro, Titulado):
            return NotImplemented
        return self.sobreduracion <= otro.sobreduracion

    # --- construccion desde datos tabulares ----------------------------------
    @classmethod
    def desde_fila(cls, fila: Any) -> "Titulado":
        """Construye un titulado desde una fila del dataset analitico de la Fase 2.

        Acepta cualquier objeto con acceso por nombre de columna (``pd.Series``,
        ``namedtuple`` de ``itertuples`` o ``dict``).
        """
        obtener = (lambda k: fila[k]) if isinstance(fila, (dict, pd.Series)) else (lambda k: getattr(fila, k))
        return cls(
            mrun=obtener("mrun"),
            genero=obtener("genero"),
            area=obtener("area_conocimiento"),
            tipo_institucion=obtener("tipo_inst_1"),
            institucion=obtener("nomb_inst"),
            carrera=obtener("nomb_carrera"),
            modalidad=obtener("modalidad"),
            region=obtener("region_sede"),
            anio_titulo=obtener("anio_titulo"),
            duracion_teorica=obtener("dur_total_carr"),
            duracion_real=obtener("duracion_real_sem"),
            edad_titulacion=obtener("edad_titulacion"),
        )


COLUMNAS_TITULADO: tuple[str, ...] = (
    "mrun", "genero", "area_conocimiento", "tipo_inst_1", "nomb_inst", "nomb_carrera",
    "modalidad", "region_sede", "anio_titulo", "dur_total_carr", "duracion_real_sem",
    "edad_titulacion",
)


class Cohorte:
    """Coleccion de titulados con el protocolo de secuencia de Python.

    Las operaciones de filtrado y agrupacion devuelven nuevas cohortes (no
    modifican la original), en linea con la convencion del proyecto de que
    ninguna operacion muta su entrada.
    """

    def __init__(self, titulados: Iterable[Titulado] = (), nombre: str = "cohorte") -> None:
        self._titulados: list[Titulado] = list(titulados)
        self._nombre = str(nombre)

    # --- protocolo de secuencia ----------------------------------------------
    def __len__(self) -> int:
        return len(self._titulados)

    def __iter__(self) -> Iterator[Titulado]:
        return iter(self._titulados)

    def __getitem__(self, indice: int) -> Titulado:
        return self._titulados[indice]

    def __contains__(self, titulado: object) -> bool:
        return titulado in self._titulados

    def __repr__(self) -> str:
        return f"Cohorte({self._nombre!r}, n={len(self)})"

    @property
    def nombre(self) -> str:
        return self._nombre

    # --- construccion y mutacion controlada ----------------------------------
    def agregar(self, titulado: Titulado) -> None:
        if not isinstance(titulado, Titulado):
            raise TypeError(f"solo se pueden agregar objetos Titulado; se recibio {type(titulado).__name__}")
        self._titulados.append(titulado)

    @classmethod
    def desde_dataframe(
        cls, df: pd.DataFrame, limite: int | None = None, nombre: str = "cohorte",
        semilla: int = 42,
    ) -> "Cohorte":
        """Instancia un ``Titulado`` por fila del dataset analitico.

        ``limite`` toma una muestra aleatoria reproducible: instanciar 1,25
        millones de objetos es viable pero lento para una demostracion.
        ``itertuples`` es un orden de magnitud mas rapido que ``iterrows``.
        """
        faltantes = set(COLUMNAS_TITULADO) - set(df.columns)
        if faltantes:
            raise ValueError(f"faltan columnas para construir titulados: {sorted(faltantes)}")
        base = df[list(COLUMNAS_TITULADO)].dropna()
        if limite is not None and limite < len(base):
            base = base.sample(limite, random_state=semilla)
        titulados = [Titulado.desde_fila(fila) for fila in base.itertuples(index=False)]
        return cls(titulados, nombre)

    # --- consultas -----------------------------------------------------------
    def filtrar(self, predicado: Callable[[Titulado], bool], nombre: str | None = None) -> "Cohorte":
        """Nueva cohorte con los titulados que cumplen el predicado."""
        return Cohorte(
            (t for t in self._titulados if predicado(t)),
            nombre or f"{self._nombre}/filtrada",
        )

    def agrupar_por(self, atributo: str) -> dict[str, "Cohorte"]:
        """Particiona la cohorte segun un atributo, en una pasada O(n)."""
        grupos: dict[str, list[Titulado]] = {}
        for t in self._titulados:
            grupos.setdefault(getattr(t, atributo), []).append(t)
        return {clave: Cohorte(lista, f"{self._nombre}/{atributo}={clave}") for clave, lista in grupos.items()}

    def valores(self, atributo: str) -> list[Any]:
        """Lista con el valor de un atributo o propiedad para cada titulado."""
        return [getattr(t, atributo) for t in self._titulados]

    def ordenados_por_sobreduracion(self, descendente: bool = False) -> list[Titulado]:
        """Titulados ordenados con el merge sort del nucleo (usa ``Titulado.__lt__``)."""
        ordenados = ordenar_merge(self._titulados)
        return ordenados[::-1] if descendente else ordenados

    # --- Strategy: la metrica decide como calcular ----------------------------
    def calcular(self, metrica: "Metrica") -> float:
        return metrica.calcular(self)

    def resumen(self, metricas: Iterable["Metrica"]) -> dict[str, float]:
        return {m.nombre: m.calcular(self) for m in metricas}

    def tabla_por(self, atributo: str, metricas: Iterable["Metrica"], minimo: int = 30) -> pd.DataFrame:
        """Tabla de metricas por grupo, omitiendo grupos con menos de ``minimo`` casos."""
        metricas = list(metricas)
        filas = []
        for clave, grupo in self.agrupar_por(atributo).items():
            if len(grupo) < minimo:
                continue
            fila = {atributo: clave, "n": len(grupo)}
            fila.update(grupo.resumen(metricas))
            filas.append(fila)
        return pd.DataFrame(filas).sort_values("n", ascending=False).reset_index(drop=True)
