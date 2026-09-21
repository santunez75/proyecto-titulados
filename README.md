# Sobreduración en la titulación de la educación superior chilena (2020–2025)

Proyecto transversal del curso **Programación para la Ciencia de Datos (202682.1927)** — Fases 1, 2 y 3.

**Autor:** Sebastian Antunez Noguera
**Docente:** Omar Salinas · **Programa:** Magíster en Ciencia de Datos e Inteligencia Artificial · Universidad Andrés Bello

---

## 1. Qué resuelve este proyecto

El sistema de educación superior chileno declara para cada carrera una
**duración teórica** (el plan comprometido con el estudiante), pero no publica
cuánto tardan efectivamente los estudiantes en titularse. La diferencia entre
ambas magnitudes —la **sobreduración**— determina el gasto de las familias, el
uso de becas y créditos estatales y la edad de entrada al mercado laboral.

Este repositorio construye esa variable a partir de los registros
administrativos de titulados del **Servicio de Información de Educación
Superior (SIES)** y caracteriza el rezago por área de conocimiento, tipo de
institución, sexo, modalidad de estudio y región.

**Pregunta central:** ¿cuánto excede la duración real de una carrera de pregrado
a su duración teórica, y qué factores se asocian a esa brecha?

### Resultados principales

| Indicador | Valor |
|-----------|-------|
| Registros procesados | 1.710.167 (2020–2025) |
| Conjunto analítico final | 1.246.760 titulados de pregrado |
| Titulación en el plazo teórico | **19,0 %** |
| Sobreduración media | **2,76 semestres** (índice 1,43) |
| Mayor rezago por área | Derecho (5,77 semestres) |
| Menor rezago por área | Educación (1,93 semestres) |
| Brecha de género | Las mujeres se titulan 0,94 semestres antes |
| Crecimiento de la modalidad no presencial | 4,7 % (2020) → 11,2 % (2025) |

## 2. Estructura del repositorio

```
proyecto-titulados/
├── F1/
│   └── F1_Definición.ipynb          Definición del problema y entorno reproducible
├── F2/
│   ├── F2_1_Obtencion_Exploracion.ipynb    Consolidación y exploración (EDA)
│   ├── F2_2_Limpieza_Transformacion.ipynb  Depuración y variables derivadas
│   └── F2_3_Validacion_Analisis.ipynb      Validación técnica y resultados
├── F3/
│   └── F3_Nucleo_Algoritmico.ipynb  Algoritmos, complejidad, POO y modelación (Fase 3)
├── src/
│   ├── config.py            Rutas, esquema de datos y constantes
│   ├── ingesta.py           Lectura por bloques y consolidación en Parquet
│   ├── limpieza.py          Sentinelas, faltantes, duplicados y bitácora
│   ├── transformacion.py    Duración real, sobreduración y agregaciones
│   ├── validacion.py        Motor de reglas de validación
│   ├── viz.py               Funciones de visualización con estilo unificado
│   ├── pipeline.py          Orquestador ejecutable de todo el flujo
│   └── nucleo/              Núcleo algorítmico de la Fase 3
│       ├── algoritmos.py    Agregación O(n), merge sort, quickselect, búsqueda binaria (recursivos)
│       ├── benchmark.py     timeit + tracemalloc, curvas de escalamiento, exponente empírico
│       ├── dominio.py       Clases Titulado y Cohorte (encapsulamiento, protocolo de secuencia)
│       ├── metricas.py      Metrica abstracta y subclases (patrón Strategy)
│       ├── jerarquia.py     NodoJerarquia recursivo con memorización (patrón Composite)
│       ├── preparacion.py   Transformador → escaladores y one-hot (herencia); partición
│       ├── modelos.py       Regresión lineal y logística por gradiente (Template Method)
│       ├── fachada.py       NucleoAnalitico (patrón Facade)
│       └── validacion_f3.py Reglas de coherencia del núcleo (reutiliza src/validacion)
├── tests/
│   ├── test_pipeline.py     22 pruebas del pipeline de F2
│   └── test_nucleo.py       51 pruebas del núcleo de F3 (normales, límite, excepciones)
├── data/
│   ├── raw/                 CSV originales del SIES (no versionados)
│   ├── interim/             Consolidado en Parquet (no versionado)
│   └── processed/           Conjunto analítico y muestra de 5.000 filas
├── reports/
│   ├── figures/             Figuras generadas por los notebooks
│   └── tables/              Tablas de resultados en CSV
├── docs/
│   ├── ER titulados ... .pdf   Esquema de registro oficial del SIES
│   └── mapa_conceptual/     Mapa conceptual técnico de la Fase 1 (SVG, PNG, PDF + generador)
├── informe/
│   ├── Sumativa1_Fase1_2_Sebastian_Antunez.pdf   Informe técnico entregado (Fases 1 y 2)
│   ├── Sumativa1_Fase1_2_Sebastian_Antunez.docx  Fuente editable del informe
│   └── evidencias/          Salidas de pytest, git log y pipeline
├── requirements.txt         Dependencias con versiones fijadas
└── README.md
```

## 3. Datos de origen

| Atributo | Detalle |
|----------|---------|
| Fuente | Servicio de Información de Educación Superior (SIES), Ministerio de Educación de Chile |
| Conjunto | *Titulados de Educación Superior por estudiante — Bases WEB con MRUN* |
| Años | 2020, 2021, 2022, 2023, 2024 y 2025 (un CSV por año) |
| Registros | 1.710.167 |
| Columnas | 40 originales; 30 utilizadas |
| Formato | CSV delimitado por `;`, codificación UTF-8 |
| Peso total | ≈ 955 MB |
| Portal | https://datosabiertos.mineduc.cl/ |
| Documentación | `docs/ER titulados Ed.Superior 2007 - 2025, WEB.pdf` |

> **Los CSV no están versionados en GitHub**: cada archivo supera el límite de
> 100 MB de la plataforma. Descárguelos del portal de datos abiertos y
> colóquelos en `data/raw/`, o defina la variable de entorno
> `TITULADOS_RAW_DIR` apuntando a la carpeta que los contiene.
>
> El repositorio sí incluye `data/processed/muestra_titulados_5000.csv`, una
> muestra aleatoria reproducible (`random_state=42`) del conjunto analítico que
> permite inspeccionar el resultado sin ejecutar el pipeline completo.

## 4. Instalación

Requiere **Python 3.11 o superior** (entorno de referencia: 3.14.7).

```powershell
git clone https://github.com/santunez75/proyecto-titulados.git
cd proyecto-titulados
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

En Linux o macOS, reemplace la activación por `source .venv/bin/activate`.

Verificación del entorno:

```powershell
python -c "from src import config; print(config.describir_entorno())"
python -m pytest tests/ -v
```

## 5. Ejecución

### 5.1 Pipeline completo desde la línea de comandos

```powershell
python -m src.pipeline
```

Ejecuta ingesta, limpieza, transformación y validación de extremo a extremo, e
imprime la bitácora y el reporte de validación. Con `--forzar-ingesta` vuelve a
leer los CSV originales aunque exista el Parquet consolidado.

### 5.2 Notebooks

Ejecútelos **en orden**: cada uno consume el artefacto que produce el anterior.

| Orden | Notebook | Qué hace | Requiere | Produce |
|-------|----------|----------|----------|---------|
| 1 | `F1/F1_Definición.ipynb` | Define el problema, verifica entorno, dependencias, esquema y código base. | CSV en `data/raw/` | Verificaciones en pantalla |
| 2 | `F2/F2_1_Obtencion_Exploracion.ipynb` | Consolida los seis años, verifica integridad contra el SIES y diagnostica calidad. | CSV en `data/raw/` | `data/interim/*.parquet` |
| 3 | `F2/F2_2_Limpieza_Transformacion.ipynb` | Depura y deriva las variables analíticas. | Parquet consolidado | `data/processed/*.parquet`, bitácora |
| 4 | `F2/F2_3_Validacion_Analisis.ipynb` | Valida, ejecuta las pruebas y produce los resultados. | Conjunto analítico | Figuras y tablas en `reports/` |

```powershell
jupyter lab
```

Tiempo aproximado de la primera ejecución completa: **4 a 6 minutos**
(la consolidación de los 955 MB toma cerca de 25 segundos).

### 5.3 Notebook de la Fase 3

`F3/F3_Nucleo_Algoritmico.ipynb` consume el dataset analítico que produce la
Fase 2 (`data/processed/titulados_pregrado_analitico.parquet`). Si ese archivo
no existe —por ejemplo, en un equipo sin los CSV originales— el notebook usa
automáticamente la muestra versionada de 5.000 registros y lo avisa.

```powershell
.venv\Scripts\python.exe -m jupyter lab F3/F3_Nucleo_Algoritmico.ipynb
```

Ejecútelo con **Kernel → Restart Kernel and Run All Cells**. Toma entre 5 y
8 minutos con el dataset completo: la mayor parte son las mediciones de
eficiencia, que repiten cada algoritmo varias veces sobre hasta 640.000
elementos. Sus salidas quedan en `reports/tables/f3_*.csv` y
`reports/figures/f3_*.png`.

El núcleo también puede usarse desde código, sin notebook:

```python
from src.nucleo.fachada import NucleoAnalitico

nucleo = NucleoAnalitico(limite_cohorte=300_000)
print(nucleo.resumen_por("tipo_institucion"))      # métricas polimórficas por grupo
print(nucleo.concentracion_rezago())               # descenso recursivo por el árbol
resultado = nucleo.ajustar_modelos()               # regresión lineal y logística desde cero
print(resultado.coeficientes())
```

## 6. Decisiones técnicas documentadas

| Decisión | Justificación |
|----------|---------------|
| Lectura por bloques de 200.000 filas | La memoria ocupada no depende del tamaño del archivo. |
| Lectura como texto y conversión controlada | Un valor inválido se registra como coerción en lugar de abortar la carga. |
| Persistencia en Parquet | Reduce 955 MB a 37,5 MB, conserva los tipos y evita reparsear texto. |
| 30 de 40 columnas | Las descartadas son redundantes (CINE-F 1997 frente a 2013) o irrelevantes; el motivo de cada una está en `config.COLUMNAS_DESCARTADAS`. |
| Códigos centinela a `NA` | 9995/9998/9999/1900 y 19000101 son valores válidos como números: procesarlos produciría duraciones imposibles. |
| Solo pregrado | Posgrado y postítulo tienen planes no comparables en duración. |
| Descartar y no imputar el año de ingreso | Imputarlo equivaldría a inventar la variable que el proyecto mide. |
| `dur_total_carr` como referencia teórica | La identidad `estudio + proceso = total` no se cumple en el 33,5 % de los registros. |
| Filas sin `mrun` excluidas del cotejo de duplicados | Pandas considera iguales dos nulos; incluirlas colapsaría estudiantes distintos. |
| Umbrales de atípicos en `config.py` | Parámetros explícitos y auditables, no constantes escondidas en el código. |
| Normalizar el catálogo de categorías y no fila por fila | Reduce el trabajo de 1,7 millones de cadenas por columna a unos pocos miles de valores únicos. |

### Decisiones de la Fase 3

| Decisión | Justificación |
|----------|---------------|
| Implementar los algoritmos desde cero y **medirlos contra pandas/NumPy** | Es la única forma de contrastar la cota teórica con el comportamiento real y de justificar cuándo usar cada cosa. |
| `timeit.repeat` con el **mínimo** de las repeticiones | El ruido del sistema solo suma tiempo; el mínimo estima el costo intrínseco. |
| Curvas de escalamiento y exponente en escala log-log | Un solo tamaño no distingue O(n) de O(n log n); la pendiente sí. |
| `Titulado` con `__slots__` y setters que validan | Cientos de miles de objetos con la mitad de memoria y sin estados inválidos. |
| `Metrica` como Strategy en vez de `if/elif` | Agregar un indicador no obliga a modificar `Cohorte` ni la jerarquía. |
| `NodoJerarquia` como Composite con totales memorizados | Una sola interfaz para hoja y nodo interno; la cache evita recorrer el árbol en cada consulta. |
| Bucle de gradiente en la clase base (Template Method) | Se escribe una vez; lineal y logística sólo aportan enlace y pérdida. |
| Solución cerrada como referencia del descenso de gradiente | Verifica que la implementación converge al óptimo exacto. |
| Escalar con parámetros **solo de entrenamiento** | Evita la fuga de información hacia el conjunto de prueba. |
| Detección explícita de divergencia por tasa excesiva | Una excepción clara en vez de pesos infinitos o NaN silenciosos. |

## 7. Validación y pruebas

- **Motor de reglas** (`src/validacion.py`): 11 reglas sobre el conjunto
  completo — integridad, dominios, rangos, coherencia aritmética, cobertura
  temporal y duplicados. Resultado: 10 aprobadas, 1 advertencia documentada.
- **Pruebas del núcleo** (`tests/test_nucleo.py`): 51 pruebas que contrastan cada
  algoritmo con una referencia independiente (`sorted`, `statistics`, pandas,
  solución cerrada) y cubren bordes (secuencias vacías, columnas constantes,
  categorías no vistas) y excepciones (tasa divergente, modelo sin ajustar).
- **Pruebas automatizadas** (`tests/test_pipeline.py`): 22 pruebas que cubren
  casos normales, casos límite y excepciones. Se ejecutan en menos de 2 segundos
  y no dependen de los CSV originales.
- **Comprobación de determinismo**: el notebook `F2_3` re-ejecuta el pipeline
  completo y compara los resultados con el conjunto guardado.

```powershell
python -m pytest tests/ -v
```

## 8. Estado del proyecto

| Fase | Contenido | Estado |
|------|-----------|--------|
| F1 | Definición del problema y entorno reproducible | Completada |
| F2 | Obtención, exploración, limpieza, transformación y validación | Completada |
| F3 | Núcleo algorítmico, eficiencia y POO; modelación desde primeros principios | En entrega (rama `fase-3/nucleo-algoritmico`) |
| F4 | Reporte analítico final | Proyectada |

## 9. Informe técnico

El informe de las Fases 1 y 2 está en `informe/Sumativa1_Fase1_2_Sebastian_Antunez.pdf`
(44 páginas). Todas sus cifras, tablas y figuras provienen de los notebooks de este
repositorio y se regeneran ejecutando el pipeline.

## 10. Créditos y licencia

Datos publicados por el **Servicio de Información de Educación Superior (SIES)**
del Ministerio de Educación de Chile bajo licencia de datos abiertos. El código
de este repositorio se distribuye con fines académicos.
