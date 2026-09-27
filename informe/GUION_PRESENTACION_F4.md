# Guion de la presentación audiovisual — Fase 4

**Proyecto:** Sobreduración en la titulación de la educación superior chilena (2020-2025)
**Autor:** Sebastian Antunez Noguera · **Duración objetivo:** 6 min 30 s (rango exigido: 5 a 8 min)
**Diapositivas:** `informe/Presentacion_Fase4_Sebastian_Antunez.pptx` (10 láminas)

---

## Cómo usar este guion

El texto en cursiva es lo que se dice; no hay que leerlo palabra por palabra, pero los
**números en negrita deben decirse exactamente** porque son los que el evaluador
contrasta con el informe. Cada bloque indica el tiempo acumulado, de modo que si al
llegar a la diapositiva 6 el reloj marca más de 4:20, conviene abreviar.

Antes de grabar: cerrar notificaciones, abrir el PPTX en modo presentación y tener el
notebook y el tablero listos por si se quiere mostrar algo en vivo (opcional).

---

## Diapositiva 1 — Portada · 0:00 → 0:20 (20 s)

> *Buenos días. Mi nombre es Sebastian Antunez y voy a presentar el proyecto final del
> curso Programación para la Ciencia de Datos: un análisis sobre la sobreduración en la
> titulación de la educación superior chilena, construido sobre **1.246.760** procesos
> de titulación reales entre 2020 y 2025.*

---

## Diapositiva 2 — El problema · 0:20 → 1:10 (50 s)

> *Cada carrera en Chile declara una duración teórica: los semestres que el plan de
> estudios compromete con el estudiante. Esa cifra no es decorativa — define expectativas
> de gasto, y sobre ella se calculan la duración de las becas y los créditos estatales.*
>
> *Lo que el sistema no publica es cuánto se tarda en realidad. Y aquí está el punto de
> partida del proyecto: al revisar el esquema oficial del SIES descubrí que las columnas
> que parecían tener la respuesta —duración de estudio, duración del proceso de
> titulación— **no registran lo que el estudiante tardó, sino lo que el plan declara**.
> Son un atributo de la carrera, no de la persona.*
>
> *Así que la pregunta técnica del proyecto fue: ¿se puede reconstruir la duración real
> a partir de los registros administrativos, y caracterizar el rezago con esa variable
> derivada?*

**Nota:** aquí conviene pausar medio segundo antes de pasar. Es la bisagra del relato.

---

## Diapositiva 3 — Cómo se construyó · 1:10 → 2:10 (60 s)

> *El proyecto se desarrolló en cuatro fases. La primera definió el problema y levantó un
> entorno reproducible: entorno virtual, dependencias fijadas por versión y el código
> separado en módulos desde el inicio.*
>
> *La segunda construyó el pipeline que convierte **955 megabytes** de archivos crudos en
> un conjunto analítico validado: resolución de códigos centinela, duplicados,
> normalización de texto y la derivación de la variable objetivo.*
>
> *La tercera implementó el núcleo algorítmico desde primeros principios —agregación,
> ordenamiento, selección y búsqueda— con medición formal de complejidad y un modelo de
> dominio orientado a objetos.*
>
> *Y la cuarta, que es la que presento, ejecuta todo eso de extremo a extremo y produce
> los resultados.*
>
> *La transformación central está abajo: la duración real se deriva del año y semestre de
> ingreso y de titulación. El «más uno» no es un ajuste arbitrario: quien ingresa y se
> titula en el mismo semestre cursó un semestre, no cero. Esa coherencia aritmética se
> verifica como regla de validación sobre el dataset completo.*

---

## Diapositiva 4 — El resultado principal · 2:10 → 3:05 (55 s)

> *Este es el resultado central. Solo el **19 por ciento** de los titulados egresa dentro
> del plazo que su propio plan declara. Dicho al revés: cuatro de cada cinco se titulan
> fuera de plazo.*
>
> *El exceso promedio es de **2 coma 76 semestres** — un 43 por ciento más de tiempo del
> previsto. Y el rezago severo, más de cuatro semestres de exceso, alcanza al **20 coma 4
> por ciento**: prácticamente la misma proporción que logra titularse a tiempo.*
>
> *Agregado, el sistema acumula **3 coma 55 millones** de semestres-estudiante por sobre
> lo planificado en el período.*
>
> *El gráfico de la izquierda muestra por qué reporto media y mediana: la distribución es
> fuertemente asimétrica. La mayoría se concentra en uno a tres semestres de rezago, pero
> una cola larga arrastra el promedio.*

---

## Diapositiva 5 — El rezago no es homogéneo · 3:05 → 4:05 (60 s)

> *El rezago tampoco se reparte de forma pareja.*
>
> *Por área de conocimiento, **Derecho triplica a Educación**: 5,77 semestres frente a
> 1,93. Casi cuatro semestres —dos años— separan a la carrera más rezagada de la menos
> rezagada.*
>
> *Por tipo de institución, las universidades acumulan más rezago que los institutos
> profesionales y su tasa de titulación oportuna es menos de la mitad. Eso sugiere que la
> duración declarada es menos realista en carreras universitarias largas.*
>
> *Y por género, las mujeres se titulan **0 coma 93 semestres antes** que los hombres. Lo
> importante del panel de la derecha es que esa brecha se sostiene en las **diez áreas
> sin excepción**. Eso descarta que se explique por composición de carreras: no es que
> las mujeres estudien carreras más cortas, es que dentro de cada área se titulan antes.*

---

## Diapositiva 6 — El efecto de la pandemia · 4:05 → 4:55 (50 s)

> *Este hallazgo no estaba en ninguna de las fases anteriores; apareció al mirar la serie
> semestral en vez del promedio agregado.*
>
> *En 2020 se titularon unas **87 mil personas menos** que en un año normal, y la
> sobreduración media tocó su mínimo. En 2021 el volumen se recuperó y la sobreduración
> alcanzó su máximo.*
>
> *La tentación es decir que 2020 fue un buen año. Pero no: las titulaciones se
> **postergaron**. Quienes debían egresar en 2020 lo hicieron en 2021, con uno o dos
> semestres adicionales encima. El mínimo y el máximo son el mismo fenómeno visto en dos
> momentos, y el mecanismo es de desplazamiento administrativo, no de deterioro
> académico.*

---

## Diapositiva 7 — La limitación · 4:55 → 5:35 (40 s)

> *Y aquí una limitación que condiciona todo lo anterior, y que creo que es uno de los
> resultados más valiosos del proyecto.*
>
> *Una base de titulados solo contiene a quien terminó. De las cohortes recientes solo se
> han titulado los excepcionalmente rápidos, porque son los únicos que alcanzaron a
> hacerlo. De las cohortes antiguas, en cambio, los que aparecen son los extremadamente
> rezagados.*
>
> *Ninguna cohorte está completa, y están incompletas en direcciones opuestas. Por eso el
> descenso de la serie desde 2024 no puede leerse como una mejora del sistema. Es una
> limitación del diseño de la fuente, no del procesamiento, y declararla es parte del
> resultado.*

---

## Diapositiva 8 — El rigor técnico · 5:35 → 6:15 (40 s)

> *Sobre el trabajo técnico: el proyecto tiene **73 pruebas automatizadas** que cubren
> casos normales, límite y excepciones, y **9 reglas de coherencia** del dominio, todas
> aprobadas.*
>
> *Los algoritmos se implementaron desde cero y se verificaron contra pandas, sorted y
> NumPy **antes** de medir su tiempo: medir un algoritmo incorrecto no tiene sentido.*
>
> *Las curvas log-log confirmaron las cotas teóricas. Pero también mostraron dónde la
> teoría no basta: quickselect es orden n en comparaciones, y sin embargo escala como
> **n elevado a 1,22**, porque cada nivel de recursión asigna tres listas nuevas. La cota
> describe el crecimiento, no la constante ni el costo de la memoria. Esa diferencia
> entre teoría y medición fue, para mí, uno de los aprendizajes centrales del curso.*

---

## Diapositiva 9 — Conclusiones · 6:15 → 6:55 (40 s)

> *En síntesis, cuatro conclusiones.*
>
> *El rezago es masivo y estructural, no aleatorio.*
>
> *La pandemia desplazó titulaciones en lugar de empeorarlas.*
>
> *Los registros administrativos no explican el caso individual: el R cuadrado es de
> **0 coma 085** y la clasificación no supera a predecir siempre la clase mayoritaria.
> Eso no es un fracaso del modelo, es un resultado: el rezago depende de trayectorias
> personales que esta fuente no registra.*
>
> *Y todo el proyecto es reproducible: cuatro comandos lo instalan y ejecutan, hay **36
> commits** con historial verificable, y cada cifra de este informe puede rastrearse
> hasta el archivo que la generó.*

---

## Diapositiva 10 — Cierre · 6:55 → 7:10 (15 s)

> *Lo que queda para seguir: incorporar la base de matrícula para ver la deserción, que
> hoy es invisible; usar modelos de supervivencia, que son los adecuados para datos
> censurados; y ampliar las variables hacia la trayectoria individual.*
>
> *El repositorio completo está disponible en GitHub. Muchas gracias.*

---

## Control de tiempos

| Diapositiva | Duración | Acumulado |
|---|---|---|
| 1. Portada | 20 s | 0:20 |
| 2. El problema | 50 s | 1:10 |
| 3. Cómo se construyó | 60 s | 2:10 |
| 4. Resultado principal | 55 s | 3:05 |
| 5. Rezago no homogéneo | 60 s | 4:05 |
| 6. Pandemia | 50 s | 4:55 |
| 7. Limitación | 40 s | 5:35 |
| 8. Rigor técnico | 40 s | 6:15 |
| 9. Conclusiones | 40 s | 6:55 |
| 10. Cierre | 15 s | **7:10** |

Queda holgura en ambos extremos: si se habla rápido el video dura unos 6 minutos, y si
se habla pausado no pasa de 7 y medio. Ambos casos están dentro del rango exigido.

## Si el video queda corto

Añadir en la diapositiva 3, después de la transformación central, una frase sobre el
pipeline: *«El pipeline retiene el 72,9 % de las filas originales y cada exclusión está
cuantificada y justificada en una bitácora auditable»*. Suma unos 12 segundos.

## Si el video queda largo

Recortar la diapositiva 8 a las dos primeras cifras (73 pruebas y 9 reglas) y omitir el
detalle de quickselect. Ahorra unos 20 segundos sin perder el hilo.

## Recomendaciones de grabación

- Grabar la pantalla con el PPTX en modo presentación y narrar en vivo; no hace falta
  aparecer en cámara, aunque suma si el formato lo permite.
- Hacer una pasada completa de prueba antes de grabar en serio. El primer intento casi
  siempre se pasa de tiempo.
- Si se equivoca en una frase, conviene rehacer solo esa diapositiva y unir los cortes,
  en lugar de repetir todo.
- Hablar más lento de lo que parece natural: en grabación siempre suena más rápido.
