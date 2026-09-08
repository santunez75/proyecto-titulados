"""Pruebas automatizadas del pipeline de datos.

Cubren los tres escenarios exigidos por la Fase 2: casos normales, casos limite
(valores en el borde de cada regla) y excepciones (entradas invalidas que deben
fallar de forma controlada). Se ejecutan con:

    pytest -v

No dependen de los CSV originales: construyen DataFrames minimos en memoria,
por lo que corren en cualquier equipo en menos de un segundo.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import config, ingesta, limpieza, transformacion, validacion  # noqa: E402


# --------------------------------------------------------------------------
# Datos de prueba
# --------------------------------------------------------------------------
def _fila(**cambios) -> dict:
    """Fila valida de referencia; los tests sobreescriben solo lo que evaluan."""
    base = {
        "cat_periodo": 2024,
        "mrun": 1001,
        "gen_alu": 2,
        "fec_nac_alu": 199805,
        "rango_edad": "25 A 29 Anos",
        "anio_ing_carr_ori": 2018,
        "sem_ing_carr_ori": 1,
        "fecha_obtencion_titulo": 20241220,
        "tipo_inst_1": "Universidades",
        "tipo_inst_2": "Universidades Privadas",
        "cod_inst": 31,
        "nomb_inst": "Universidad X",
        "cod_carrera": 41,
        "nomb_carrera": "Enfermeria",
        "nivel_global": "Pregrado",
        "nivel_carrera_1": "Profesional Con Licenciatura",
        "nivel_carrera_2": "Carreras Profesionales",
        "dur_estudio_carr": 10,
        "dur_proceso_tit": 0,
        "dur_total_carr": 10,
        "region_sede": "Maule",
        "provincia_sede": "Talca",
        "comuna_sede": "Talca",
        "jornada": "Diurna",
        "modalidad": "Presencial",
        "tipo_plan_carr": "Plan Regular",
        "area_conocimiento": "Salud",
        "area_generica": "Enfermeria",
        "cine_f_13_area": "Salud Y Bienestar",
        "cine_f_13_subarea": "Salud",
    }
    base.update(cambios)
    return base


@pytest.fixture
def df_base() -> pd.DataFrame:
    return pd.DataFrame([_fila()])


# --------------------------------------------------------------------------
# Casos normales
# --------------------------------------------------------------------------
def test_duracion_real_caso_normal(df_base):
    """Ingreso 2018-1 y titulo en diciembre de 2024 => 14 semestres."""
    resultado = transformacion.calcular_duracion_real(
        transformacion.derivar_calendario(df_base)
    )
    assert resultado.loc[0, "duracion_real_sem"] == 14


def test_sobreduracion_y_categoria(df_base):
    """14 semestres reales contra 10 teoricos => 4 de sobreduracion (moderado)."""
    df = transformacion.construir_dataset_analitico(df_base)
    assert df.loc[0, "sobreduracion_sem"] == 4
    assert df.loc[0, "indice_duracion"] == 1.4
    assert df.loc[0, "categoria_rezago"] == "Rezago moderado"
    assert not df.loc[0, "titulacion_oportuna"]


def test_edad_descuenta_mes_no_cumplido(df_base):
    """Nacida en mayo de 1998 y titulada en diciembre de 2024 => 26 anios."""
    df = transformacion.construir_dataset_analitico(df_base)
    assert df.loc[0, "edad_titulacion"] == 26


def test_edad_cuando_aun_no_cumple_anios():
    """Nacida en diciembre y titulada en marzo: aun no cumplio anios."""
    df = pd.DataFrame([_fila(fec_nac_alu=199812, fecha_obtencion_titulo=20240315)])
    resultado = transformacion.construir_dataset_analitico(df)
    assert resultado.loc[0, "edad_titulacion"] == 25


def test_semestre_de_titulacion_segun_mes():
    """Julio pertenece al primer semestre; agosto, al segundo."""
    df = pd.DataFrame(
        [
            _fila(fecha_obtencion_titulo=20240715),
            _fila(mrun=1002, fecha_obtencion_titulo=20240801),
        ]
    )
    resultado = transformacion.derivar_calendario(df)
    assert resultado["semestre_titulo"].tolist() == [1, 2]


# --------------------------------------------------------------------------
# Casos limite
# --------------------------------------------------------------------------
def test_duracion_minima_es_uno():
    """Ingreso y titulacion en el mismo semestre => 1, nunca 0."""
    df = pd.DataFrame(
        [_fila(anio_ing_carr_ori=2024, fecha_obtencion_titulo=20240310)]
    )
    resultado = transformacion.calcular_duracion_real(
        transformacion.derivar_calendario(df)
    )
    assert resultado.loc[0, "duracion_real_sem"] == 1


def test_clasificacion_en_los_bordes():
    """Los cortes 0, 2 y 4 pertenecen a la categoria inferior."""
    serie = pd.Series([-3, 0, 1, 2, 3, 4, 5])
    esperado = [
        "Oportuna",
        "Oportuna",
        "Rezago leve",
        "Rezago leve",
        "Rezago moderado",
        "Rezago moderado",
        "Rezago severo",
    ]
    assert transformacion.clasificar_rezago(serie).tolist() == esperado


def test_sentinelas_se_convierten_en_na():
    """Los codigos 9999 y 19000101 deben quedar como NA, no como numeros."""
    df = pd.DataFrame(
        [_fila(anio_ing_carr_ori=9999, sem_ing_carr_ori=0, fec_nac_alu=190001)]
    )
    resultado = limpieza.marcar_sentinelas(df)
    assert pd.isna(resultado.loc[0, "anio_ing_carr_ori"])
    assert pd.isna(resultado.loc[0, "sem_ing_carr_ori"])
    assert pd.isna(resultado.loc[0, "fec_nac_alu"])


def test_normalizacion_de_texto_respeta_nombres_propios():
    """Los conectores van en minuscula, pero no cuando abren el nombre."""
    entrada = pd.Series([
        "  ARTE Y   ARQUITECTURA ",
        "LA FLORIDA",
        "LIB. GRAL. B. O'HIGGINS",
        "UNIVERSIDAD DE LOS ANDES",
    ])
    esperado = [
        "Arte y Arquitectura",
        "La Florida",
        "Lib. Gral. B. O'Higgins",
        "Universidad de los Andes",
    ]
    assert limpieza.normalizar_texto(entrada).tolist() == esperado


def test_duplicados_sin_mrun_no_se_colapsan():
    """Dos estudiantes sin identificador no son el mismo estudiante."""
    df = pd.DataFrame([_fila(mrun=None), _fila(mrun=None)])
    df = limpieza.marcar_sentinelas(df)
    resultado = limpieza.eliminar_duplicados(df)
    assert len(resultado) == 2


def test_duplicado_exacto_se_elimina():
    df = pd.DataFrame([_fila(), _fila()])
    df = limpieza.marcar_sentinelas(df)
    assert len(limpieza.eliminar_duplicados(df)) == 1


def test_duracion_teorica_cero_no_divide_por_cero():
    """Un plan sin duracion informada produce indice NA, no una excepcion."""
    df = pd.DataFrame([_fila(dur_total_carr=0)])
    resultado = transformacion.construir_dataset_analitico(df)
    assert pd.isna(resultado.loc[0, "indice_duracion"])
    assert bool(resultado.loc[0, "atipico_teorica"])


def test_registro_sin_fecha_nacimiento_se_marca_atipico():
    """Sin fecha de nacimiento no se puede validar la edad: se excluye."""
    df = pd.DataFrame([_fila(fec_nac_alu=190001)])
    df = limpieza.marcar_sentinelas(df)
    resultado = transformacion.construir_dataset_analitico(df)
    assert bool(resultado.loc[0, "es_atipico"])


# --------------------------------------------------------------------------
# Excepciones y manejo de errores
# --------------------------------------------------------------------------
def test_archivos_faltantes_lanza_excepcion(tmp_path):
    with pytest.raises(ingesta.ArchivoRawNoEncontrado):
        ingesta.listar_archivos_raw(raw_dir=tmp_path)


def test_cargar_consolidado_inexistente(tmp_path):
    with pytest.raises(ingesta.ArchivoRawNoEncontrado):
        ingesta.cargar_consolidado(tmp_path / "no_existe.parquet")


def test_validador_detecta_dataset_corrupto(df_base):
    """Una duracion imposible debe hacer fallar la regla de rango."""
    df = transformacion.construir_dataset_analitico(df_base)
    df.loc[0, "duracion_real_sem"] = 999
    validador = validacion.validador_estandar()
    reporte = validador.ejecutar(df)
    estados = dict(zip(reporte["regla"], reporte["estado"]))
    assert estados["rango_duracion_real"] == "FALLA"
    assert not validador.aprobado


def test_validador_aprueba_dataset_correcto():
    """Un dataset correcto que cubre los seis anios pasa todas las reglas."""
    filas = [
        _fila(
            mrun=1000 + i,
            cat_periodo=anio,
            anio_ing_carr_ori=anio - 6,
            fecha_obtencion_titulo=int(f"{anio}1220"),
        )
        for i, anio in enumerate(config.ANIOS)
    ]
    df = transformacion.construir_dataset_analitico(pd.DataFrame(filas))
    validador = validacion.validador_estandar()
    validador.ejecutar(df)
    assert validador.aprobado, validador.reporte.to_string(index=False)


def test_estado_antes_de_ejecutar_lanza_error():
    validador = validacion.validador_estandar()
    with pytest.raises(RuntimeError):
        _ = validador.aprobado


def test_regla_con_excepcion_se_reporta_como_falla(df_base):
    """Si una regla revienta, el motor lo informa en vez de caerse."""
    def regla_rota(_: pd.DataFrame) -> tuple[bool, str]:
        raise ValueError("columna inexistente")

    validador = validacion.ValidadorDataset(
        [validacion.Regla("rota", "Regla que falla", regla_rota)]
    )
    reporte = validador.ejecutar(df_base)
    assert reporte.loc[0, "estado"] == "FALLA"
    assert "ValueError" in reporte.loc[0, "detalle"]


# --------------------------------------------------------------------------
# Agregaciones
# --------------------------------------------------------------------------
def test_tabla_agregada_respeta_minimo_de_casos():
    filas = [_fila(mrun=i) for i in range(10)]
    df = transformacion.construir_dataset_analitico(pd.DataFrame(filas))
    assert transformacion.tabla_agregada(df, "area_conocimiento", minimo_casos=30).empty
    resultado = transformacion.tabla_agregada(df, "area_conocimiento", minimo_casos=5)
    assert resultado.loc[0, "titulados"] == 10


def test_configuracion_expone_versiones():
    entorno = config.describir_entorno()
    assert entorno["pandas"] != "no instalado"
    assert entorno["python"].startswith("3.")
