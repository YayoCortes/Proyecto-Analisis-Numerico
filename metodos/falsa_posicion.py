"""Metodo de Falsa Posicion (regla falsa).

En lugar de partir el intervalo a la mitad, traza la recta que une
(a, f(a)) con (b, f(b)) y toma el punto donde esa recta cruza el eje x.

    c = b - f(b) * (a - b) / (f(a) - f(b))
"""

from metodos import cerrados
from nucleo.resultado import ErrorMetodo, Resultado

NOMBRE = "Falsa Posición"
CLAVE = "falsa_posicion"
TIPO = "cerrado"
RESUMEN = "Une (a, f(a)) con (b, f(b)) con una recta y toma el punto donde esa recta corta el eje x."
FORMULA = "c = b - f(b)(a - b) / (f(a) - f(b))"

PARAMETROS = cerrados.PARAMETROS_CERRADOS
COLUMNAS = cerrados.columnas_cerradas("c")


def _corte_con_eje(a, b, fa, fb):
    denominador = fa - fb
    if denominador == 0:  # division entre cero en la formula
        raise ErrorMetodo(
            f"f({a:g}) y f({b:g}) son iguales: la recta entre los dos puntos "
            "es horizontal y nunca corta el eje x."
        )
    return b - (fb * (a - b) / denominador)


def falsa_posicion(funcion, a, b, tol_pct, max_iter) -> Resultado:
    return cerrados.resolver(funcion, a, b, tol_pct, max_iter, _corte_con_eje)


def ejecutar(funcion, parametros: dict, tol_pct: float, max_iter: int) -> Resultado:
    """Entrada unica que usa la interfaz grafica."""
    a, b = cerrados.leer_intervalo(parametros)
    return falsa_posicion(funcion, a, b, tol_pct, max_iter)
