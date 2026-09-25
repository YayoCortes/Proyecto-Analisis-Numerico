"""Metodo de Biseccion.

Parte el intervalo [a, b] por la mitad en cada paso y se queda con la
mitad donde la funcion cambia de signo.

    c = (a + b) / 2
"""

from metodos import cerrados
from nucleo.resultado import Resultado

NOMBRE = "Bisección"
CLAVE = "biseccion"
TIPO = "cerrado"
RESUMEN = "Parte el intervalo [a, b] a la mitad en cada paso y se queda con la mitad donde f(x) cambia de signo."
FORMULA = "c = (a + b) / 2"

PARAMETROS = cerrados.PARAMETROS_CERRADOS
COLUMNAS = cerrados.columnas_cerradas("c = (a+b)/2")


def _punto_medio(a, b, fa, fb):
    return (a + b) / 2


def biseccion(funcion, a, b, tol_pct, max_iter) -> Resultado:
    return cerrados.resolver(funcion, a, b, tol_pct, max_iter, _punto_medio)


def ejecutar(funcion, parametros: dict, tol_pct: float, max_iter: int) -> Resultado:
    """Entrada unica que usa la interfaz grafica."""
    a, b = cerrados.leer_intervalo(parametros)
    return biseccion(funcion, a, b, tol_pct, max_iter)
