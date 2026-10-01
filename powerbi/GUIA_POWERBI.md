# Primer tablero en Power BI con los datos del proyecto

Guía para construir, desde cero, un tablero sobre la sobreduración en la
titulación. No supone experiencia previa con Power BI.

Los archivos de esta carpeta los genera `scripts/exportar_powerbi.py`:

```powershell
.venv\Scripts\python.exe -m scripts.exportar_powerbi
```

---

## 0. Instalar Power BI Desktop

Es gratis y solo existe para Windows. Dos formas:

- **Microsoft Store** — busca "Power BI Desktop". Es la vía recomendada: se
  actualiza sola.
- **Descarga directa** — https://powerbi.microsoft.com/desktop/

No necesitas cuenta de Microsoft para trabajar en local. Solo se pide cuenta si
quieres *publicar* el informe en el servicio web, que para este proyecto no
hace falta.

---

## 1. Qué hay en esta carpeta

Un **modelo en estrella**: una tabla grande de hechos (un titulado por fila) y
cuatro tablas pequeñas de dimensiones que la describen. Es la forma estándar de
organizar datos para Power BI.

| Archivo | Filas | Qué contiene |
|---|---|---|
| `hechos_titulados.parquet` | 1.246.760 | Una fila por titulado: métricas, claves y el score de riesgo |
| `dim_institucion.csv` | 148 | Institución, tipo (Universidad, IP, CFT) |
| `dim_carrera.csv` | 5.286 | Carrera, área de conocimiento, clasificación CINE |
| `dim_territorio.csv` | 110 | Región, provincia, comuna de la sede |
| `dim_tiempo.csv` | 13 | Año y semestre de titulación (2020-S1 a 2026-S1) |
| `hechos_titulados.csv` | 1.246.760 | Los mismos hechos en CSV (156 MB), para cargar sin Power Query |
| `muestra_hechos.csv` | 5.000 | Muestra de los hechos, para abrir en Excel y mirar |

### Columnas de la tabla de hechos

**Claves** (conectan con las dimensiones): `cod_inst`, `id_carrera`,
`id_territorio`, `id_periodo`.

**Atributos para filtrar**: `genero`, `modalidad`, `jornada`, `rango_edad`,
`categoria_rezago`, `cohorte_ingreso`, `es_atipico`.

**Métricas**:

| Columna | Significado |
|---|---|
| `duracion_teorica_sem` | Duración del plan de estudios, en semestres |
| `duracion_real_sem` | Semestres que tomó realmente |
| `sobreduracion_sem` | Real − teórica. **La variable central del proyecto** |
| `indice_duracion` | Real / teórica. 1,0 = en plazo; 1,5 = 50 % más |
| `titulacion_oportuna` | Verdadero si se tituló dentro del plazo |
| `prob_rezago` | Probabilidad estimada de **no** titularse en plazo (modelo F3) |
| `edad_ingreso`, `edad_titulacion` | Edad en cada momento |

---

## 2. Cargar los datos

### Opción A — desde los CSV (la más simple para empezar)

1. Abre Power BI Desktop → **Obtener datos** → **Texto/CSV**.
2. Elige `hechos_titulados.csv` (156 MB, 1,25 millones de filas).
3. En la vista previa, confirma que *Origen de archivo* diga
   **65001: Unicode (UTF-8)** y pulsa **Cargar**. Tarda uno o dos minutos.
4. Repite con los cuatro `dim_*.csv`.

### Opción B — desde el Parquet (más rápido y liviano)

El conector **Parquet** del menú *Obtener datos* pide una **URL**: sirve para
archivos publicados en la web, no para un archivo del disco. Para un archivo
local se entra por otra puerta:

1. **Obtener datos → Consulta en blanco** (*Blank query*).
2. En el editor de Power Query: **Inicio → Editor avanzado**.
3. Reemplaza todo el contenido por:

   ```
   let
       Origen = Parquet.Document(
           File.Contents("<ruta del proyecto>\powerbi\hechos_titulados.parquet")
       )
   in
       Origen
   ```

   Reemplace `<ruta del proyecto>` por la carpeta donde tiene el repositorio.

4. **Listo** → renombra la consulta a `hechos_titulados` en el panel derecho →
   **Cerrar y aplicar**.

Carga unas cuatro veces más rápido que el CSV y deja el `.pbix` más liviano.
De paso muestra lo que hay detrás de Power BI: toda carga es una consulta en
lenguaje M, también cuando se hace con clics.

Si ves caracteres raros en los nombres de instituciones, la codificación se
detectó mal: en el paso de vista previa cambia *Origen de archivo* a
**65001: Unicode (UTF-8)**.

> **Importar vs. DirectQuery**: usa *Importar* (la opción por defecto). Carga
> los datos en memoria comprimidos y todo va rápido. DirectQuery sirve cuando
> los datos viven en una base que cambia constantemente, que no es el caso.

---

## 3. Crear las relaciones

Ve a la vista **Modelo** (tercer icono de la barra izquierda). Verás cinco
tablas sueltas. Arrastra cada clave de los hechos sobre la de su dimensión:

| Desde `hechos_titulados` | Hacia |
|---|---|
| `cod_inst` | `dim_institucion[cod_inst]` |
| `id_carrera` | `dim_carrera[id_carrera]` |
| `id_territorio` | `dim_territorio[id_territorio]` |
| `id_periodo` | `dim_tiempo[id_periodo]` |

Las cuatro deben quedar **muchos a uno** (`*` del lado de los hechos, `1` del
lado de la dimensión) y con dirección de filtro **única**. Power BI casi
siempre lo detecta bien; si marca "muchos a muchos", hay un duplicado en la
dimensión y algo salió mal en la exportación.

Al terminar, el diagrama tiene forma de estrella: los hechos al centro, las
dimensiones alrededor. Eso es todo el modelado.

---

## 4. Las primeras medidas (DAX)

Una **medida** es un cálculo que se recalcula según lo que el usuario filtre.
No es una columna: no ocupa espacio, se evalúa al vuelo.

Clic derecho sobre `hechos_titulados` → **Nueva medida**, y pega una por una:

```dax
Titulados = COUNTROWS(hechos_titulados)
```

```dax
Sobreduración media = AVERAGE(hechos_titulados[sobreduracion_sem])
```

```dax
% Titulación oportuna =
DIVIDE(
    CALCULATE([Titulados], hechos_titulados[titulacion_oportuna] = TRUE()),
    [Titulados]
)
```

```dax
% Rezago severo =
DIVIDE(
    CALCULATE([Titulados], hechos_titulados[categoria_rezago] = "Rezago severo"),
    [Titulados]
)
```

```dax
Semestres en exceso = SUM(hechos_titulados[sobreduracion_sem])
```

```dax
Brecha de género (sem) =
CALCULATE([Sobreduración media], hechos_titulados[genero] = "Hombre")
    - CALCULATE([Sobreduración media], hechos_titulados[genero] = "Mujer")
```

Formatea `% Titulación oportuna` y `% Rezago severo` como porcentaje con un
decimal (pestaña *Herramientas de medidas*), y `Sobreduración media` con dos
decimales.

**Cómo verificar que van bien.** Pon `Sobreduración media` en una tarjeta sin
ningún filtro: debe dar **2,76**. `% Titulación oportuna` debe dar **19,0 %** y
`Brecha de género` **0,94**. Son las cifras del informe de la Fase 2. Si no
coinciden, la medida está mal escrita o hay un filtro activo.

---

## 5. Página 1 — Panorama

1. **Cuatro tarjetas** (*Card*) arriba: `Titulados`, `Sobreduración media`,
   `% Titulación oportuna`, `% Rezago severo`.
2. **Gráfico de líneas**: eje `dim_tiempo[periodo]`, valores
   `Sobreduración media` y `% Titulación oportuna` (esta última en el eje
   secundario, porque están en escalas distintas).
3. **Gráfico de barras**: eje `dim_carrera[area_conocimiento]`, valor
   `Sobreduración media`, ordenado de mayor a menor. Derecho encabeza con 5,77
   y Educación cierra con 1,93.
4. **Segmentaciones** (*Slicer*) a la izquierda: `genero`, `modalidad`,
   `dim_institucion[tipo_inst_1]`.

Con esto ya tienes un tablero funcional. Prueba a hacer clic en una barra del
área de conocimiento: todo lo demás se filtra solo. Ese cruce automático es lo
que Power BI aporta sobre un gráfico estático.

---

## 6. Página 2 — Dónde se concentra el rezago

Aquí se reproduce, de forma interactiva, lo que hace `NodoJerarquia` en el
núcleo de la Fase 3.

Inserta un **Árbol de descomposición** (*Decomposition tree*):

- **Analizar**: `Sobreduración media`
- **Explicar por**: `tipo_inst_1`, `nomb_inst`, `area_conocimiento`,
  `nomb_carrera`

Haz clic en el `+` y elige *Valor alto*: el árbol desciende solo por la rama
con mayor sobreduración, nivel a nivel. Es exactamente el
`descender_por_maximo()` del proyecto, pero manejado con el ratón.

Añade al lado una **tabla** con `nomb_inst`, `Titulados` y
`Sobreduración media`, y aplica un filtro de nivel visual `Titulados >= 1000`
para que no aparezcan instituciones con cinco egresados y promedios absurdos.

---

## 7. Página 3 — Territorio y brechas

1. **Mapa**: campo `dim_territorio[region_sede]`, tamaño de burbuja
   `Titulados`, color `Sobreduración media`. Si el mapa no reconoce las
   regiones, selecciona la columna en el panel de datos y en *Categoría de
   datos* elige **Provincia o Estado**.
2. **Gráfico de columnas agrupadas**: eje `area_conocimiento`, leyenda
   `genero`, valor `Sobreduración media`. Muestra que la brecha favorable a las
   mujeres se sostiene en casi todas las áreas.
3. **Tarjeta**: `Brecha de género (sem)`.

---

## 8. Página 4 — Focalización por riesgo

Esta es la página que convierte el análisis en decisión, y usa el modelo
logístico de la Fase 3.

**Crea el parámetro de umbral.** Pestaña *Modelado* → **Nuevo parámetro** →
*Numérico*: nombre `Umbral`, de 0,50 a 0,95, incremento 0,01, valor inicial
0,81. Marca "Agregar segmentación a esta página".

**Crea las medidas que responden al umbral:**

```dax
Estudiantes sobre el umbral =
CALCULATE([Titulados], hechos_titulados[prob_rezago] >= [Umbral Valor])
```

```dax
% de la cohorte señalada =
DIVIDE([Estudiantes sobre el umbral], [Titulados])
```

```dax
Cobertura del rezago real =
DIVIDE(
    CALCULATE(
        [Titulados],
        hechos_titulados[prob_rezago] >= [Umbral Valor],
        hechos_titulados[titulacion_oportuna] = FALSE()
    ),
    CALCULATE([Titulados], hechos_titulados[titulacion_oportuna] = FALSE())
)
```

Ponlas en tres tarjetas y mueve el control deslizante. Verás el intercambio de
frente: bajar el umbral cubre a más estudiantes que efectivamente se rezagan,
pero señala a mucha más gente de la que un programa de apoyo puede atender.
Esa es la decisión real, y el tablero la hace tangible.

**Agrega un cuadro de texto con esta advertencia**, en serio:

> El modelo explica una fracción pequeña de la variación individual
> (R² = 0,085) y su exactitud no supera a predecir siempre la clase
> mayoritaria. El score sirve para **priorizar grupos**, no para etiquetar a un
> estudiante en particular.

Un tablero hace que cualquier número parezca autoritativo. Declarar la
limitación donde se ve es lo que separa un análisis serio de uno que vende
humo.

---

## 9. Errores frecuentes al empezar

| Síntoma | Causa | Solución |
|---|---|---|
| Los promedios dan valores absurdos en carreras pequeñas | Promedio sobre 3 egresados | Filtro de nivel visual `Titulados >= 100` |
| Aparece "Suma de sobreduracion_sem" | Arrastraste la columna, no la medida | Usa siempre las medidas que creaste |
| Caracteres raros en nombres | Codificación mal detectada | Origen de archivo → 65001 UTF-8 |
| El mapa no ubica las regiones | Falta la categoría geográfica | Marca la columna como *Provincia o Estado* |
| Relación "muchos a muchos" | Clave duplicada en la dimensión | Revisa la exportación |
| El archivo `.pbix` pesa mucho | Normal: los datos van dentro | Con 1,25 M filas quedan unos 15–25 MB |

---

## 10. Qué sigue

- **Publicar**: con una cuenta institucional puedes subir el informe al
  servicio web y compartir el enlace. Requiere licencia Pro para compartir.
- **Actualizar los datos**: si regeneras el pipeline, vuelve a correr
  `exportar_powerbi.py` y pulsa *Actualizar* en Power BI. Las medidas y los
  gráficos se mantienen.
- **Python dentro de Power BI**: existe un visual que ejecuta código Python en
  el informe. Sirve para demostrar la integración, pero es lento y exige Python
  instalado en cada equipo que abra el archivo. Para producción es mejor lo que
  hicimos: precalcular en Python y que Power BI solo consuma el resultado.
