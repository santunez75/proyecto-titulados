"""Pruebas del nucleo algoritmico (Fase 3).

Organizadas por modulo y, dentro de cada uno, por escenario: casos normales
(resultado esperado contra una referencia independiente), casos limite
(secuencias vacias o de un elemento, bordes de rango, columnas constantes) y
excepciones (entradas invalidas que deben fallar con un error explicito).
No dependen de los CSV del SIES: construyen sus datos en memoria.
"""

from __future__ import annotations

import statistics
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.nucleo import algoritmos as alg  # noqa: E402
from src.nucleo import benchmark as bm  # noqa: E402
from src.nucleo import metricas as me  # noqa: E402
from src.nucleo.dominio import Cohorte, Titulado  # noqa: E402
from src.nucleo.jerarquia import NodoJerarquia, construir_jerarquia  # noqa: E402
from src.nucleo.modelos import (  # noqa: E402
    RegresionLinealCerrada, RegresionLinealGD, RegresionLogisticaGD, metricas_clasificacion,
)
from src.nucleo.preparacion import (  # noqa: E402
    CodificadorOneHot, EscaladorEstandar, EscaladorMinMax, PreparadorModelacion,
    dividir_entrenamiento_prueba,
)


# ===========================================================================
# algoritmos
# ===========================================================================
@pytest.fixture
def enteros():
    return np.random.default_rng(7).integers(-5, 40, 2_000).tolist()


class TestAgrupacion:
    def test_media_por_grupo_coincide_con_pandas(self, enteros):
        claves = [x % 4 for x in enteros]
        esperado = pd.Series(enteros).groupby(pd.Series(claves)).mean().to_dict()
        assert alg.agrupar_media(claves, enteros) == pytest.approx(esperado)
        assert alg.agrupar_media_ingenua(claves, enteros) == pytest.approx(esperado)

    def test_un_solo_grupo(self):
        assert alg.agrupar_media(["a", "a"], [2.0, 4.0]) == {"a": 3.0}

    def test_largos_distintos_lanzan_error(self):
        with pytest.raises(ValueError):
            alg.agrupar_media(["a"], [1.0, 2.0])


class TestOrdenamiento:
    def test_merge_sort_coincide_con_sorted(self, enteros):
        assert alg.ordenar_merge(enteros) == sorted(enteros)
        assert alg.ordenar_insercion(enteros[:300]) == sorted(enteros[:300])

    def test_no_muta_la_entrada(self, enteros):
        copia = list(enteros)
        alg.ordenar_merge(enteros)
        assert enteros == copia

    def test_vacia_y_un_elemento(self):
        assert alg.ordenar_merge([]) == []
        assert alg.ordenar_merge([42]) == [42]

    def test_es_estable(self):
        pares = [(2, "a"), (1, "b"), (2, "c"), (1, "d")]
        ordenado = alg.ordenar_merge([(k, v) for k, v in pares])
        assert ordenado == [(1, "b"), (1, "d"), (2, "a"), (2, "c")]


class TestSeleccion:
    def test_mediana_coincide_con_statistics(self, enteros):
        assert alg.mediana(enteros, 0) == statistics.median(enteros)
        assert alg.mediana_ordenando(enteros) == statistics.median(enteros)

    def test_quickselect_recupera_cada_posicion(self):
        datos = [9, 1, 8, 2, 7, 2]
        ordenados = sorted(datos)
        for k in range(len(datos)):
            assert alg.quickselect(datos, k, semilla=1) == ordenados[k]

    def test_mediana_par_e_impar(self):
        assert alg.mediana([3, 1, 2]) == 2
        assert alg.mediana([4, 1, 3, 2]) == 2.5

    def test_k_fuera_de_rango_y_vacia(self):
        with pytest.raises(IndexError):
            alg.quickselect([1, 2, 3], 3)
        with pytest.raises(ValueError):
            alg.quickselect([], 0)
        with pytest.raises(ValueError):
            alg.mediana([])


class TestBusqueda:
    def test_binaria_encuentra_y_no_encuentra(self):
        ordenados = [1, 3, 5, 7, 9]
        for i, v in enumerate(ordenados):
            assert alg.busqueda_binaria(ordenados, v) == i
        assert alg.busqueda_binaria(ordenados, 4) == -1
        assert alg.busqueda_lineal(ordenados, 7) == 3

    def test_binaria_en_vacia(self):
        assert alg.busqueda_binaria([], 1) == -1

    def test_conteos_por_umbral_coinciden_con_recuento_directo(self, enteros):
        ordenados = sorted(enteros)
        for umbral in (-10, 0, 2, 4, 39, 100):
            assert alg.contar_sobre_umbral(ordenados, umbral) == sum(1 for x in enteros if x > umbral)
        assert alg.contar_en_rango(ordenados, 0, 2) == sum(1 for x in enteros if 0 < x <= 2)

    def test_cotas_en_bordes(self):
        assert alg.primer_indice_mayor_igual([1, 1, 1], 1) == 0
        assert alg.primer_indice_mayor([1, 1, 1], 1) == 3
        assert alg.primer_indice_mayor_igual([], 5) == 0


# ===========================================================================
# benchmark
# ===========================================================================
class TestBenchmark:
    def test_medicion_basica(self):
        m = bm.medir("suma", sum, list(range(1000)), repeticiones=2)
        assert m.n == 1000 and m.segundos > 0 and m.memoria_pico_kb is not None

    def test_exponente_de_funcion_lineal_cercano_a_uno(self):
        curva = bm.curva_escalamiento(
            "lineal", lambda xs: sum(xs), lambda n: (list(range(n)),), [20_000, 80_000, 320_000], repeticiones=2
        )
        assert 0.7 < curva.exponente < 1.3

    def test_exponente_cuadratico(self):
        def cuadratica(xs):
            return sum(1 for a in xs for b in xs if a < b)
        curva = bm.curva_escalamiento("cuadratica", cuadratica, lambda n: (list(range(n)),), [100, 200, 400], repeticiones=2)
        assert 1.7 < curva.exponente < 2.3

    def test_estimar_orden_exige_dos_tamanos(self):
        with pytest.raises(ValueError):
            bm.estimar_orden([bm.Medicion("x", 10, 0.1)])
        with pytest.raises(ValueError):
            bm.estimar_orden([bm.Medicion("x", 10, 0.1), bm.Medicion("x", 10, 0.2)])

    def test_comparar_ordena_por_tiempo(self):
        tabla = bm.comparar({"sorted": sorted, "merge": alg.ordenar_merge}, list(range(2000, 0, -1)), repeticiones=2)
        assert list(tabla.columns[:2]) == ["implementacion", "n"]
        assert tabla["segundos"].is_monotonic_increasing
        assert tabla.loc[0, "razon_vs_mejor"] == 1.0


# ===========================================================================
# dominio
# ===========================================================================
def _titulado(**cambios) -> Titulado:
    base = dict(
        mrun=1, genero="Mujer", area="Salud", tipo_institucion="Universidades",
        institucion="U1", carrera="Enfermeria", modalidad="Presencial", region="Maule",
        anio_titulo=2024, duracion_teorica=10, duracion_real=12, edad_titulacion=26,
    )
    base.update(cambios)
    return Titulado(**base)


class TestTitulado:
    def test_propiedades_derivadas(self):
        t = _titulado()
        assert t.sobreduracion == 2 and t.indice_duracion == 1.2
        assert not t.es_oportuna and t.categoria_rezago == "Rezago leve"
        assert _titulado(duracion_real=10).es_oportuna
        assert _titulado(duracion_real=15).categoria_rezago == "Rezago severo"

    def test_encapsulamiento_identidad_solo_lectura(self):
        t = _titulado()
        with pytest.raises(AttributeError):
            t.mrun = 99  # type: ignore[misc]
        with pytest.raises(AttributeError):
            t.sobreduracion = 0  # type: ignore[misc]

    def test_setters_validan(self):
        t = _titulado()
        with pytest.raises(ValueError):
            t.duracion_teorica = 0
        with pytest.raises(ValueError):
            t.duracion_real = 0
        with pytest.raises(ValueError):
            _titulado(edad_titulacion=10)
        t.duracion_real = 9  # valido: la sobreduracion se recalcula sola
        assert t.sobreduracion == -1 and t.es_oportuna

    def test_orden_natural_e_igualdad(self):
        a, b, c = _titulado(mrun=1, duracion_real=15), _titulado(mrun=2, duracion_real=11), _titulado(mrun=1)
        assert sorted([a, b]) == [b, a]
        assert alg.ordenar_merge([a, b]) == [b, a]
        assert a == c and a != b and len({a, c}) == 1

    def test_desde_fila_con_dict_y_series(self):
        fila = {
            "mrun": 5, "genero": "Hombre", "area_conocimiento": "Derecho", "tipo_inst_1": "Universidades",
            "nomb_inst": "U2", "nomb_carrera": "Derecho", "modalidad": "Presencial", "region_sede": "RM",
            "anio_titulo": 2023, "dur_total_carr": 10, "duracion_real_sem": 16, "edad_titulacion": 27,
        }
        assert Titulado.desde_fila(fila).sobreduracion == 6
        assert Titulado.desde_fila(pd.Series(fila)).carrera == "Derecho"


class TestCohorte:
    @pytest.fixture
    def cohorte(self):
        return Cohorte([
            _titulado(mrun=1, duracion_real=10),
            _titulado(mrun=2, duracion_real=12, genero="Hombre"),
            _titulado(mrun=3, duracion_real=16, genero="Hombre", area="Derecho"),
        ], nombre="prueba")

    def test_protocolo_de_secuencia(self, cohorte):
        assert len(cohorte) == 3 and cohorte[0].mrun == 1
        assert _titulado(mrun=2, duracion_real=12) in cohorte
        assert [t.mrun for t in cohorte] == [1, 2, 3]
        assert "n=3" in repr(cohorte)

    def test_filtrar_y_agrupar_no_mutan(self, cohorte):
        hombres = cohorte.filtrar(lambda t: t.genero == "Hombre")
        assert len(hombres) == 2 and len(cohorte) == 3
        grupos = cohorte.agrupar_por("area")
        assert set(grupos) == {"Salud", "Derecho"} and len(grupos["Salud"]) == 2

    def test_strategy_con_metricas(self, cohorte):
        assert cohorte.calcular(me.MediaSobreduracion()) == pytest.approx((0 + 2 + 6) / 3)
        assert cohorte.calcular(me.MedianaSobreduracion()) == 2
        assert cohorte.calcular(me.TasaOportuna()) == pytest.approx(100 / 3)
        assert cohorte.calcular(me.TasaRezagoSevero()) == pytest.approx(100 / 3)
        resumen = cohorte.resumen(me.metricas_estandar())
        assert set(resumen) == {m.nombre for m in me.metricas_estandar()}

    def test_ordenados_con_merge_sort(self, cohorte):
        assert [t.mrun for t in cohorte.ordenados_por_sobreduracion(descendente=True)] == [3, 2, 1]

    def test_agregar_rechaza_tipos_ajenos(self, cohorte):
        with pytest.raises(TypeError):
            cohorte.agregar("no soy un titulado")  # type: ignore[arg-type]

    def test_metrica_en_cohorte_vacia_lanza_error(self):
        with pytest.raises(ValueError):
            Cohorte().calcular(me.MediaSobreduracion())

    def test_desde_dataframe_exige_columnas(self):
        with pytest.raises(ValueError):
            Cohorte.desde_dataframe(pd.DataFrame({"mrun": [1]}))

    def test_percentil_valida_rango(self):
        with pytest.raises(ValueError):
            me.PercentilSobreduracion(120)


# ===========================================================================
# jerarquia
# ===========================================================================
class TestJerarquia:
    @pytest.fixture
    def arbol(self):
        cohorte = Cohorte([
            _titulado(mrun=1, tipo_institucion="U", institucion="A", carrera="x", duracion_real=10),
            _titulado(mrun=2, tipo_institucion="U", institucion="A", carrera="y", duracion_real=14),
            _titulado(mrun=3, tipo_institucion="U", institucion="B", carrera="x", duracion_real=18),
            _titulado(mrun=4, tipo_institucion="IP", institucion="C", carrera="z", duracion_real=11),
        ])
        return construir_jerarquia(cohorte)

    def test_totales_recursivos_y_estructura(self, arbol):
        assert arbol.total() == 4 and arbol.total_sin_cache() == 4
        assert arbol.profundidad() == 3 and len(arbol.hojas()) == 4
        assert arbol["U"].total() == 3 and arbol["U"]["B"].total() == 1
        assert arbol["U"]["A"]["y"].ruta() == "Sistema > U > A > y"
        assert sum(1 for _ in arbol.titulados()) == 4

    def test_cache_se_invalida_al_insertar(self, arbol):
        assert arbol.total() == 4
        arbol.insertar(_titulado(mrun=9, duracion_real=10), ["IP", "C", "z"], ["tipo_institucion", "institucion", "carrera"])
        assert arbol.total() == 5 and arbol["IP"].total() == 2

    def test_metrica_composite_y_descenso(self, arbol):
        media = me.MediaSobreduracion()
        assert arbol.calcular(media) == pytest.approx((0 + 4 + 8 + 1) / 4)
        camino = arbol.descender_por_maximo(media, minimo=1)
        assert [n.nombre for n in camino] == ["Sistema", "U", "B", "x"]

    def test_buscar_y_dataframe(self, arbol):
        assert arbol.buscar("B").nivel == "institucion"
        assert arbol.buscar("no existe") is None
        tabla = arbol.a_dataframe([me.MediaSobreduracion()], nivel_maximo=1)
        assert set(tabla["nivel"]) == {"sistema", "tipo_institucion"}

    def test_nodo_vacio(self):
        raiz = NodoJerarquia("raiz", "sistema")
        assert raiz.total() == 0 and raiz.es_hoja and raiz.profundidad() == 0
        assert raiz.descender_por_maximo(me.MediaSobreduracion()) == [raiz]


# ===========================================================================
# preparacion
# ===========================================================================
class TestPreparacion:
    def test_escalador_estandar(self):
        X = np.array([[1.0, 10.0], [2.0, 10.0], [3.0, 10.0]])
        Z = EscaladorEstandar().ajustar_transformar(X)
        assert np.allclose(Z.mean(axis=0), 0) and np.allclose(Z[:, 0].std(), 1)
        assert np.allclose(Z[:, 1], 0)  # columna constante: no divide por cero

    def test_estandar_invertir(self):
        X = np.random.default_rng(0).normal(5, 2, (50, 3))
        esc = EscaladorEstandar().ajustar(X)
        assert np.allclose(esc.invertir(esc.transformar(X)), X)

    def test_minmax_en_cero_uno(self):
        Z = EscaladorMinMax().ajustar_transformar(np.array([[0.0, 5.0], [10.0, 5.0], [5.0, 5.0]]))
        assert Z.min() == 0 and Z.max() == 1

    def test_transformar_sin_ajustar_y_dimensiones(self):
        esc = EscaladorEstandar()
        with pytest.raises(RuntimeError):
            esc.transformar(np.ones((2, 2)))
        esc.ajustar(np.ones((3, 2)))
        with pytest.raises(ValueError):
            esc.transformar(np.ones((3, 3)))
        with pytest.raises(ValueError):
            esc.transformar(np.array([[1.0, np.nan]]))

    def test_onehot_omite_primera_y_categoria_desconocida(self):
        df = pd.DataFrame({"g": ["a", "b", "c", "a"]})
        cod = CodificadorOneHot().ajustar(df, ["g"])
        assert cod.nombres_columnas == ["g=b", "g=c"]
        M = cod.transformar(pd.DataFrame({"g": ["b", "zzz"]}))
        assert M.tolist() == [[1.0, 0.0], [0.0, 0.0]]

    def test_particion_reproducible_y_disjunta(self):
        a_ent, a_pru = dividir_entrenamiento_prueba(100, 0.2, 1)
        b_ent, b_pru = dividir_entrenamiento_prueba(100, 0.2, 1)
        assert np.array_equal(a_ent, b_ent) and len(a_pru) == 20
        assert not set(a_ent) & set(a_pru)
        with pytest.raises(ValueError):
            dividir_entrenamiento_prueba(100, 1.5)

    def test_preparador_compone_y_exige_ajuste(self):
        df = pd.DataFrame({"x": [1.0, 2.0, 3.0], "c": ["a", "b", "a"]})
        prep = PreparadorModelacion(["x"], ["c"])
        with pytest.raises(RuntimeError):
            prep.transformar(df)
        M = prep.ajustar_transformar(df)
        assert M.shape == (3, 2) and prep.nombres_columnas == ["x", "c=b"]


# ===========================================================================
# modelos
# ===========================================================================
class TestModelos:
    @pytest.fixture
    def lineal(self):
        rng = np.random.default_rng(3)
        X = rng.normal(size=(400, 3))
        y = X @ np.array([1.5, -2.0, 0.5]) + 0.7 + rng.normal(scale=0.05, size=400)
        return X, y

    def test_descenso_converge_a_solucion_cerrada(self, lineal):
        X, y = lineal
        gd = RegresionLinealGD(0.3, 800).ajustar(X, y)
        cerrada = RegresionLinealCerrada().ajustar(X, y)
        assert np.allclose(gd.pesos, cerrada.pesos, atol=1e-2)
        assert abs(gd.sesgo - cerrada.sesgo) < 1e-2
        assert gd.evaluar(X, y)["r2"] > 0.99

    def test_perdida_decrece(self, lineal):
        X, y = lineal
        h = RegresionLinealGD(0.3, 200).ajustar(X, y).historial_perdida
        assert h[0] > h[-1] and all(b <= a + 1e-9 for a, b in zip(h, h[1:]))

    def test_logistica_separa_datos_separables(self):
        rng = np.random.default_rng(5)
        X = rng.normal(size=(600, 2))
        y = (X[:, 0] + X[:, 1] > 0).astype(float)
        m = RegresionLogisticaGD(0.5, 800).ajustar(X, y)
        assert m.evaluar(X, y)["exactitud"] > 0.95
        assert 0 <= m.predecir_probabilidad(X).min() and m.predecir_probabilidad(X).max() <= 1

    def test_pesos_devueltos_son_copia(self, lineal):
        X, y = lineal
        m = RegresionLinealGD(0.3, 50).ajustar(X, y)
        m.pesos[:] = 0
        assert not np.allclose(m.pesos, 0)

    def test_errores_controlados(self, lineal):
        X, y = lineal
        with pytest.raises(RuntimeError):
            RegresionLinealGD().predecir(X)
        with pytest.raises(ValueError):
            RegresionLinealGD().ajustar(X, y[:10])
        with pytest.raises(ValueError):
            RegresionLinealGD(tasa_aprendizaje=0)
        with pytest.raises(RuntimeError, match="divergio"):
            RegresionLinealGD(tasa_aprendizaje=5.0, iteraciones=100).ajustar(X, y)
        m = RegresionLinealGD(0.3, 20).ajustar(X, y)
        with pytest.raises(ValueError):
            m.predecir(X[:, :2])

    def test_metricas_clasificacion_extremos(self):
        y = np.array([0, 0, 1, 1])
        perfecto = metricas_clasificacion(y, y)
        assert perfecto["exactitud"] == 1 and perfecto["f1"] == 1
        nulo = metricas_clasificacion(y, np.zeros(4))
        assert nulo["sensibilidad"] == 0 and nulo["precision"] == 0 and nulo["f1"] == 0
