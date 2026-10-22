"""Integracion numerica: regla del Trapecio y regla de Simpson 1/3.

Las dos dividen [a, b] en n segmentos iguales de ancho h = (b - a) / n y
suman f en los puntos x_i = a + i*h, cada uno con su coeficiente:

    Trapecio      I ≈ (h/2) [f(x0) + 2 f(x1) + ... + 2 f(x(n-1)) + f(xn)]
    Simpson 1/3   I ≈ (h/3) [f(x0) + 4 f(x1) + 2 f(x2) + ... + 4 f(x(n-1)) + f(xn)]

El trapecio une los puntos con rectas; Simpson une cada tres puntos con
una parabola, por eso necesita un numero par de segmentos.
"""

from nucleo.resultado import (
    Columna,
    ErrorMetodo,
    Iteracion,
    Parametro,
    ResultadoIntegral,
)
from nucleo.validacion import entero, exigir_finito, numero

NOMBRE = "Trapecio y Simpson"
CLAVE = "integracion"
TIPO = "integracion"
GRAFICA = "area"
USA_TOLERANCIA = False  # no itera: no pide tolerancia ni maximo de iteraciones

TRAPECIO = "trapecio"
SIMPSON = "simpson"

NOMBRES_REGLA = {
    TRAPECIO: "Regla del Trapecio",
    SIMPSON: "Regla de Simpson 1/3",
}

RESUMEN = "Aproxima el área bajo f(x) entre a y b dividiendo el intervalo en n segmentos iguales."
FORMULA = "h = (b - a) / n"

PARAMETROS = [
    Parametro("regla", "Regla", TRAPECIO, opciones=[(TRAPECIO, "Trapecio"), (SIMPSON, "Simpson 1/3")]),
    Parametro("a", "Desde a", "0"),
    Parametro("b", "Hasta b", "0.8"),
    Parametro("n", "Segmentos n", "4"),
]

COLUMNAS = [
    Columna("numero", "i", 45),
    Columna("valor", "xᵢ", 140),
    Columna("fx", "f(xᵢ)", 150),
    Columna("coef", "Coeficiente", 100),
    Columna("producto", "Coeficiente × f(xᵢ)", 170),
]

# Mas segmentos vuelven lenta la tabla sin mejorar lo que se aprende
MAX_SEGMENTOS = 10000


def explicacion(parametros: dict) -> tuple[str, str, str]:
    """Titulo, resumen y formula segun la regla elegida."""
    if parametros.get("regla") == SIMPSON:
        return (
            NOMBRES_REGLA[SIMPSON],
            "Une cada tres puntos seguidos con una parábola y suma el área bajo "
            "esas parábolas. Necesita un número par de segmentos.",
            "I ≈ (h/3) [f(x₀) + 4 Σ f(impares) + 2 Σ f(pares) + f(xₙ)]",
        )
    return (
        NOMBRES_REGLA[TRAPECIO],
        "Une cada par de puntos vecinos con una recta y suma el área de los "
        "n trapecios que quedan bajo la curva.",
        "I ≈ (h/2) [f(x₀) + 2 Σ f(xᵢ) + f(xₙ)]",
    )


def _coeficiente_trapecio(i: int, n: int) -> int:
    return 1 if i in (0, n) else 2


def _coeficiente_simpson(i: int, n: int) -> int:
    if i in (0, n):
        return 1
    return 4 if i % 2 == 1 else 2


def _integrar(funcion, a, b, n, regla, coeficiente, divisor) -> ResultadoIntegral:
    """Parte comun: arma la tabla de puntos y aplica (h/divisor) * suma."""
    if a == b:
        raise ErrorMetodo("Los límites son iguales: el área entre a y b es cero.")
    if n < 1:
        raise ErrorMetodo("El número de segmentos n debe ser al menos 1.")
    if n > MAX_SEGMENTOS:
        raise ErrorMetodo(f"El número de segmentos no puede pasar de {MAX_SEGMENTOS}.")

    h = (b - a) / n
    filas: list[Iteracion] = []
    suma = 0.0

    for i in range(n + 1):
        # El ultimo punto se toma igual a b para no arrastrar redondeo
        xi = b if i == n else a + i * h
        fxi = exigir_finito(funcion.f(xi), xi)
        coef = coeficiente(i, n)
        suma += coef * fxi
        filas.append(Iteracion(i, xi, fxi, None, {"coef": coef, "producto": coef * fxi}))

    return ResultadoIntegral(
        iteraciones=filas,
        integral=h / divisor * suma,
        regla=regla,
        a=a,
        b=b,
        n=n,
        h=h,
        suma=suma,
        exacto=funcion.integral(a, b),
    )


def trapecio(funcion, a, b, n) -> ResultadoIntegral:
    return _integrar(funcion, a, b, n, TRAPECIO, _coeficiente_trapecio, 2)


def simpson(funcion, a, b, n) -> ResultadoIntegral:
    if n % 2 != 0:
        pares = sorted({m for m in (n - 1, n + 1) if m >= 2})
        sugerencia = " o ".join(f"n = {m}" for m in pares)
        raise ErrorMetodo(
            f"La regla de Simpson 1/3 necesita un número par de segmentos (n = {n}).\n"
            f"Prueba con {sugerencia}, o usa la regla del Trapecio."
        )
    return _integrar(funcion, a, b, n, SIMPSON, _coeficiente_simpson, 3)


def ejecutar(funcion, parametros: dict, tol_pct=None, max_iter=None) -> ResultadoIntegral:
    """Entrada unica que usa la interfaz grafica (la tolerancia no se usa)."""
    a = numero(parametros.get("a"), "a")
    b = numero(parametros.get("b"), "b")
    n = entero(parametros.get("n"), "n")
    if parametros.get("regla") == SIMPSON:
        return simpson(funcion, a, b, n)
    return trapecio(funcion, a, b, n)
