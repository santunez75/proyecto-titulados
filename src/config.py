"""Configuracion central del proyecto.

Concentra rutas, esquema del dataset y constantes de negocio para que ningun
notebook contenga rutas absolutas ni "numeros magicos". Cambiar una ruta o un
umbral aqui se propaga a todo el pipeline, lo que es requisito de
reproducibilidad: el proyecto se ejecuta igual en cualquier equipo.
"""

from __future__ import annotations

import os
from pathlib import Path

# --- Rutas -----------------------------------------------------------------
# BASE_DIR se resuelve desde la ubicacion de este archivo (src/config.py), de
# modo que el codigo funciona igual si se invoca desde un notebook, un test o
# la linea de comandos.
BASE_DIR: Path = Path(__file__).resolve().parents[1]

# La carpeta de datos crudos puede sobreescribirse con la variable de entorno
# TITULADOS_RAW_DIR (util cuando los CSV viven fuera del repositorio, que es lo
# habitual: pesan ~955 MB y no pueden versionarse en GitHub).
RAW_DIR: Path = Path(os.environ.get("TITULADOS_RAW_DIR", BASE_DIR / "data" / "raw"))
INTERIM_DIR: Path = BASE_DIR / "data" / "interim"
PROCESSED_DIR: Path = BASE_DIR / "data" / "processed"
FIGURES_DIR: Path = BASE_DIR / "reports" / "figures"
TABLES_DIR: Path = BASE_DIR / "reports" / "tables"

for _d in (INTERIM_DIR, PROCESSED_DIR, FIGURES_DIR, TABLES_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# Artefactos del pipeline
PARQUET_CONSOLIDADO: Path = INTERIM_DIR / "titulados_2020_2025_consolidado.parquet"
PARQUET_LIMPIO: Path = PROCESSED_DIR / "titulados_pregrado_analitico.parquet"
MUESTRA_CSV: Path = PROCESSED_DIR / "muestra_titulados_5000.csv"

# --- Cobertura temporal ----------------------------------------------------
ANIOS: tuple[int, ...] = (2020, 2021, 2022, 2023, 2024, 2025)
PATRON_ARCHIVO: str = "*Titulados_Ed_Superior_{anio}_WEB.csv"
SEPARADOR: str = ";"
ENCODING: str = "utf-8"

# Conteos oficiales publicados por el SIES en el esquema de registro
# ("ER titulados Ed.Superior 2007 - 2025, WEB.pdf", seccion 1.1). Se usan como
# prueba de integridad de la ingesta: si no calzan, la carga esta incompleta.
FILAS_OFICIALES_SIES: dict[int, int] = {
    2020: 203_598,
    2021: 281_491,
    2022: 291_460,
    2023: 299_893,
    2024: 304_727,
    2025: 328_998,
}

# --- Esquema ---------------------------------------------------------------
# Subconjunto de columnas efectivamente utilizado. Se descartan nombre_grado,
# tipo_inst_3, version y la clasificacion CINE-F 1997 (cine_f_97_*) por ser
# redundantes frente a CINE-F 2013, decision documentada en el informe.
COLUMNAS_USADAS: dict[str, str] = {
    "cat_periodo": "int16",
    "mrun": "int64",
    "gen_alu": "int8",
    "fec_nac_alu": "int32",
    "rango_edad": "category",
    "anio_ing_carr_ori": "int32",
    "sem_ing_carr_ori": "int8",
    "fecha_obtencion_titulo": "int32",
    "tipo_inst_1": "category",
    "tipo_inst_2": "category",
    "cod_inst": "int16",
    "nomb_inst": "category",
    "cod_carrera": "int32",
    "nomb_carrera": "category",
    "nivel_global": "category",
    "nivel_carrera_1": "category",
    "nivel_carrera_2": "category",
    "dur_estudio_carr": "int16",
    "dur_proceso_tit": "int16",
    "dur_total_carr": "int16",
    "region_sede": "category",
    "provincia_sede": "category",
    "comuna_sede": "category",
    "jornada": "category",
    "modalidad": "category",
    "tipo_plan_carr": "category",
    "area_conocimiento": "category",
    "area_generica": "category",
    "cine_f_13_area": "category",
    "cine_f_13_subarea": "category",
}

COLUMNAS_DESCARTADAS: dict[str, str] = {
    "nombre_titulo": "Texto libre de alta cardinalidad; no aporta al analisis agregado.",
    "nombre_grado": "Vacio en carreras tecnicas; redundante con nivel_carrera_1.",
    "tipo_inst_3": "Desagregacion de tipo_inst_2 sin uso en las preguntas planteadas.",
    "anio_ing_carr_act": "Refiere a convalidacion; el SIES indica usar la carrera de origen.",
    "sem_ing_carr_act": "Idem anterior.",
    "cod_sede": "El analisis territorial se realiza a nivel de comuna/region, no de sede.",
    "nomb_sede": "Idem anterior.",
    "version": "Metadato administrativo del plan, sin valor analitico.",
    "cine_f_97_area": "Clasificacion CINE-F 1997, superada por CINE-F 2013.",
    "cine_f_97_subarea": "Idem anterior.",
}

# --- Diccionarios de dominio ----------------------------------------------
# Fuente: esquema de registro SIES, seccion 1.2.
MAPA_GENERO: dict[int, str] = {1: "Hombre", 2: "Mujer"}

# Codigos centinela que el SIES usa en lugar de un valor faltante explicito.
SENTINELAS_ANIO_INGRESO: tuple[int, ...] = (1900, 9995, 9998, 9999)
SENTINELA_FECHA: int = 19000101
SENTINELA_FEC_NAC: int = 190001
SEMESTRES_VALIDOS: tuple[int, ...] = (1, 2)

# --- Reglas de negocio -----------------------------------------------------
SEMESTRES_POR_ANIO: int = 2
MES_CORTE_PRIMER_SEMESTRE: int = 7  # titulos hasta julio -> semestre 1

# Limites de plausibilidad para la duracion real reconstruida (en semestres).
# 1 semestre es el minimo logico; 40 semestres (20 anios) es el tope adoptado
# para descartar trayectorias no representativas del fenomeno estudiado.
DURACION_REAL_MIN: int = 1
DURACION_REAL_MAX: int = 40

# Corte etario de plausibilidad al momento de titularse.
EDAD_MIN: int = 15
EDAD_MAX: int = 90

# Umbrales de la clasificacion de rezago (en semestres de sobreduracion).
UMBRALES_REZAGO: tuple[tuple[str, float], ...] = (
    ("Oportuna", 0.0),
    ("Rezago leve", 2.0),
    ("Rezago moderado", 4.0),
)
ETIQUETA_REZAGO_SEVERO: str = "Rezago severo"

# --- Estilo de visualizacion ----------------------------------------------
PALETA: dict[str, str] = {
    "primario": "#1F4E79",
    "secundario": "#C55A11",
    "acento": "#2E7D32",
    "neutro": "#6C757D",
    "alerta": "#B22222",
}
PALETA_GENERO: dict[str, str] = {"Hombre": "#1F4E79", "Mujer": "#C55A11"}
FIGSIZE: tuple[float, float] = (10.0, 5.5)
DPI: int = 150


def describir_entorno() -> dict[str, str]:
    """Devuelve versiones de Python y librerias clave para trazabilidad.

    Se invoca al inicio de cada notebook: deja registrada en la salida
    ejecutada la version exacta con la que se produjeron los resultados.
    """
    import platform
    import sys

    versiones = {
        "python": sys.version.split()[0],
        "plataforma": platform.platform(),
        "ejecutable": sys.executable,
    }
    for nombre in ("numpy", "pandas", "matplotlib", "seaborn", "pyarrow"):
        try:
            modulo = __import__(nombre)
            versiones[nombre] = getattr(modulo, "__version__", "desconocida")
        except ImportError:  # pragma: no cover - depende del entorno
            versiones[nombre] = "no instalado"
    return versiones
