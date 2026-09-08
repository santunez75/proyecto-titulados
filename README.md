# Sobreduración en la titulación de la educación superior chilena (2020–2025)

Proyecto transversal del curso **«Nombre del curso» («Código»)** — Fases 1 y 2.

**Equipo:** «Integrante 1», «Integrante 2», «Integrante 3» · **Grupo:** «N»
**Docente:** «Nombre del docente» · **Institución:** Universidad Andrés Bello

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
├── src/
│   ├── config.py            Rutas, esquema de datos y constantes
│   ├── ingesta.py           Lectura por bloques y consolidación en Parquet
│   ├── limpieza.py          Sentinelas, faltantes, duplicados y bitácora
│   ├── transformacion.py    Duración real, sobreduración y agregaciones
│   ├── validacion.py        Motor de reglas de validación
│   ├── viz.py               Funciones de visualización con estilo unificado
│   └── pipeline.py          Orquestador ejecutable de todo el flujo
├── tests/
│   └── test_pipeline.py     22 pruebas: casos normales, límite y excepciones
├── data/
│   ├── raw/                 CSV originales del SIES (no versionados)
│   ├── interim/             Consolidado en Parquet (no versionado)
│   └── processed/           Conjunto analítico y muestra de 5.000 filas
├── reports/
│   ├── figures/             Figuras generadas por los notebooks
│   └── tables/              Tablas de resultados en CSV
├── docs/                    Esquema de registro oficial del SIES
├── informe/
│   ├── f1_s01_evaluacion_entregable_grupox.pdf   Informe técnico (entregable)
│   ├── f1_s01_evaluacion_entregable_grupox.docx  Fuente editable del informe
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
git clone «URL del repositorio»
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

## 7. Validación y pruebas

- **Motor de reglas** (`src/validacion.py`): 11 reglas sobre el conjunto
  completo — integridad, dominios, rangos, coherencia aritmética, cobertura
  temporal y duplicados. Resultado: 10 aprobadas, 1 advertencia documentada.
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
| F3 | Modelación de la sobreduración | Proyectada |
| F4 | Reporte analítico final | Proyectada |

## 9. Informe técnico

El informe de las Fases 1 y 2 está en `informe/f1_s01_evaluacion_entregable_grupox.pdf`
(44 páginas). Todas sus cifras, tablas y figuras provienen de los notebooks de este
repositorio y se regeneran ejecutando el pipeline.

## 10. Créditos y licencia

Datos publicados por el **Servicio de Información de Educación Superior (SIES)**
del Ministerio de Educación de Chile bajo licencia de datos abiertos. El código
de este repositorio se distribuye con fines académicos.
