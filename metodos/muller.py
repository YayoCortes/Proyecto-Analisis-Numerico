"""Metodo de Muller.

Metodo abierto que parte de tres puntos x0, x1, x2. Por ellos pasa una
parabola, y la nueva aproximacion x3 es el punto donde esa parabola corta
el eje x (el corte mas cercano a x2).

    h0 = x1 - x0                 h1 = x2 - x1
    d0 = (f(x1) - f(x0)) / h0    d1 = (f(x2) - f(x1)) / h1
    a  = (d1 - d0) / (h1 + h0)
    b  = a * h1 + d1
    c  = f(x2)
    x3 = x2 - 2c / (b ± sqrt(b^2 - 4ac))

El signo del denominador se toma igual al de b: asi el denominador es lo
mas grande posible y se evita restar dos numeros casi iguales. Despues se
descarta x0 y se repite con x1, x2, x3.
"""

import math

from nucleo.resultado import (
    CONVERGIO,
    MAX_ITERACIONES,
    RAIZ_EXACTA,
    Columna,
    ErrorMetodo,
    Iteracion,
    Parametro,
    Resultado,
)
from nucleo.validacion import (
    error_relativo,
    exigir_finito,
    numero,
    validar_comunes,
)

NOMBRE = "Müller"
CLAVE = "muller"
TIPO = "abierto"
GRAFICA = "parabolas"
RESUMEN = (
    "Por tres puntos x₀, x₁, x₂ de la curva pasa una parábola. La nueva "
    "aproximación es el punto donde esa parábola corta el eje x."
)
FORMULA = "x₃ = x₂ - 2c / (b ± √(b² - 4ac))"

# Claves propias (y no x0) para no mezclar sus valores con los de Newton
PARAMETROS = [
    Parametro("m0", "Punto x₀", "4.5"),
    Parametro("m1", "Punto x₁", "5.5"),
    Parametro("m2", "Punto x₂", "5"),
]

# Las 15 cantidades de cada iteracion, en el orden en que se calculan
COLUMNAS = [
    Columna("numero", "i", 40),
    Columna("x0", "x₀", 112),
    Columna("x1", "x₁", 112),
    Columna("x2", "x₂", 112),
    Columna("f0", "f(x₀)", 118),
    Columna("f1", "f(x₁)", 118),
    Columna("f2", "f(x₂)", 118),
    Columna("h0", "h₀", 112),
    Columna("h1", "h₁", 112),
    Columna("d0", "δ₀", 118),
    Columna("d1", "δ₁", 118),
    Columna("a", "a", 118),
    Columna("b", "b", 118),
    Columna("c", "c", 118),
    Columna("valor", "x₃", 118),
    Columna("ea", "ea %", 105),
]

# Un discriminante apenas negativo suele ser solo redondeo (raiz doble)
REDONDEO_DISCRIMINANTE = 1e-12


def muller(funcion, x0, x1, x2, tol_pct, max_iter) -> Resultado:
    validar_comunes(tol_pct, max_iter)

    if x0 == x1 or x1 == x2 or x0 == x2:
        raise ErrorMetodo(
            "Los tres puntos iniciales deben ser distintos:\n"
            "por dos puntos iguales no se puede trazar la parábola."
        )

    f0 = exigir_finito(funcion.f(x0), x0)
    f1 = exigir_finito(funcion.f(x1), x1)
    f2 = exigir_finito(funcion.f(x2), x2)

    iteraciones: list[Iteracion] = []

    for i in range(1, max_iter + 1):
        h0 = x1 - x0
        h1 = x2 - x1
        if h0 == 0 or h1 == 0 or h0 + h1 == 0:
            raise ErrorMetodo(
                f"En la iteración {i} dos de los tres puntos coinciden.\n"
                "Prueba con otros valores iniciales."
            )

        d0 = (f1 - f0) / h0
        d1 = (f2 - f1) / h1
        a = (d1 - d0) / (h1 + h0)
        b = a * h1 + d1
        c = f2

        discriminante = b * b - 4 * a * c
        if discriminante < 0:
            if discriminante >= -REDONDEO_DISCRIMINANTE * (b * b + abs(4 * a * c)):
                discriminante = 0.0
            else:
                raise ErrorMetodo(
                    f"En la iteración {i} la parábola no corta el eje x:\n"
                    f"b² - 4ac = {discriminante:.6g} es negativo y la raíz "
                    "sería un número complejo.\n"
                    "Prueba con puntos iniciales más cerca de una raíz real."
                )

        raiz_disc = math.sqrt(discriminante)
        denominador = b + raiz_disc if abs(b + raiz_disc) >= abs(b - raiz_disc) else b - raiz_disc
        if denominador == 0:
            raise ErrorMetodo(
                f"En la iteración {i} el denominador b ± √(b² - 4ac) vale cero.\n"
                "Prueba con otros valores iniciales."
            )

        x3 = x2 + (-2 * c / denominador)
        f3 = exigir_finito(funcion.f(x3), x3)
        ea = error_relativo(x3, x2)

        iteraciones.append(
            Iteracion(
                numero=i,
                valor=x3,
                fx=f3,
                ea=ea,
                extra={
                    "x0": x0, "x1": x1, "x2": x2,
                    "f0": f0, "f1": f1, "f2": f2,
                    "h0": h0, "h1": h1,
                    "d0": d0, "d1": d1,
                    "a": a, "b": b, "c": c,
                },
            )
        )

        if f3 == 0:
            return Resultado(iteraciones, x3, f3, RAIZ_EXACTA)
        if ea <= tol_pct:
            return Resultado(iteraciones, x3, f3, CONVERGIO)

        # Se descarta el punto mas viejo
        x0, x1, x2 = x1, x2, x3
        f0, f1, f2 = f1, f2, f3

    ultima = iteraciones[-1]
    return Resultado(iteraciones, ultima.valor, ultima.fx, MAX_ITERACIONES)


def ejecutar(funcion, parametros: dict, tol_pct: float, max_iter: int) -> Resultado:
    """Entrada unica que usa la interfaz grafica."""
    x0 = numero(parametros.get("m0"), "x₀")
    x1 = numero(parametros.get("m1"), "x₁")
    x2 = numero(parametros.get("m2"), "x₂")
    return muller(funcion, x0, x1, x2, tol_pct, max_iter)
