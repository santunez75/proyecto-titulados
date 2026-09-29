"""Exporta el dataset analitico a un modelo en estrella listo para Power BI.

Genera en ``powerbi/``:

- ``hechos_titulados.parquet``  1.246.760 filas: metricas, claves y el score
  de riesgo del modelo logistico de la Fase 3.
- ``dim_institucion.csv``, ``dim_carrera.csv``, ``dim_territorio.csv``,
  ``dim_tiempo.csv``  tablas de dimension pequenas, en CSV para poder abrirlas
  en Excel y entender el modelo.
- ``muestra_hechos.csv``  5.000 filas de la tabla de hechos, por si se quiere
  inspeccionar el contenido sin abrir el Parquet.

El score ``prob_rezago`` es la probabilidad estimada de NO titularse en el
plazo teorico, calculada con ``RegresionLogisticaGD`` (Fase 3). Se ajusta en
una particion de entrenamiento y se aplica a todas las filas.

Uso:
    .venv\\Scripts\\python.exe -m scripts.exportar_powerbi
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from src.nucleo.fachada import (  # noqa: E402
    VARIABLES_CATEGORICAS,
    VARIABLES_NUMERICAS,
    cargar_datos,
)
from src.nucleo.modelos import RegresionLogisticaGD  # noqa: E402
from src.nucleo.preparacion import (  # noqa: E402
    PreparadorModelacion,
    dividir_entrenamiento_prueba,
)

SALIDA = RAIZ / "powerbi"
SIN_DATO = -1  # clave para las filas sin codigo de carrera


def _clave_carrera(df: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame]:
    """Clave subrogada por carrera-institucion.

    ``cod_carrera`` no es unico entre instituciones (731 codigos para 4.682
    combinaciones reales), asi que la dimension se construye sobre el par
    institucion-carrera y se numera de 1 en adelante.
    """
    columnas = ["cod_inst", "cod_carrera", "nomb_carrera", "area_conocimiento",
                "area_generica", "cine_f_13_area", "cine_f_13_subarea"]
    dim = (
        df[columnas]
        .astype({c: "string" for c in columnas})
        .drop_duplicates()
        .sort_values(["cod_inst", "nomb_carrera"])
        .reset_index(drop=True)
    )
    dim.insert(0, "id_carrera", np.arange(1, len(dim) + 1))
    clave = df[columnas].astype({c: "string" for c in columnas}).merge(
        dim, on=columnas, how="left"
    )["id_carrera"]
    return clave.fillna(SIN_DATO).astype("int32"), dim


def _clave_territorio(df: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame]:
    columnas = ["region_sede", "provincia_sede", "comuna_sede"]
    dim = (
        df[columnas]
        .astype({c: "string" for c in columnas})
        .drop_duplicates()
        .sort_values(columnas)
        .reset_index(drop=True)
    )
    dim.insert(0, "id_territorio", np.arange(1, len(dim) + 1))
    clave = df[columnas].astype({c: "string" for c in columnas}).merge(
        dim, on=columnas, how="left"
    )["id_territorio"]
    return clave.fillna(SIN_DATO).astype("int32"), dim


def _dimension_tiempo(df: pd.DataFrame) -> pd.DataFrame:
    dim = (
        df[["anio_titulo", "semestre_titulo"]]
        .drop_duplicates()
        .dropna()
        .astype("int32")
        .sort_values(["anio_titulo", "semestre_titulo"])
        .reset_index(drop=True)
    )
    dim["id_periodo"] = dim["anio_titulo"] * 10 + dim["semestre_titulo"]
    dim["periodo"] = dim["anio_titulo"].astype(str) + "-S" + dim["semestre_titulo"].astype(str)
    return dim[["id_periodo", "anio_titulo", "semestre_titulo", "periodo"]]


def _score_riesgo(df: pd.DataFrame, semilla: int = 42, limite_ajuste: int = 200_000) -> np.ndarray:
    """Probabilidad estimada de NO titularse en el plazo teorico.

    El modelo se ajusta sobre una particion de entrenamiento (para no evaluarse
    a si mismo) y se aplica a todas las filas. Devuelve 1 - P(oportuna), de modo
    que un valor alto signifique mas riesgo de rezago.
    """
    columnas = list(VARIABLES_NUMERICAS) + list(VARIABLES_CATEGORICAS) + ["titulacion_oportuna"]
    completo = df[columnas].dropna()
    muestra = completo.sample(min(limite_ajuste, len(completo)), random_state=semilla)

    preparador = PreparadorModelacion(VARIABLES_NUMERICAS, VARIABLES_CATEGORICAS)
    indices_ent, _ = dividir_entrenamiento_prueba(len(muestra), semilla=semilla)
    entrenamiento = muestra.iloc[indices_ent]

    X_ent = preparador.ajustar_transformar(entrenamiento)
    y_ent = entrenamiento["titulacion_oportuna"].to_numpy(dtype="float64")
    modelo = RegresionLogisticaGD(tasa_aprendizaje=0.5, iteraciones=1500).ajustar(X_ent, y_ent)

    # Se puntua todo el dataset; las filas con datos faltantes quedan en NaN.
    utilizables = df[list(VARIABLES_NUMERICAS) + list(VARIABLES_CATEGORICAS)].notna().all(axis=1)
    score = np.full(len(df), np.nan)
    if utilizables.any():
        X = preparador.transformar(df.loc[utilizables])
        score[utilizables.to_numpy()] = 1.0 - modelo.predecir_probabilidad(X)
    return score


def main() -> None:
    SALIDA.mkdir(exist_ok=True)
    df, origen = cargar_datos()
    print(f"Dataset {origen}: {len(df):,} filas".replace(",", "."))

    hechos = pd.DataFrame(
        {
            "id_titulado": np.arange(1, len(df) + 1, dtype="int32"),
            "cod_inst": df["cod_inst"].astype("int32"),
            "id_periodo": (df["anio_titulo"].astype("int32") * 10
                           + df["semestre_titulo"].astype("int32")),
            # Atributos de baja cardinalidad: se dejan en la tabla de hechos
            # para que el modelo sea simple de entender y filtrar.
            "genero": df["genero"].astype("string"),
            "modalidad": df["modalidad"].astype("string"),
            "jornada": df["jornada"].astype("string"),
            "rango_edad": df["rango_edad"].astype("string"),
            "categoria_rezago": df["categoria_rezago"].astype("string"),
            "cohorte_ingreso": df["cohorte_ingreso"].astype("Int16"),
            # Metricas
            "duracion_teorica_sem": df["dur_total_carr"].astype("Int16"),
            "duracion_real_sem": df["duracion_real_sem"].astype("Int16"),
            "sobreduracion_sem": df["sobreduracion_sem"].astype("Int16"),
            "indice_duracion": df["indice_duracion"].astype("float64"),
            "titulacion_oportuna": df["titulacion_oportuna"].astype("boolean"),
            "edad_ingreso": df["edad_ingreso"].astype("Int16"),
            "edad_titulacion": df["edad_titulacion"].astype("Int16"),
            "es_atipico": df["es_atipico"].astype("boolean"),
        }
    )
    hechos["id_carrera"], dim_carrera = _clave_carrera(df)
    hechos["id_territorio"], dim_territorio = _clave_territorio(df)

    print("Ajustando el modelo logistico y puntuando las filas...")
    hechos["prob_rezago"] = _score_riesgo(df)
    cubiertas = hechos["prob_rezago"].notna().sum()
    print(f"  score calculado en {cubiertas:,} filas".replace(",", "."))

    dim_institucion = (
        df[["cod_inst", "nomb_inst", "tipo_inst_1", "tipo_inst_2"]]
        .astype({"nomb_inst": "string", "tipo_inst_1": "string", "tipo_inst_2": "string"})
        .drop_duplicates("cod_inst")
        .sort_values("nomb_inst")
    )
    dim_tiempo = _dimension_tiempo(df)

    hechos.to_parquet(SALIDA / "hechos_titulados.parquet", index=False)
    dim_institucion.to_csv(SALIDA / "dim_institucion.csv", index=False, encoding="utf-8-sig")
    dim_carrera.to_csv(SALIDA / "dim_carrera.csv", index=False, encoding="utf-8-sig")
    dim_territorio.to_csv(SALIDA / "dim_territorio.csv", index=False, encoding="utf-8-sig")
    dim_tiempo.to_csv(SALIDA / "dim_tiempo.csv", index=False, encoding="utf-8-sig")
    # Formato chileno (; como separador de columnas y coma decimal): Power BI
    # con configuracion regional espanola interpreta el punto como separador de
    # miles, de modo que un CSV con decimales en punto convierte 0,81 en 81.
    hechos.to_csv(SALIDA / "hechos_titulados.csv", index=False,
                  encoding="utf-8-sig", sep=";", decimal=",")
    hechos.sample(5_000, random_state=42).to_csv(
        SALIDA / "muestra_hechos.csv", index=False, encoding="utf-8-sig",
        sep=";", decimal=","
    )

    print(f"\nArchivos en {SALIDA}:")
    for archivo in sorted(SALIDA.iterdir()):
        print(f"  {archivo.name:32} {archivo.stat().st_size / 1024 / 1024:7.2f} MB")
    print(f"\nHechos: {len(hechos):,} filas".replace(",", "."))
    print(f"Dimensiones: institucion {len(dim_institucion)}, carrera {len(dim_carrera)}, "
          f"territorio {len(dim_territorio)}, tiempo {len(dim_tiempo)}")


if __name__ == "__main__":
    main()
