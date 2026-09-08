"""Depuracion del consolidado: sentinelas, faltantes, duplicados y tipos.

El SIES no publica valores nulos explicitos: usa codigos centinela (9995, 9998,
9999 y 1900 en los anios de ingreso; 19000101 en las fechas; semestre 0).
Tratarlos como numeros reales contaminaria cualquier calculo de duracion, por
lo que el primer paso del pipeline es convertirlos en NA y recien despues
decidir su tratamiento.

Cada operacion queda registrada en una ``BitacoraLimpieza``, que produce la
tabla de trazabilidad exigida por la Fase 2: que se hizo, cuantas filas se
vieron afectadas y por que.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from . import config


@dataclass
class PasoLimpieza:
    """Registro de una unica operacion de limpieza."""

    paso: str
    detalle: str
    filas_antes: int
    filas_despues: int

    @property
    def filas_afectadas(self) -> int:
        return self.filas_antes - self.filas_despues

    @property
    def porcentaje(self) -> float:
        if self.filas_antes == 0:
            return 0.0
        return round(100 * self.filas_afectadas / self.filas_antes, 3)


@dataclass
class BitacoraLimpieza:
    """Acumula los pasos aplicados y los expone como tabla auditable.

    Ejemplo
    -------
    >>> bitacora = BitacoraLimpieza()
    >>> bitacora.registrar("filtro", "solo pregrado", 100, 80)
    >>> bitacora.a_dataframe()["filas_afectadas"].tolist()
    [20]
    """

    pasos: list[PasoLimpieza] = field(default_factory=list)

    def registrar(self, paso: str, detalle: str, antes: int, despues: int) -> None:
        """Anexa un paso a la bitacora."""
        self.pasos.append(PasoLimpieza(paso, detalle, antes, despues))

    def a_dataframe(self) -> pd.DataFrame:
        """Convierte la bitacora en un DataFrame listo para exportar."""
        return pd.DataFrame(
            [
                {
                    "paso": p.paso,
                    "detalle": p.detalle,
                    "filas_antes": p.filas_antes,
                    "filas_despues": p.filas_despues,
                    "filas_afectadas": p.filas_afectadas,
                    "porcentaje": p.porcentaje,
                }
                for p in self.pasos
            ]
        )

    def __len__(self) -> int:
        return len(self.pasos)


def reporte_faltantes(df: pd.DataFrame) -> pd.DataFrame:
    """Tabla de valores faltantes por columna, ordenada de mayor a menor."""
    nulos = df.isna().sum()
    reporte = pd.DataFrame(
        {
            "columna": nulos.index,
            "nulos": nulos.to_numpy(),
            "porcentaje": (100 * nulos / len(df)).round(3).to_numpy(),
            "tipo": [str(df[c].dtype) for c in nulos.index],
        }
    )
    return reporte.sort_values("nulos", ascending=False).reset_index(drop=True)


def marcar_sentinelas(
    df: pd.DataFrame, bitacora: BitacoraLimpieza | None = None
) -> pd.DataFrame:
    """Reemplaza los codigos centinela del SIES por NA explicitos.

    No elimina filas: solo hace visible la ausencia de dato, de modo que el
    reporte de faltantes refleje la realidad del conjunto y las decisiones
    posteriores se tomen sobre informacion correcta.
    """
    df = df.copy()
    conteos: dict[str, int] = {}

    mascara_anio = df["anio_ing_carr_ori"].isin(config.SENTINELAS_ANIO_INGRESO)
    conteos["anio_ing_carr_ori"] = int(mascara_anio.sum())
    df["anio_ing_carr_ori"] = df["anio_ing_carr_ori"].where(~mascara_anio).astype("Int32")

    mascara_sem = ~df["sem_ing_carr_ori"].isin(config.SEMESTRES_VALIDOS)
    conteos["sem_ing_carr_ori"] = int(mascara_sem.sum())
    df["sem_ing_carr_ori"] = df["sem_ing_carr_ori"].where(~mascara_sem).astype("Int8")

    mascara_fecha = df["fecha_obtencion_titulo"] <= config.SENTINELA_FECHA
    conteos["fecha_obtencion_titulo"] = int(mascara_fecha.sum())
    df["fecha_obtencion_titulo"] = (
        df["fecha_obtencion_titulo"].where(~mascara_fecha).astype("Int32")
    )

    mascara_nac = df["fec_nac_alu"] <= config.SENTINELA_FEC_NAC
    conteos["fec_nac_alu"] = int(mascara_nac.sum())
    df["fec_nac_alu"] = df["fec_nac_alu"].where(~mascara_nac).astype("Int32")

    mascara_gen = ~df["gen_alu"].isin(tuple(config.MAPA_GENERO))
    conteos["gen_alu"] = int(mascara_gen.sum())
    df["gen_alu"] = df["gen_alu"].where(~mascara_gen).astype("Int8")

    # mrun y cod_carrera llegan vacios en una fraccion de los registros; la
    # ingesta ya los convirtio a float por coercion. Aqui se normalizan al tipo
    # entero anulable que corresponde a un identificador.
    for columna, tipo in (("mrun", "Int64"), ("cod_carrera", "Int32")):
        if columna in df.columns:
            conteos[columna] = int(df[columna].isna().sum())
            df[columna] = df[columna].astype(tipo)

    if bitacora is not None:
        detalle = ", ".join(f"{k}={v:,}" for k, v in conteos.items() if v)
        bitacora.registrar(
            "marcar_sentinelas",
            f"Codigos SIES y vacios convertidos a NA ({detalle or 'sin ocurrencias'})",
            len(df),
            len(df),
        )
    return df


# Palabras que no se capitalizan cuando aparecen dentro de un nombre propio,
# para que "ARTE Y ARQUITECTURA" quede como "Arte y Arquitectura" y no como
# "Arte Y Arquitectura".
CONECTORES: tuple[str, ...] = (
    "y", "e", "o", "u", "de", "del", "la", "las", "el", "los",
    "en", "con", "para", "por", "al", "a",
)


def normalizar_texto(serie: pd.Series) -> pd.Series:
    """Homogeneiza una columna de texto: sin espacios sobrantes y en Titulo.

    Evita que variantes como "SEDE SANTIAGO" y "Sede Santiago " se cuenten como
    categorias distintas al agrupar, y respeta la ortografia castellana dejando
    los conectores en minuscula.

    El conector solo se convierte cuando queda rodeado de espacios. Asi los
    nombres que empiezan por uno de ellos se conservan intactos (la comuna "La
    Florida" no debe volverse "la Florida") y tampoco se altera la region
    "O'Higgins", donde la O va seguida de un apostrofo.

    Ejemplo
    -------
    >>> normalizar_texto(pd.Series(["  ARTE Y   ARQUITECTURA ", "LA FLORIDA"])).tolist()
    ['Arte y Arquitectura', 'La Florida']
    """
    texto = (
        serie.astype("string")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.title()
    )
    patron = r"(?<= )(" + "|".join(c.capitalize() for c in CONECTORES) + r")(?= )"
    return texto.str.replace(patron, lambda m: m.group(1).lower(), regex=True)


def normalizar_categorias(
    df: pd.DataFrame,
    columnas: tuple[str, ...] | None = None,
    bitacora: BitacoraLimpieza | None = None,
) -> pd.DataFrame:
    """Aplica ``normalizar_texto`` a las columnas categoricas del esquema.

    La normalizacion se ejecuta sobre los **valores unicos** de cada columna y
    luego se propaga con un mapeo. Aplicar las expresiones regulares fila por
    fila supondria procesar 1,7 millones de cadenas por columna; hacerlo sobre
    el catalogo de categorias reduce el trabajo a unos pocos miles de valores.
    """
    df = df.copy()
    if columnas is None:
        columnas = tuple(
            c for c, t in config.COLUMNAS_USADAS.items() if t == "category" and c in df
        )
    cambios = 0
    for columna in columnas:
        original = df[columna].astype("string")
        unicos = pd.Series(original.dropna().unique(), dtype="string")
        mapa = dict(zip(unicos, normalizar_texto(unicos)))
        normalizada = original.map(mapa).astype("string")
        cambios += int((original.fillna("") != normalizada.fillna("")).sum())
        df[columna] = normalizada.astype("category")

    if bitacora is not None:
        bitacora.registrar(
            "normalizar_categorias",
            f"{len(columnas)} columnas homogeneizadas; {cambios:,} celdas modificadas",
            len(df),
            len(df),
        )
    return df


def eliminar_duplicados(
    df: pd.DataFrame,
    claves: tuple[str, ...] = (
        "cat_periodo",
        "mrun",
        "cod_carrera",
        "fecha_obtencion_titulo",
    ),
    bitacora: BitacoraLimpieza | None = None,
) -> pd.DataFrame:
    """Elimina la repeticion exacta de un mismo titulo para un mismo estudiante.

    Dos precauciones deliberadas:

    1. Se conserva el caso de un estudiante con dos titulos distintos en el
       mismo anio (carreras diferentes): es un hecho real del sistema, no un
       error de registro.
    2. Las filas sin ``mrun`` quedan fuera del cotejo. Como pandas trata dos NA
       como iguales al buscar duplicados, incluirlas colapsaria estudiantes
       distintos en un unico registro.
    """
    antes = len(df)
    claves_presentes = [c for c in claves if c in df.columns]

    if "mrun" in df.columns:
        identificables = df["mrun"].notna()
        parte_id = (
            df.loc[identificables]
            .drop_duplicates(subset=claves_presentes, keep="first")
        )
        df = (
            pd.concat([parte_id, df.loc[~identificables]])
            .sort_index()
            .reset_index(drop=True)
        )
    else:  # pragma: no cover - el esquema siempre incluye mrun
        df = df.drop_duplicates(subset=claves_presentes, keep="first").reset_index(drop=True)

    if bitacora is not None:
        bitacora.registrar(
            "eliminar_duplicados",
            f"Clave: {' + '.join(claves_presentes)} (excluye filas sin mrun)",
            antes,
            len(df),
        )
    return df


def filtrar_nivel(
    df: pd.DataFrame, nivel: str = "Pregrado", bitacora: BitacoraLimpieza | None = None
) -> pd.DataFrame:
    """Restringe el analisis a un nivel formativo.

    El proyecto se acota a pregrado porque los postitulos y posgrados tienen
    planes de duracion muy heterogenea y su duracion teorica no es comparable
    con la de una carrera regular; mezclarlos distorsionaria la sobreduracion.
    """
    antes = len(df)
    df = df.loc[df["nivel_global"] == nivel].reset_index(drop=True)
    if bitacora is not None:
        bitacora.registrar("filtrar_nivel", f"nivel_global == '{nivel}'", antes, len(df))
    return df


def descartar_sin_insumos(
    df: pd.DataFrame,
    columnas: tuple[str, ...] = (
        "anio_ing_carr_ori",
        "sem_ing_carr_ori",
        "fecha_obtencion_titulo",
        "dur_total_carr",
    ),
    bitacora: BitacoraLimpieza | None = None,
) -> pd.DataFrame:
    """Elimina las filas sin los datos minimos para calcular la duracion real.

    Se opta por descartar y no imputar: imputar un anio de ingreso equivaldria a
    inventar la variable que el proyecto pretende medir. El volumen descartado
    se documenta para acotar el sesgo que esta decision introduce.
    """
    antes = len(df)
    presentes = [c for c in columnas if c in df.columns]
    df = df.dropna(subset=presentes).reset_index(drop=True)
    if bitacora is not None:
        bitacora.registrar(
            "descartar_sin_insumos", f"Filas sin {', '.join(presentes)}", antes, len(df)
        )
    return df
