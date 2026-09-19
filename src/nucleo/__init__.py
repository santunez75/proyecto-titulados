"""Nucleo algoritmico del proyecto (Fase 3).

Implementa, desde primeros principios, los algoritmos y las abstracciones que en
la Fase 2 delegabamos integramente en pandas, para poder razonar sobre su
complejidad, medir su eficiencia y organizar el dominio con programacion
orientada a objetos.

Modulos
-------
algoritmos    Agregacion en una pasada, merge sort y quickselect recursivos,
              busqueda binaria recursiva. Cada funcion declara su complejidad.
benchmark     Mediciones reproducibles con timeit y tracemalloc; curvas de
              escalamiento y estimacion empirica del orden de crecimiento.
dominio       Clases Titulado y Cohorte (encapsulamiento, metodos especiales).
metricas      Jerarquia Metrica -> subclases intercambiables (patron Strategy).
jerarquia     Arbol Sistema -> Tipo -> Institucion -> Carrera con agregacion y
              busqueda recursivas (patron Composite).
preparacion   Escaladores y codificador one-hot con interfaz comun
              (herencia + polimorfismo) y particion entrenamiento/prueba.
modelos       Regresion lineal y logistica por descenso de gradiente
              (patron Template Method) y solucion cerrada de contraste.
fachada       Punto de entrada unico que orquesta el flujo (patron Facade).
"""

__version__ = "0.3.0"
