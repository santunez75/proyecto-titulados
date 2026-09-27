# Registro de cambios y trazabilidad de mejoras

Proyecto: **Sobreduración en la titulación de la educación superior chilena (2020-2025)**
Asignatura: Programación para la Ciencia de Datos (202682.1927) · Autor: Sebastian Antunez Noguera

Este archivo registra las mejoras aplicadas al proyecto, su origen, el commit que las
implementa y su impacto técnico. Cada fila es verificable con `git show <hash>`.

---

## 1. Mejoras derivadas de observaciones formativas y autodiagnóstico

| # | Observación / problema detectado | Fase donde surgió | Mejora aplicada | Commit | Impacto técnico |
|---|---|---|---|---|---|
| 1 | La normalización de texto recorría fila por fila 1,7 millones de cadenas; la limpieza tardaba minutos | F2 | Se normaliza el catálogo de valores únicos (unos miles) y se mapea de vuelta | `5e07669` | **Rendimiento**: reduce el costo de 1,7 M de operaciones a ~8 mil |
| 2 | Los tipos anulables de pandas (`Int16`, `boolean`) rompían matplotlib y propagaban `NA` en comparaciones | F2 | Conversión explícita a `float64` antes de graficar; `fillna(True)` en el marcado de atípicos | `f698c37` | **Corrección**: 19 filas dejaban de marcarse en silencio |
| 3 | La celda de pruebas usaba `sys.executable`: con un kernel distinto al entorno virtual fallaba sin mostrar la causa | F2 (detectado al reproducir en un segundo equipo) | La celda apunta al intérprete del `.venv` del proyecto e imprime `stderr` cuando el código de salida no es cero | `b8770f5` | **Reproducibilidad**: un fallo silencioso pasa a ser un fallo diagnosticable |
| 4 | Los notebooks dependían del Parquet completo, no versionado: en un equipo sin los CSV originales no se podían ejecutar | F2 | `cargar_datos()` degrada a la muestra versionada de 5.000 registros con aviso explícito | `40be4d9` | **Reproducibilidad**: el proyecto corre en cualquier equipo sin datos externos |
| 5 | La lógica analítica vivía en funciones sueltas sobre DataFrames; los invariantes del dominio no estaban garantizados en ninguna parte | F2 | Modelo de dominio con `Titulado` y `Cohorte`: validación en los setters y magnitudes derivadas como propiedades de solo lectura | `a1342a5` | **Modularidad**: un objeto no puede existir en estado incoherente |
| 6 | La agregación por grupo recorría la secuencia una vez por grupo (O(n·k)) | F3 | Agregación en una sola pasada O(n) con dos diccionarios acumuladores | `8d87723` | **Rendimiento**: 1,9× más rápida y 860× menos memoria (0,7 KB vs. 603,9 KB) |
| 7 | Los conteos por umbral recorrían la lista completa por cada categoría de rezago | F3 | Dos búsquedas binarias recursivas sobre una copia ordenada; cota superior para manejar los empates | `8d87723` | **Rendimiento**: O(log n) por consulta; 6.516× más rápido que el recorrido lineal |
| 8 | El descenso de gradiente devolvía pesos infinitos o `NaN` con tasas de aprendizaje altas | F3 | Detección explícita de divergencia con excepción y mensaje accionable | `40be4d9` | **Robustez**: error claro en vez de resultado silenciosamente inválido |
| 9 | El informe de la Fase 3 tenía el contenido exigido pero no la estructura mínima solicitada | F3 (sumativa) | Reorganización completa en las secciones I–VI de las instrucciones | `b5523ad` | **Documentación**: correspondencia uno a uno con la pauta de evaluación |
| 10 | El informe citaba la agregación propia como «5 veces más rápida»; el 5,5 de la tabla era la razón contra pandas, no contra la versión ingenua | F3 (verificación cruzada en F4) | Cifras corregidas a 1,9× en tiempo y 860× en memoria, y aclaración de la comparación de `quickselect` | `12ae178` | **Confiabilidad**: toda cifra del informe es rastreable a `reports/tables/` |

## 2. Evolución por fase

| Fase | Commits | Entregable principal | Estado |
|---|---|---|---|
| F1 | `8d219de` … `02cd383` | Definición del problema y entorno reproducible | Completada |
| F2 | `c8bb51e` … `fc75c8f` | Pipeline de limpieza, transformación y validación | Completada |
| F3 | `76867c7` … `b62d36a` | Núcleo algorítmico, eficiencia y POO | Completada |
| F4 | `12ae178` … | Reporte analítico, visualizaciones y comunicación | En entrega |

Ramas utilizadas: `main`, `fase-2/pipeline-datos`, `fase-3/nucleo-algoritmico`. Las dos
ramas de trabajo se integraron a `main` con fusiones explícitas (`b1021bc` y `9062995`),
de modo que el punto de integración queda registrado en el historial.

## 3. Nota sobre la autoría

El proyecto es de autoría individual. El historial registra dos identidades de Git
(`Sebastian Antunez` y `santunez75`) que corresponden a la misma persona trabajando desde
dos equipos distintos; ambas apuntan a la cuenta institucional del autor.

## 4. Cómo verificar cualquier fila de este registro

```bash
git show <hash>              # cambios exactos del commit
git log --oneline --graph    # estructura de ramas y fusiones
git log --follow <archivo>   # historia de un archivo concreto
```
