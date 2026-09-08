"""Funciones de visualizacion con estilo unificado.

Todas las figuras del proyecto se generan desde aqui para que compartan
tipografia, tamano, paleta y resolucion, y para que cada grafico quede guardado
en ``reports/figures`` con un nombre estable que el informe pueda referenciar.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from . import config


def aplicar_estilo() -> None:
    """Fija el estilo global de matplotlib/seaborn para todo el proyecto."""
    sns.set_theme(style="whitegrid", context="notebook")
    matplotlib.rcParams.update(
        {
            "figure.figsize": config.FIGSIZE,
            "figure.dpi": 100,
            "savefig.dpi": config.DPI,
            "savefig.bbox": "tight",
            "axes.titlesize": 13,
            "axes.titleweight": "bold",
            "axes.labelsize": 11,
            "axes.grid": True,
            "grid.alpha": 0.3,
            "font.size": 10,
            "legend.frameon": False,
        }
    )


def guardar(fig: plt.Figure, nombre: str, carpeta: Path | None = None) -> Path:
    """Guarda la figura en PNG y devuelve la ruta, para citarla en el informe."""
    carpeta = carpeta or config.FIGURES_DIR
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / f"{nombre}.png"
    fig.savefig(ruta)
    return ruta


def formato_es(valor: float, formato: str = "{:.1f}") -> str:
    """Formatea un numero segun la convencion chilena: coma decimal, punto de miles.

    Ejemplo
    -------
    >>> formato_es(203598, "{:,.0f}")
    '203.598'
    >>> formato_es(2.5, "{:.2f}")
    '2,50'
    """
    texto = formato.format(valor)
    # str.translate intercambia ambos simbolos en una sola pasada, sin
    # necesidad de un caracter centinela intermedio.
    return texto.translate(str.maketrans({",": ".", ".": ","}))


def _anotar_barras(ax: plt.Axes, formato: str = "{:.1f}", horizontal: bool = True) -> None:
    """Escribe el valor al final de cada barra, con formato numerico local."""
    for contenedor in ax.containers:
        ax.bar_label(
            contenedor,
            fmt=lambda v: formato_es(v, formato),
            padding=3,
            fontsize=9,
            color="#333333",
        )
    if horizontal:
        ax.margins(x=0.12)
    else:
        ax.margins(y=0.12)


def barras(
    datos: pd.Series,
    titulo: str,
    etiqueta_valor: str,
    color: str | None = None,
    horizontal: bool = True,
    formato: str = "{:.1f}",
    nombre_archivo: str | None = None,
) -> plt.Figure:
    """Grafico de barras ordenado, con los valores anotados."""
    fig, ax = plt.subplots()
    color = color or config.PALETA["primario"]
    # Los tipos anulables de pandas (Int16, Float64) no son interpretables por
    # matplotlib: se convierten a float antes de graficar.
    datos = datos.astype("float64")

    if horizontal:
        datos = datos.sort_values()
        ax.barh(datos.index.astype(str), datos.to_numpy(), color=color)
        ax.set_xlabel(etiqueta_valor)
    else:
        ax.bar(datos.index.astype(str), datos.to_numpy(), color=color)
        ax.set_ylabel(etiqueta_valor)

    ax.set_title(titulo)
    _anotar_barras(ax, formato, horizontal)
    fig.tight_layout()
    if nombre_archivo:
        guardar(fig, nombre_archivo)
    return fig


def barras_agrupadas(
    tabla: pd.DataFrame,
    titulo: str,
    etiqueta_valor: str,
    colores: dict[str, str] | None = None,
    nombre_archivo: str | None = None,
) -> plt.Figure:
    """Barras agrupadas a partir de una tabla ancha (filas = categorias)."""
    fig, ax = plt.subplots()
    paleta = colores or config.PALETA_GENERO
    tabla = tabla.astype("float64")
    tabla.plot(
        kind="barh",
        ax=ax,
        color=[paleta.get(c, config.PALETA["neutro"]) for c in tabla.columns],
        width=0.75,
    )
    ax.set_xlabel(etiqueta_valor)
    ax.set_ylabel("")
    ax.set_title(titulo)
    ax.legend(title="")
    fig.tight_layout()
    if nombre_archivo:
        guardar(fig, nombre_archivo)
    return fig


def serie_temporal(
    tabla: pd.DataFrame,
    titulo: str,
    etiqueta_valor: str,
    nombre_archivo: str | None = None,
    marcador: str = "o",
) -> plt.Figure:
    """Lineas por anio para una o varias series."""
    fig, ax = plt.subplots()
    tabla = tabla.astype("float64")
    for i, columna in enumerate(tabla.columns):
        ax.plot(
            tabla.index.astype(int),
            tabla[columna].to_numpy(),
            marker=marcador,
            linewidth=2,
            label=str(columna),
            color=list(config.PALETA.values())[i % len(config.PALETA)],
        )
    ax.set_xlabel("Anio del proceso de titulacion")
    ax.set_ylabel(etiqueta_valor)
    ax.set_title(titulo)
    if tabla.shape[1] > 1:
        ax.legend()
    fig.tight_layout()
    if nombre_archivo:
        guardar(fig, nombre_archivo)
    return fig


def histograma(
    serie: pd.Series,
    titulo: str,
    etiqueta_valor: str,
    bins: int = 40,
    referencia: float | None = 0.0,
    nombre_archivo: str | None = None,
) -> plt.Figure:
    """Histograma con una linea de referencia (por defecto, sobreduracion cero)."""
    fig, ax = plt.subplots()
    valores = serie.dropna().astype("float64").to_numpy()
    ax.hist(valores, bins=bins, color=config.PALETA["primario"], alpha=0.85)
    if referencia is not None:
        ax.axvline(
            referencia,
            color=config.PALETA["alerta"],
            linestyle="--",
            linewidth=1.5,
            label="Titulacion en el tiempo teorico",
        )
        ax.legend()
    ax.set_xlabel(etiqueta_valor)
    ax.set_ylabel("Titulados")
    ax.set_title(titulo)
    fig.tight_layout()
    if nombre_archivo:
        guardar(fig, nombre_archivo)
    return fig


def cajas_por_categoria(
    df: pd.DataFrame,
    categoria: str,
    valor: str,
    titulo: str,
    etiqueta_valor: str,
    nombre_archivo: str | None = None,
    max_categorias: int = 12,
) -> plt.Figure:
    """Diagramas de caja del valor por categoria, ordenados por mediana."""
    orden = (
        df.groupby(categoria, observed=True)[valor]
        .median()
        .sort_values(ascending=False)
        .head(max_categorias)
        .index
    )
    subconjunto = df.loc[df[categoria].isin(orden)]
    fig, ax = plt.subplots(figsize=(config.FIGSIZE[0], config.FIGSIZE[1] + 1))
    sns.boxplot(
        data=subconjunto,
        y=categoria,
        x=valor,
        order=orden,
        ax=ax,
        color=config.PALETA["primario"],
        fliersize=0,
        width=0.6,
    )
    ax.set_xlabel(etiqueta_valor)
    ax.set_ylabel("")
    ax.set_title(titulo)
    fig.tight_layout()
    if nombre_archivo:
        guardar(fig, nombre_archivo)
    return fig


def mapa_calor(
    tabla: pd.DataFrame,
    titulo: str,
    etiqueta_valor: str,
    nombre_archivo: str | None = None,
    formato: str = ".1f",
) -> plt.Figure:
    """Mapa de calor para cruces de dos dimensiones categoricas."""
    fig, ax = plt.subplots(figsize=(config.FIGSIZE[0], config.FIGSIZE[1] + 1))
    sns.heatmap(
        tabla.astype("float64"),
        annot=True,
        fmt=formato,
        cmap="YlOrRd",
        linewidths=0.5,
        cbar_kws={"label": etiqueta_valor},
        ax=ax,
    )
    ax.set_title(titulo)
    ax.set_xlabel("")
    ax.set_ylabel("")
    fig.tight_layout()
    if nombre_archivo:
        guardar(fig, nombre_archivo)
    return fig
