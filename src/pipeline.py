"""Orquestador del flujo de datos de la Fase 2.

Encadena ingesta, limpieza, transformacion y validacion en una sola llamada
reproducible. Los notebooks usan estas mismas funciones paso a paso; este
modulo permite ademas ejecutar todo el pipeline desde la linea de comandos:

    python -m src.pipeline

lo que sirve como prueba de que el proyecto corre de inicio a fin sin errores.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from . import config, ingesta, limpieza, transformacion, validacion


def ejecutar(
    forzar_ingesta: bool = False, guardar: bool = True, verboso: bool = True
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Ejecuta el pipeline completo y devuelve dataset, bitacora y validacion."""
    if forzar_ingesta or not config.PARQUET_CONSOLIDADO.exists():
        df, bitacora_ingesta = ingesta.consolidar(verboso=verboso)
        if verboso:
            print(bitacora_ingesta.to_string(index=False))
    else:
        df = ingesta.cargar_consolidado()
        if verboso:
            print(f"[pipeline] Consolidado cargado: {len(df):,} filas")

    bitacora = limpieza.BitacoraLimpieza()
    bitacora.registrar("consolidado_inicial", "Union de los seis anios", len(df), len(df))

    df = limpieza.marcar_sentinelas(df, bitacora)
    df = limpieza.normalizar_categorias(df, bitacora=bitacora)
    df = limpieza.filtrar_nivel(df, bitacora=bitacora)
    df = limpieza.eliminar_duplicados(df, bitacora=bitacora)
    df = limpieza.descartar_sin_insumos(df, bitacora=bitacora)
    df = transformacion.construir_dataset_analitico(df, bitacora)
    df = transformacion.filtrar_atipicos(df, bitacora)

    validador = validacion.validador_estandar()
    reporte = validador.ejecutar(df)

    if verboso:
        print(bitacora.a_dataframe().to_string(index=False))
        print(reporte[["regla", "estado", "detalle"]].to_string(index=False))
        print(validador.resumen())

    if guardar:
        df.to_parquet(config.PARQUET_LIMPIO, index=False)
        df.sample(5_000, random_state=42).to_csv(config.MUESTRA_CSV, index=False)
        bitacora.a_dataframe().to_csv(
            config.TABLES_DIR / "bitacora_limpieza.csv", index=False
        )
        reporte.to_csv(config.TABLES_DIR / "reporte_validacion.csv", index=False)
        if verboso:
            mb = config.PARQUET_LIMPIO.stat().st_size / 1024**2
            print(f"[pipeline] Dataset analitico: {config.PARQUET_LIMPIO} ({mb:,.1f} MB)")

    if not validador.aprobado:
        raise RuntimeError(
            "El dataset no supero las reglas criticas de validacion:\n"
            + reporte.loc[reporte["estado"] == "FALLA"].to_string(index=False)
        )
    return df, bitacora.a_dataframe(), reporte


def cargar_analitico(ruta: Path | None = None) -> pd.DataFrame:
    """Carga el dataset analitico ya procesado."""
    ruta = Path(ruta) if ruta is not None else config.PARQUET_LIMPIO
    if not ruta.exists():
        raise FileNotFoundError(
            f"No existe {ruta}. Ejecute `python -m src.pipeline` o el notebook "
            "F2/F2_2_Limpieza_Transformacion.ipynb."
        )
    return pd.read_parquet(ruta)


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada de linea de comandos."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--forzar-ingesta",
        action="store_true",
        help="Vuelve a leer los CSV originales aunque exista el Parquet consolidado.",
    )
    parser.add_argument(
        "--sin-guardar",
        action="store_true",
        help="Ejecuta el pipeline sin escribir archivos de salida.",
    )
    args = parser.parse_args(argv)

    ejecutar(forzar_ingesta=args.forzar_ingesta, guardar=not args.sin_guardar)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
