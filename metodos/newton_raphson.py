"""Metodo de Newton-Raphson.

Metodo abierto: parte de un solo punto x0 y en cada paso sigue la recta
tangente a la curva hasta el eje x.

    x(i+1) = x(i) - f(x(i)) / f'(x(i))

La derivada no la escribe el usuario: se obtiene simbolicamente con SymPy
a partir de la misma f(x) (ver nucleo/parser.py).
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

NOMBRE = "Newton-Raphson"
CLAVE = "newton_raphson"
TIPO = "abierto"
RESUMEN = "Desde un solo punto x₀, sigue la recta tangente a la curva hasta donde corta el eje x."
FORMULA = "x(i+1) = x(i) - f(x(i)) / f'(x(i))"

PARAMETROS = [
    Parametro("x0", "x₀  (valor inicial)", "-1.5"),
]

COLUMNAS = [
    Columna("numero", "i", 45),
    Columna("xi", "xᵢ", 140),
    Columna("fxi", "f(xᵢ)", 140),
    Columna("dfxi", "f'(xᵢ)", 140),
    Columna("valor", "xᵢ₊₁", 150),
    Columna("ea", "ea %", 115),
]

# Por debajo de esto la tangente es practicamente horizontal y el metodo
# no puede continuar (el codigo original fallaba con ZeroDivisionError).
DERIVADA_MINIMA = 1e-14


def newton_raphson(funcion, x0, tol_pct, max_iter) -> Resultado:
    validar_comunes(tol_pct, max_iter)

    xi = x0
    fxi = exigir_finito(funcion.f(xi), xi)

    if fxi == 0:
        return Resultado([Iteracion(1, xi, fxi, None, {"xi": xi, "fxi": fxi, "dfxi": funcion.df(xi)})], xi, fxi, RAIZ_EXACTA)

    iteraciones: list[Iteracion] = []

    for i in range(1, max_iter + 1):
        dfxi = exigir_finito(funcion.df(xi), xi, "f'")

        if abs(dfxi) < DERIVADA_MINIMA:
            raise ErrorMetodo(
                f"La derivada se anula en x = {xi:g}  (f'(x) = {dfxi:g}).\n"
                "La recta tangente es horizontal y nunca corta el eje x.\n"
                "Elige otro valor inicial x₀."
            )

        x_siguiente = xi - fxi / dfxi

        if not math.isfinite(x_siguiente):
            raise ErrorMetodo(
                f"El método se disparó en la iteración {i}  (x = {xi:g}).\n"
                "Prueba con un valor inicial más cerca de la raíz."
            )

        f_siguiente = exigir_finito(funcion.f(x_siguiente), x_siguiente)
        ea = error_relativo(x_siguiente, xi)

        iteraciones.append(
            Iteracion(
                numero=i,
                valor=x_siguiente,
                fx=f_siguiente,
                ea=ea,
                extra={"xi": xi, "fxi": fxi, "dfxi": dfxi},
            )
        )

        if f_siguiente == 0:
            return Resultado(iteraciones, x_siguiente, f_siguiente, RAIZ_EXACTA)
        if ea <= tol_pct:
            return Resultado(iteraciones, x_siguiente, f_siguiente, CONVERGIO)

        xi, fxi = x_siguiente, f_siguiente

    ultima = iteraciones[-1]
    return Resultado(iteraciones, ultima.valor, ultima.fx, MAX_ITERACIONES)


def ejecutar(funcion, parametros: dict, tol_pct: float, max_iter: int) -> Resultado:
    """Entrada unica que usa la interfaz grafica."""
    x0 = numero(parametros.get("x0"), "x₀")
    return newton_raphson(funcion, x0, tol_pct, max_iter)
