"""Obtencion y consolidacion de los archivos anuales del SIES.

Estrategia: los seis CSV (~955 MB en total) se leen por bloques (chunks) para
no cargar el archivo completo en memoria, se convierten a tipos economicos y se
consolidan en un unico archivo Parquet. Parquet reduce ~10 veces el espacio y
conserva los tipos, de modo que las etapas siguientes parten siempre del mismo
insumo binario y no vuelven a parsear texto.
"""

from __future__ import annotations

import time
from pathlib import Path

import pandas as pd

from . import config


class ArchivoRawNoEncontrado(FileNotFoundError):
    """Se lanza cuando falta el CSV de un anio esperado en RAW_DIR."""


def listar_archivos_raw(
    raw_dir: Path | None = None, anios: tuple[int, ...] | None = None
) -> dict[int, Path]:
    """Localiza el CSV correspondiente a cada anio de la ventana de analisis.

    Parametros
    ----------
    raw_dir : Path, opcional
        Carpeta con los CSV originales. Por defecto ``config.RAW_DIR``.
    anios : tuple[int, ...], opcional
        Anios a buscar. Por defecto ``config.ANIOS``.

    Retorna
    -------
    dict[int, Path]
        Mapa anio -> ruta del archivo.

    Lanza
    -----
    ArchivoRawNoEncontrado
        Si algun anio no tiene archivo, para fallar temprano y con un mensaje
        claro en lugar de producir un consolidado incompleto.
    """
    raw_dir = Path(raw_dir) if raw_dir is not None else config.RAW_DIR
    anios = anios if anios is not None else config.ANIOS

    encontrados: dict[int, Path] = {}
    faltantes: list[int] = []
    for anio in anios:
        coincidencias = sorted(raw_dir.glob(config.PATRON_ARCHIVO.format(anio=anio)))
        if coincidencias:
            encontrados[anio] = coincidencias[0]
        else:
            faltantes.append(anio)

    if faltantes:
        raise ArchivoRawNoEncontrado(
            f"No se encontraron los CSV de {faltantes} en {raw_dir}. "
            "Descarguelos del portal SIES o defina la variable de entorno "
            "TITULADOS_RAW_DIR apuntando a la carpeta que los contiene."
        )
    return encontrados


def _convertir_tipos(bloque: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Convierte a numerico las columnas que lo requieren y cuenta coerciones.

    Todo el archivo se lee como texto para que un valor invalido no aborte la
    carga completa. Aqui se fuerza el tipo definitivo y se registra cuantos
    valores no pudieron convertirse: ese conteo es evidencia de calidad de
    datos que se reporta en la Fase 2.
    """
    coerciones: dict[str, int] = {}
    for columna, tipo in config.COLUMNAS_USADAS.items():
        if tipo == "category":
            continue
        serie = pd.to_numeric(bloque[columna], errors="coerce")
        nulos = int(serie.isna().sum())
        if nulos:
            coerciones[columna] = nulos
        # Los enteros se dejan como float si hubo coercion; el casteo estricto
        # se realiza en la etapa de limpieza, una vez decidido el tratamiento
        # de los faltantes.
        bloque[columna] = serie.astype(tipo) if nulos == 0 else serie
    return bloque, coerciones


def leer_anio(ruta: Path, chunksize: int = 200_000) -> tuple[pd.DataFrame, dict[str, int]]:
    """Lee un CSV anual por bloques y devuelve el DataFrame y sus coerciones."""
    bloques: list[pd.DataFrame] = []
    coerciones_totales: dict[str, int] = {}

    lector = pd.read_csv(
        ruta,
        sep=config.SEPARADOR,
        encoding=config.ENCODING,
        usecols=list(config.COLUMNAS_USADAS),
        dtype=str,
        chunksize=chunksize,
    )
    for bloque in lector:
        bloque, coerciones = _convertir_tipos(bloque)
        for columna, cantidad in coerciones.items():
            coerciones_totales[columna] = coerciones_totales.get(columna, 0) + cantidad
        bloques.append(bloque)

    df = pd.concat(bloques, ignore_index=True)
    return df, coerciones_totales


def consolidar(
    raw_dir: Path | None = None,
    destino: Path | None = None,
    guardar: bool = True,
    verboso: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Apila los seis anios en un unico DataFrame y lo persiste en Parquet.

    Retorna
    -------
    (df, bitacora)
        ``df`` es el consolidado y ``bitacora`` un DataFrame con una fila por
        anio (filas leidas, filas oficiales SIES, diferencia, tiempo y
        coerciones), que constituye la evidencia de trazabilidad de la ingesta.
    """
    destino = Path(destino) if destino is not None else config.PARQUET_CONSOLIDADO
    archivos = listar_archivos_raw(raw_dir)

    partes: list[pd.DataFrame] = []
    registros: list[dict[str, object]] = []

    for anio, ruta in archivos.items():
        inicio = time.perf_counter()
        df_anio, coerciones = leer_anio(ruta)
        segundos = time.perf_counter() - inicio

        oficiales = config.FILAS_OFICIALES_SIES.get(anio)
        registros.append(
            {
                "anio": anio,
                "archivo": ruta.name,
                "mb_origen": round(ruta.stat().st_size / 1024**2, 1),
                "filas_leidas": len(df_anio),
                "filas_oficiales_sies": oficiales,
                "diferencia": None if oficiales is None else len(df_anio) - oficiales,
                "columnas": df_anio.shape[1],
                "segundos": round(segundos, 1),
                "coerciones": sum(coerciones.values()),
            }
        )
        if verboso:
            print(f"[ingesta] {anio}: {len(df_anio):>8,} filas en {segundos:5.1f} s")
        partes.append(df_anio)

    df = pd.concat(partes, ignore_index=True)

    # Las categorias se asignan sobre el consolidado: si se hiciera por bloque,
    # cada uno tendria su propio catalogo y pandas degradaria el tipo a texto.
    for columna, tipo in config.COLUMNAS_USADAS.items():
        if tipo == "category":
            df[columna] = df[columna].astype("category")

    if guardar:
        destino.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(destino, index=False)
        if verboso:
            mb = destino.stat().st_size / 1024**2
            print(f"[ingesta] Parquet escrito en {destino} ({mb:,.1f} MB)")

    bitacora = pd.DataFrame(registros)
    return df, bitacora


def cargar_consolidado(ruta: Path | None = None) -> pd.DataFrame:
    """Carga el Parquet consolidado; exige haber ejecutado ``consolidar`` antes."""
    ruta = Path(ruta) if ruta is not None else config.PARQUET_CONSOLIDADO
    if not ruta.exists():
        raise ArchivoRawNoEncontrado(
            f"No existe {ruta}. Ejecute ingesta.consolidar() o el notebook "
            "F2/F2_1_Obtencion_Exploracion.ipynb antes de continuar."
        )
    return pd.read_parquet(ruta)
