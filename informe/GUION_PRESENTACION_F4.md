# Guion de la presentación audiovisual — Fase 4

**Proyecto:** Sobreduración en la titulación de la educación superior chilena (2020-2025)  
**Autor:** Sebastian Antunez Noguera  
**Diapositivas:** `informe/Presentacion_Fase4_Sebastian_Antunez.pptx`, construidas sobre el template institucional `PPT-Facultad-Ingenieria.pptx`

> Este mismo texto está cargado como **notas del orador** dentro del PPTX: se ve en la vista Presentador y al imprimir con notas. Ambos se generan del mismo archivo, así que no pueden desincronizarse.

---

## Cómo usar este guion

El texto en cursiva es lo que se dice. No hay que leerlo palabra por palabra, pero **los números en negrita deben decirse exactamente**: son los que el evaluador contrasta con el informe. Las acotaciones en recuadro no se leen.

Antes de grabar: cerrar notificaciones, abrir el PPTX en modo presentación (la vista Presentador muestra estas notas en la pantalla del expositor) y hacer una pasada completa de prueba.

---

## Diapositiva 1 — Portada · 0:00 - 0:20 · 20 s

> *Buenos días. Mi nombre es Sebastian Antunez y voy a presentar el proyecto final del curso Programación para la Ciencia de Datos: un análisis sobre la sobreduración en la titulación de la educación superior chilena, construido sobre 1.246.760 procesos de titulación reales entre 2020 y 2025.*

**RECORDAR: hablar más lento de lo que parece natural; en grabación siempre suena más rápido.**

---

## Diapositiva 2 — El problema · 0:20 - 1:10 · 50 s

> *Cada carrera en Chile declara una duración teórica. Sobre esa cifra se calculan la duración de las becas y los créditos estatales.*

> *Lo que el sistema no publica es cuánto se tarda en realidad. Y aquí está el punto de partida: al revisar el esquema oficial del SIES descubrí que las columnas que parecían tener la respuesta NO registran lo que el estudiante tardó, sino lo que el plan declara. Son un atributo de la carrera, no de la persona.*

> *Así que la pregunta fue: se puede reconstruir la duración real desde los registros administrativos, y caracterizar el rezago con esa variable derivada.*

**PAUSA de medio segundo antes de avanzar: es la bisagra del relato.**

---

## Diapositiva 3 — Cómo se construyó · 1:10 - 2:10 · 60 s

> *El proyecto se desarrolló en cuatro fases. La primera definió el problema y levantó el entorno reproducible. La segunda construyó el pipeline que convierte 955 megabytes de archivos crudos en un conjunto analítico validado. La tercera implementó el núcleo algorítmico desde primeros principios, con medición formal de complejidad y un modelo de dominio orientado a objetos. Y la cuarta, que es la que presento, ejecuta todo eso de extremo a extremo.*

> *La transformación central está abajo: la duración real se deriva del año y semestre de ingreso y de titulación. El "más uno" no es arbitrario: quien ingresa y se titula en el mismo semestre cursó un semestre, no cero. Esa coherencia aritmética se verifica como regla de validación sobre el dataset completo.*

**SI EL VIDEO VA CORTO, agregar aquí: el pipeline retiene el 72,9 por ciento de las filas originales y cada exclusión está cuantificada en una bitácora auditable.**

---

## Diapositiva 4 — El resultado principal · 2:10 - 3:05 · 55 s

> *Este es el resultado central. Solo el 19 por ciento de los titulados egresa dentro del plazo que su propio plan declara. Dicho al revés: cuatro de cada cinco se titulan fuera de plazo.*

> *El exceso promedio es de 2 coma 76 semestres, un 43 por ciento más de tiempo del previsto. Y el rezago severo, más de cuatro semestres de exceso, alcanza al 20 coma 4 por ciento: prácticamente la misma proporción que logra titularse a tiempo.*

> *Agregado, el sistema acumula 3 coma 55 millones de semestres-estudiante por sobre lo planificado en el período.*

> *El gráfico de la izquierda muestra por qué reporto media y mediana: la distribución es asimétrica, con una cola larga que arrastra el promedio.*

---

## Diapositiva 5 — El rezago no es homogéneo · 3:05 - 4:05 · 60 s

> *El rezago tampoco se reparte de forma pareja.*

> *Por área de conocimiento, Derecho triplica a Educación: 5,77 semestres frente a 1,93. Casi cuatro semestres, dos años, separan a la carrera más rezagada de la menos rezagada.*

> *Por tipo de institución, las universidades acumulan más rezago que los institutos profesionales y su tasa de titulación oportuna es menos de la mitad. Eso sugiere que la duración declarada es menos realista en carreras universitarias largas.*

> *Y por género, las mujeres se titulan 0 coma 93 semestres antes. Lo importante del panel derecho es que la brecha se sostiene en las diez áreas sin excepción: no es que estudien carreras más cortas, es que dentro de cada área se titulan antes.*

---

## Diapositiva 6 — La pandemia desplazó titulaciones · 4:05 - 4:55 · 50 s

> *Este hallazgo no estaba en ninguna de las fases anteriores; apareció al mirar la serie semestral en vez del promedio agregado.*

> *En 2020 se titularon unas 87 mil personas menos que en un año normal, y la sobreduración media tocó su mínimo. En 2021 el volumen se recuperó y la sobreduración alcanzó su máximo.*

> *La tentación es decir que 2020 fue un buen año. Pero no: las titulaciones se POSTERGARON. Quienes debían egresar en 2020 lo hicieron en 2021, con uno o dos semestres adicionales encima. El mínimo y el máximo son el mismo fenómeno visto en dos momentos, y el mecanismo es de desplazamiento administrativo, no de deterioro académico.*

---

## Diapositiva 7 — Una limitación que condiciona todo · 4:55 - 5:35 · 40 s

> *Y aquí una limitación que condiciona todo lo anterior, y que creo que es uno de los resultados más valiosos del proyecto.*

> *Una base de titulados solo contiene a quien terminó. De las cohortes recientes solo se han titulado los excepcionalmente rápidos, porque son los únicos que alcanzaron a hacerlo. De las cohortes antiguas, en cambio, los que aparecen son los extremadamente rezagados.*

> *Ninguna cohorte está completa, y lo están en direcciones opuestas. Por eso el descenso de la serie desde 2024 no puede leerse como una mejora del sistema. Es una limitación de la fuente, no del procesamiento, y declararla es parte del resultado.*

---

## Diapositiva 8 — El rigor detrás de las cifras · 5:35 - 6:15 · 40 s

> *Sobre el trabajo técnico: el proyecto tiene 73 pruebas automatizadas que cubren casos normales, límite y excepciones, y 9 reglas de coherencia del dominio, todas aprobadas.*

> *Los algoritmos se implementaron desde cero y se verificaron contra pandas, sorted y NumPy ANTES de medir su tiempo: medir un algoritmo incorrecto no tiene sentido.*

> *Las curvas log-log confirmaron las cotas teóricas, pero también mostraron dónde la teoría no basta: quickselect es orden n en comparaciones y sin embargo escala como n elevado a 1,22, porque cada nivel de recursión asigna tres listas nuevas. La cota describe el crecimiento, no la constante. Ese contraste fue uno de los aprendizajes centrales del curso.*

**SI EL VIDEO VA LARGO, recortar esta lámina a las dos primeras cifras y omitir el detalle de quickselect: ahorra unos 20 segundos.**

---

## Diapositiva 9 — Conclusiones · 6:15 - 6:55 · 40 s

> *En síntesis, cuatro conclusiones.*

> *El rezago es masivo y estructural, no aleatorio.*

> *La pandemia desplazó titulaciones en lugar de empeorarlas.*

> *Los registros administrativos no explican el caso individual: el R cuadrado es de 0 coma 085 y la clasificación no supera a predecir siempre la clase mayoritaria. Eso no es un fracaso del modelo, es un resultado: el rezago depende de trayectorias personales que esta fuente no registra.*

> *Y todo el proyecto es reproducible: cuatro comandos lo instalan y ejecutan, con 45 commits verificables y cada cifra rastreable hasta el archivo que la generó.*

---

## Diapositiva 10 — Cierre · 6:55 - 7:10 · 15 s

> *Lo que queda para seguir: incorporar la base de matrícula para ver la deserción, que hoy es invisible; usar modelos de supervivencia, que son los adecuados para datos censurados; y ampliar las variables hacia la trayectoria individual.*

> *El repositorio completo está disponible en GitHub. Muchas gracias.*

---

## Control de tiempos

| # | Diapositiva | Ventana | Palabras habladas |
|---|---|---|---|
| 1 | Portada | 0:00 - 0:20 · 20 s | 46 |
| 2 | El problema | 0:20 - 1:10 · 50 s | 103 |
| 3 | Cómo se construyó | 1:10 - 2:10 · 60 s | 123 |
| 4 | El resultado principal | 2:10 - 3:05 · 55 s | 119 |
| 5 | El rezago no es homogéneo | 3:05 - 4:05 · 60 s | 118 |
| 6 | La pandemia desplazó titulaciones | 4:05 - 4:55 · 50 s | 110 |
| 7 | Una limitación que condiciona todo | 4:55 - 5:35 · 40 s | 105 |
| 8 | El rigor detrás de las cifras | 5:35 - 6:15 · 40 s | 109 |
| 9 | Conclusiones | 6:15 - 6:55 · 40 s | 94 |
| 10 | Cierre | 6:55 - 7:10 · 15 s | 46 |
| | **Total** | | **973** |

La duración real depende del ritmo al hablar. Con este guion:

| Ritmo | Palabras por minuto | Duración |
|---|---|---|
| Rápido | 155 | 6:17 |
| Normal | 140 | 6:57 |
| Pausado | 125 | 7:47 |

Los tres casos caen dentro del rango exigido de 5 a 8 minutos, con margen en ambos extremos. Aun así conviene cronometrar la pasada de prueba: si supera los 7:30, aplicar el recorte indicado en la diapositiva 8.

## Recomendaciones de grabación

- Grabar la pantalla con el PPTX en modo presentación y narrar en vivo. No hace falta aparecer en cámara, aunque suma si el formato lo permite.
- Hablar más lento de lo que parece natural: en grabación siempre suena más rápido.
- Si se equivoca en una frase, rehacer solo esa diapositiva y unir los cortes, en lugar de repetir todo.
- Dejar medio segundo de silencio al cambiar de lámina: ayuda al montaje y da tiempo al espectador.