# Sobreduración en la titulación de la educación superior chilena (2020–2025)

Proyecto transversal del curso **Programación para la Ciencia de Datos (202682.1927)** — Fases 1 a 4 (completo).

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
| Rezago severo (más de 4 semestres) | 20,4 % de los titulados |
| Titulación anticipada (antes del plazo) | 4,1 % |
| Semestres-estudiante en exceso acumulados | 3.551.990 |

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
├── F4/
│   └── F4_Reporte_Analitico.ipynb   Reporte integrador F1–F4, visualizaciones y discusión
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
│   ├── Sumativa1_Fase1_2_...pdf/.docx   Informe de las Fases 1 y 2
│   ├── Sumativa2_Fase3_...pdf/.docx     Informe de la Fase 3
│   ├── Sumativa3_Fase4_...pdf/.docx     Informe final integrador (Fase 4)
│   ├── Presentacion_Fase4_...pptx       Presentación de cierre: 10 diapositivas con notas
│   ├── GUION_PRESENTACION_F4.md         Guion cronometrado de la presentación
│   └── evidencias*/         Salidas de pytest, git log y pipeline por fase
├── powerbi/
│   ├── proyecto/            Tablero en formato .pbip: informe y modelo como texto versionable
│   │   ├── Analisis.pbip            Archivo que abre Power BI Desktop
│   │   ├── Analisis.Report/         9 páginas, 88 visuales
│   │   └── Analisis.SemanticModel/  Modelo en estrella, 25 medidas DAX y 2 parámetros
│   ├── tema_sobreduracion.json  Paleta y tipografía del tablero
│   └── GUIA_POWERBI.md      Cómo se construyó y cómo se abre
├── scripts/
│   └── exportar_powerbi.py  Exporta el modelo en estrella y el score de riesgo
├── .mailmap                 Unifica bajo un solo autor las dos identidades de Git usadas
├── CHANGELOG.md             Trazabilidad de mejoras vinculada a commits
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

### 4.1 Qué trae el repositorio clonado y qué no

Un `git clone` entrega el proyecto completo salvo los datos masivos: los CSV
del SIES pesan 955 MB y cada uno supera el límite de 100 MB por archivo de
GitHub, de modo que ni ellos ni los artefactos derivados están versionados.

| Al clonar | Estado | Cómo se obtiene |
|---|---|---|
| Código, notebooks con sus salidas, informes, presentación y tablero | Incluidos | — |
| `data/processed/muestra_titulados_5000.csv` | Incluida | — |
| `data/raw/*.csv` (955 MB) | **No incluidos** | Portal de datos abiertos del Mineduc |
| `data/interim/` y `data/processed/*.parquet` | **No incluidos** | `python -m src.pipeline` |
| CSV del modelo en estrella de `powerbi/` | **No incluidos** | `python -m scripts.exportar_powerbi` |

Sin los CSV originales el proyecto **igual se ejecuta**: los notebooks detectan
que falta el Parquet, usan la muestra versionada de 5.000 registros y lo avisan
en pantalla. Las 73 pruebas de `pytest` no dependen de ningún dato externo, así
que son lo primero que debería funcionar en un equipo recién clonado.

Los notebooks se descargan **ya ejecutados**, con todas sus salidas, figuras y
tablas visibles: se pueden leer de principio a fin sin ejecutar nada. Están
declarados contra el kernel `proyecto-titulados`; para re-ejecutarlos hay que
registrarlo una vez en el entorno virtual:

```powershell
.venv\Scripts\python.exe -m ipykernel install --user --name proyecto-titulados --display-name "Python (proyecto-titulados)"
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

### 5.4 Notebook de la Fase 4

`F4/F4_Reporte_Analitico.ipynb` es el reporte integrador: recorre el flujo F1→F4,
produce las cuatro figuras finales y las tablas de resultados, ejecuta la validación
técnica y cierra con la discusión y las conclusiones.

```powershell
.venv\Scripts\python.exe -m jupyter lab F4/F4_Reporte_Analitico.ipynb
```

Ejecútelo con **Kernel → Restart Kernel and Run All Cells**. Tarda menos de un minuto
con el dataset completo, porque reutiliza los resultados de eficiencia medidos en la
Fase 3 en lugar de repetirlos. Sus salidas quedan en `reports/figures/f4_*.png` y
`reports/tables/f4_*.csv`.

### 5.5 Tablero interactivo en Power BI (valor agregado)

El tablero no estaba pedido en ninguna fase del proyecto. Se incorporó como
**valor agregado** por dos razones: permite explorar los resultados sin
ejecutar código ni leer Python, y cierra el ciclo de comunicación con la
herramienta que efectivamente se usa para presentar análisis en una
organización. Lo que en el informe es una figura fija, aquí es una pregunta que
el lector puede reformular.

Está versionado en formato **`.pbip`**, que guarda el informe y el modelo como
archivos de texto en lugar de un binario: cada cambio queda visible en un
`diff` y el tablero entra en el control de versiones como cualquier otro
código.

**Qué responde cada página**

| Página | Pregunta |
|---|---|
| Panorama | ¿Cuánta sobreduración hay y cómo se reparte? |
| Brechas | ¿Entre qué grupos se abre la diferencia? |
| Instituciones | ¿Qué instituciones concentran el rezago? |
| Cohortes | ¿El rezago empeora o mejora con el tiempo? |
| Comparación | ¿Cómo se sitúa una institución frente al promedio nacional? |
| Costo del rezago | ¿Cuánto cuesta el rezago en aranceles, con el arancel que el usuario fije? |
| Riesgo y decisión | ¿A cuántos estudiantes alcanzaría una intervención según el umbral elegido? |
| Metodología | ¿De dónde sale cada cifra y qué no puede afirmarse con ella? |
| Detalle de institución | Ficha completa de una institución (acceso por *drillthrough*) |

Son **9 páginas y 88 visuales** sobre un modelo en estrella de 1.246.760 filas
de hechos y cuatro dimensiones, con **25 medidas DAX**, cinco relaciones y dos
parámetros *what-if* —arancel anual y umbral de riesgo— que recalculan los
indicadores al moverlos. El score de riesgo que alimenta la página de decisión
proviene del modelo logístico implementado desde primeros principios en la
Fase 3: el tablero consume el núcleo algorítmico del proyecto, no una
estimación aparte.

El tema (`powerbi/tema_sobreduracion.json`) repite la codificación de color de
las figuras del informe —un color para lo destacado, gris para el contexto—,
de modo que documento y tablero se lean con la misma gramática visual.

**Cómo abrirlo**

1. Generar los datos, que no se versionan por tamaño:

   ```powershell
   .venv\Scripts\python.exe -m scripts.exportar_powerbi
   ```

2. Abrir `powerbi/proyecto/Analisis.pbip` con **Power BI Desktop**.
3. **Inicio → Actualizar**.

> **Al abrirlo en otro equipo.** Las cinco consultas guardan la ruta absoluta
> de la carpeta `powerbi/` de este proyecto, porque Power Query no admite rutas
> relativas al archivo. Si el repositorio se clona en otra ubicación, la
> actualización falla con *«No se pudo encontrar el archivo»*. Se corrige una
> sola vez en **Inicio → Transformar datos → Configuración del origen de datos
> → Cambiar origen**, apuntando a la carpeta `powerbi/` del equipo actual, y se
> guarda. El detalle está en [powerbi/GUIA_POWERBI.md](powerbi/GUIA_POWERBI.md).

El archivo `powerbi/Analisis.pbix` que genera Power BI Desktop al guardar como
binario tampoco se versiona: el formato `.pbip` es la fuente, y el `.pbix` se
obtiene de él con **Archivo → Guardar como**.

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

### Decisiones de la Fase 4

| Decisión | Justificación |
|----------|---------------|
| Invertir el escalado antes de informar cualquier cifra | Los coeficientes y las medias en unidades estandarizadas no son interpretables: el lector necesita semestres, no desviaciones típicas. |
| Declarar el orden de las categorías con `pd.Categorical` | En un eje ordinal el orden alfabético sugiere comparaciones que los datos no sostienen. |
| Estratificar la brecha de género por área antes de afirmarla | Una diferencia agregada puede deberse a la composición de los grupos; la brecha se sostiene en las diez áreas, y eso es lo que permite enunciarla. |
| Tres figuras principales, una por objetivo analítico, más una de apoyo | Una figura sin pregunta asociada es decoración; la correspondencia objetivo↔figura se comprueba con una aserción dentro del notebook. |
| Título de cada figura redactado como enunciado | El título dice el hallazgo, no el nombre de las variables graficadas. |
| Color con función: un destacado y un neutro | El color señala dónde mirar; todo lo demás es contexto en gris. |
| Cuatro enunciados por figura: qué muestra, qué se infiere, qué límite tiene, cómo aporta | Obliga a declarar el límite de cada lectura junto al hallazgo, y no relegado al final del informe. |
| Huella SHA-256 de cada archivo exportado | Permite verificar que la figura incluida en el informe es exactamente la que produjo el notebook. |
| Aserción que contrasta las cifras del informe con las recién calculadas | Si una cifra del documento deja de coincidir con el dato, el notebook falla en vez de pasar inadvertido. |
| Publicar el tablero como `.pbip` y no como `.pbix` | El binario no admite revisión por diff; el formato de proyecto deja el informe y el modelo como texto versionable. |

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
| F3 | Núcleo algorítmico, eficiencia y POO; modelación desde primeros principios | Completada (rama `fase-3/nucleo-algoritmico`, integrada en `main`) |
| F4 | Reporte analítico, visualizaciones, discusión y comunicación | Completada |
| — | Tablero interactivo en Power BI | Valor agregado, fuera de lo exigido |

La Fase 4 cierra el proyecto con tres entregables: el notebook integrador
`F4/F4_Reporte_Analitico.ipynb`, que recorre el flujo completo F1→F4 y produce
las figuras y tablas finales; el informe
`informe/Sumativa3_Fase4_Sebastian_Antunez.pdf`, que discute los resultados y
sus límites; y la presentación `informe/Presentacion_Fase4_...pptx` con su
guion cronometrado. A ellos se suma, por iniciativa propia y fuera de lo
exigido, el **tablero de Power BI** descrito en el apartado 5.5: convierte los
hallazgos fijos del informe en un instrumento que el lector puede interrogar,
con dos parámetros que permiten evaluar escenarios de costo y de cobertura de
una intervención.

La trazabilidad de las mejoras aplicadas entre fases, con su commit e impacto técnico,
está en [CHANGELOG.md](CHANGELOG.md).

## 9. Informe técnico

| Entrega | Archivo | Contenido |
|---|---|---|
| Fases 1 y 2 | `informe/Sumativa1_Fase1_2_Sebastian_Antunez.pdf` | Definición, pipeline y validación |
| Fase 3 (sumativa) | `informe/Sumativa2_Fase3_Sebastian_Antunez.pdf` | Núcleo algorítmico, eficiencia y POO |
| Fase 4 | `informe/Sumativa3_Fase4_Sebastian_Antunez.pdf` | Reporte final integrador |

Todas las cifras, tablas y figuras de los informes provienen de los notebooks de este
repositorio y se regeneran ejecutándolos.

## 10. Créditos y licencia

Datos publicados por el **Servicio de Información de Educación Superior (SIES)**
del Ministerio de Educación de Chile bajo licencia de datos abiertos. El código
de este repositorio se distribuye con fines académicos.
