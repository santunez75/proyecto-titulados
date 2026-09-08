"""Derivacion de las variables analiticas del proyecto.

El SIES publica la duracion *teorica* del plan de estudios, no el tiempo que
efectivamente tardo cada estudiante. La contribucion tecnica de esta fase es
reconstruir la duracion real a partir del anio y semestre de ingreso a la
carrera de origen y de la fecha de obtencion del titulo, y compararla con la
duracion teorica para obtener la sobreduracion, que es la variable objetivo del
proyecto.

Convencion de calculo
---------------------
Un titulo obtenido hasta julio se imputa al primer semestre del anio; desde
agosto, al segundo (``config.MES_CORTE_PRIMER_SEMESTRE``). La duracion real se
mide en semestres academicos e incluye tanto el semestre de ingreso como el de
egreso, de modo que un estudiante que ingresa y se titula dentro del mismo
semestre registra una duracion de 1 y no de 0.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import config
from .limpieza import BitacoraLimpieza


def derivar_calendario(df: pd.DataFrame) -> pd.DataFrame:
    """Descompone ``fecha_obtencion_titulo`` (AAAAMMDD) en sus componentes."""
    df = df.copy()
    fecha = df["fecha_obtencion_titulo"].astype("Int64")

    df["anio_titulo"] = (fecha // 10_000).astype("Int16")
    df["mes_titulo"] = ((fecha // 100) % 100).astype("Int8")
    df["semestre_titulo"] = np.where(
        df["mes_titulo"] <= config.MES_CORTE_PRIMER_SEMESTRE, 1, 2
    )
    df["semestre_titulo"] = pd.Series(df["semestre_titulo"], index=df.index).astype("Int8")
    df.loc[fecha.isna(), ["anio_titulo", "mes_titulo", "semestre_titulo"]] = pd.NA
    return df


def calcular_duracion_real(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula la duracion real de la trayectoria, en semestres academicos.

    duracion_real = (anio_titulo - anio_ingreso) * 2
                    + (semestre_titulo - semestre_ingreso) + 1
    """
    df = df.copy()
    if "semestre_titulo" not in df.columns:
        df = derivar_calendario(df)

    anios = (df["anio_titulo"].astype("Int32") - df["anio_ing_carr_ori"].astype("Int32"))
    semestres = (
        df["semestre_titulo"].astype("Int16") - df["sem_ing_carr_ori"].astype("Int16")
    )
    df["duracion_real_sem"] = (
        anios * config.SEMESTRES_POR_ANIO + semestres + 1
    ).astype("Int16")
    return df


def calcular_edad_titulacion(df: pd.DataFrame) -> pd.DataFrame:
    """Edad cumplida al momento de titularse, en anios.

    ``fec_nac_alu`` viene en formato AAAAMM, por lo que la edad se ajusta segun
    el mes: si el mes de nacimiento es posterior al de titulacion, el estudiante
    aun no habia cumplido anios.
    """
    df = df.copy()
    nacimiento = df["fec_nac_alu"].astype("Int64")
    anio_nac = (nacimiento // 100).astype("Int32")
    mes_nac = (nacimiento % 100).astype("Int16")

    edad = df["anio_titulo"].astype("Int32") - anio_nac
    aun_no_cumple = (mes_nac > df["mes_titulo"].astype("Int16")).fillna(False)
    df["edad_titulacion"] = (edad - aun_no_cumple.astype("Int32")).astype("Int16")

    # Edad de ingreso a la carrera, util para caracterizar trayectorias adultas.
    df["edad_ingreso"] = (
        df["anio_ing_carr_ori"].astype("Int32") - anio_nac
    ).astype("Int16")
    return df


def calcular_sobreduracion(df: pd.DataFrame) -> pd.DataFrame:
    """Compara la duracion real con la teorica y clasifica el rezago.

    Genera tres variables:

    - ``sobreduracion_sem``: semestres por sobre la duracion teorica total.
    - ``indice_duracion``: razon real/teorica (1.0 = exactamente lo planificado).
    - ``titulacion_oportuna``: verdadero si no hubo sobreduracion.
    """
    df = df.copy()
    teorica = df["dur_total_carr"].astype("Int16")

    df["sobreduracion_sem"] = (df["duracion_real_sem"] - teorica).astype("Int16")
    # La division se hace en float y se protege el caso teorica == 0, que en el
    # dataset corresponde a planes sin duracion informada.
    denominador = teorica.astype("float64").replace(0, np.nan)
    df["indice_duracion"] = (
        df["duracion_real_sem"].astype("float64") / denominador
    ).round(3)
    df["titulacion_oportuna"] = df["sobreduracion_sem"] <= 0
    df["categoria_rezago"] = clasificar_rezago(df["sobreduracion_sem"])
    return df


def clasificar_rezago(sobreduracion: pd.Series) -> pd.Series:
    """Traduce la sobreduracion en semestres a una categoria ordinal.

    Los cortes provienen de ``config.UMBRALES_REZAGO``: sin sobreduracion es
    titulacion oportuna; hasta 2 semestres, rezago leve; hasta 4, moderado; por
    sobre 4, severo.

    Ejemplo
    -------
    >>> clasificar_rezago(pd.Series([0, 2, 4, 9])).tolist()
    ['Oportuna', 'Rezago leve', 'Rezago moderado', 'Rezago severo']
    """
    etiquetas = [e for e, _ in config.UMBRALES_REZAGO] + [config.ETIQUETA_REZAGO_SEVERO]
    cortes = [-np.inf] + [u for _, u in config.UMBRALES_REZAGO] + [np.inf]
    categorias = pd.cut(
        sobreduracion.astype("float64"),
        bins=cortes,
        labels=etiquetas,
        right=True,
        ordered=True,
    )
    return categorias.astype("category")


def etiquetar_dimensiones(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega etiquetas legibles para las variables codificadas."""
    df = df.copy()
    df["genero"] = (
        df["gen_alu"].map(config.MAPA_GENERO).astype("category")
    )
    df["cohorte_ingreso"] = df["anio_ing_carr_ori"].astype("Int16")
    df["es_no_presencial"] = (df["modalidad"] == "No Presencial")
    return df


def marcar_atipicos(df: pd.DataFrame) -> pd.DataFrame:
    """Marca (sin eliminar) los registros fuera de los rangos plausibles.

    Se separan tres causas para poder cuantificarlas por separado en el informe:
    duracion imposible o excesiva, edad fuera de rango y duracion teorica nula.

    Los valores faltantes se marcan como atipicos de forma explicita: un
    registro sin fecha de nacimiento no permite verificar la plausibilidad de la
    edad, y dejar el indicador en NA haria que el filtro posterior descartara
    filas de manera silenciosa.
    """
    df = df.copy()
    df["atipico_duracion"] = (
        ~df["duracion_real_sem"].between(
            config.DURACION_REAL_MIN, config.DURACION_REAL_MAX
        )
    ).fillna(True).astype(bool)
    df["atipico_edad"] = (
        ~df["edad_titulacion"].between(config.EDAD_MIN, config.EDAD_MAX)
    ).fillna(True).astype(bool)
    df["atipico_teorica"] = (df["dur_total_carr"] <= 0).fillna(True).astype(bool)
    df["es_atipico"] = (
        df["atipico_duracion"] | df["atipico_edad"] | df["atipico_teorica"]
    )
    return df


def filtrar_atipicos(
    df: pd.DataFrame, bitacora: BitacoraLimpieza | None = None
) -> pd.DataFrame:
    """Elimina los registros marcados como atipicos y lo deja asentado."""
    antes = len(df)
    detalle = (
        f"duracion={int(df['atipico_duracion'].sum()):,}, "
        f"edad={int(df['atipico_edad'].sum()):,}, "
        f"teorica_nula={int(df['atipico_teorica'].sum()):,}"
    )
    df = df.loc[~df["es_atipico"]].reset_index(drop=True)
    if bitacora is not None:
        bitacora.registrar("filtrar_atipicos", detalle, antes, len(df))
    return df


def construir_dataset_analitico(
    df: pd.DataFrame, bitacora: BitacoraLimpieza | None = None
) -> pd.DataFrame:
    """Encadena todas las derivaciones sobre un consolidado ya depurado.

    Es el unico punto de entrada que deben usar los notebooks: garantiza que el
    orden de las transformaciones sea siempre el mismo y, por lo tanto, que el
    resultado sea reproducible.
    """
    antes = len(df)
    df = derivar_calendario(df)
    df = calcular_duracion_real(df)
    df = calcular_edad_titulacion(df)
    df = calcular_sobreduracion(df)
    df = etiquetar_dimensiones(df)
    df = marcar_atipicos(df)
    if bitacora is not None:
        bitacora.registrar(
            "construir_dataset_analitico",
            "Derivacion de duracion real, sobreduracion, edad y etiquetas",
            antes,
            len(df),
        )
    return df


def tabla_agregada(
    df: pd.DataFrame,
    dimensiones: list[str] | str,
    metrica: str = "sobreduracion_sem",
    minimo_casos: int = 30,
) -> pd.DataFrame:
    """Resume una metrica por una o mas dimensiones.

    Parametros
    ----------
    dimensiones : list[str] | str
        Columnas de agrupacion.
    metrica : str
        Variable numerica a resumir.
    minimo_casos : int
        Los grupos con menos casos que este umbral se descartan, para no
        publicar promedios calculados sobre poblaciones minimas.
    """
    if isinstance(dimensiones, str):
        dimensiones = [dimensiones]

    agrupado = df.groupby(dimensiones, observed=True).agg(
        titulados=(metrica, "size"),
        media=(metrica, "mean"),
        mediana=(metrica, "median"),
        p25=(metrica, lambda s: s.quantile(0.25)),
        p75=(metrica, lambda s: s.quantile(0.75)),
        pct_oportuna=("titulacion_oportuna", "mean"),
    )
    agrupado["media"] = agrupado["media"].round(2)
    agrupado["pct_oportuna"] = (100 * agrupado["pct_oportuna"]).round(1)
    agrupado = agrupado.loc[agrupado["titulados"] >= minimo_casos]
    return agrupado.sort_values("media", ascending=False).reset_index()


def razon_feminidad(df: pd.DataFrame, dimension: str) -> pd.DataFrame:
    """Participacion femenina por categoria, para el analisis de brechas.

    Devuelve el numero de titulados por sexo, el porcentaje de mujeres y la
    brecha de sobreduracion entre mujeres y hombres (negativa cuando las
    mujeres se titulan mas rapido).
    """
    base = df.dropna(subset=["genero"])
    conteo = (
        base.pivot_table(
            index=dimension,
            columns="genero",
            values="duracion_real_sem",
            aggfunc="size",
            observed=True,
        )
        .fillna(0)
        .astype(int)
    )
    conteo["total"] = conteo.sum(axis=1)
    conteo["pct_mujeres"] = (100 * conteo.get("Mujer", 0) / conteo["total"]).round(1)

    medias = base.pivot_table(
        index=dimension,
        columns="genero",
        values="sobreduracion_sem",
        aggfunc="mean",
        observed=True,
    )
    conteo["brecha_sobreduracion"] = (
        medias.get("Mujer") - medias.get("Hombre")
    ).round(2)
    return conteo.sort_values("pct_mujeres", ascending=False).reset_index()
