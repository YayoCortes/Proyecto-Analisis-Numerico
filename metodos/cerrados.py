"""Motor comun de los metodos cerrados (biseccion y falsa posicion).

Los dos metodos son identicos salvo por la formula con que calculan el
punto c dentro del intervalo, asi que el bucle vive aqui una sola vez y
cada metodo aporta unicamente su formula.
"""

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


# Los dos metodos piden el mismo par de datos y muestran la misma tabla
PARAMETROS_CERRADOS = [
    Parametro("a", "a  (extremo izquierdo)", "5"),
    Parametro("b", "b  (extremo derecho)", "10"),
]


def columnas_cerradas(nombre_c: str) -> list[Columna]:
    return [
        Columna("numero", "i", 45),
        Columna("a", "a", 130),
        Columna("b", "b", 130),
        Columna("valor", nombre_c, 145),
        Columna("fx", "f(c)", 135),
        Columna("ea", "ea %", 115),
    ]


def resolver(funcion, a, b, tol_pct, max_iter, calcular_c) -> Resultado:
    """Bucle comun: valida el intervalo e itera hasta cumplir la tolerancia.

    calcular_c(a, b, fa, fb) es lo unico que cambia entre un metodo y otro.
    """
    validar_comunes(tol_pct, max_iter)

    if a == b:
        raise ErrorMetodo("El intervalo está vacío: a y b son iguales.")
    if a > b:
        a, b = b, a  # se acepta el intervalo al reves

    fa = exigir_finito(funcion.f(a), a)
    fb = exigir_finito(funcion.f(b), b)

    # Si un extremo ya es la raiz, no hace falta iterar
    if fa == 0:
        return Resultado([Iteracion(1, a, fa, None, {"a": a, "b": b})], a, fa, RAIZ_EXACTA)
    if fb == 0:
        return Resultado([Iteracion(1, b, fb, None, {"a": a, "b": b})], b, fb, RAIZ_EXACTA)

    # Teorema de Bolzano: sin cambio de signo no se garantiza raiz
    if fa * fb > 0:
        raise ErrorMetodo(
            f"No hay cambio de signo en [{a:g}, {b:g}]:\n"
            f"f({a:g}) = {fa:.6g} y f({b:g}) = {fb:.6g} tienen el mismo signo.\n"
            "Elige otro intervalo donde la función cruce el eje x."
        )

    iteraciones: list[Iteracion] = []
    c_anterior = None

    for i in range(1, max_iter + 1):
        c = calcular_c(a, b, fa, fb)
        fc = exigir_finito(funcion.f(c), c)

        # En la primera iteracion no hay valor anterior con que comparar
        ea = None if i == 1 else error_relativo(c, c_anterior)

        iteraciones.append(Iteracion(i, c, fc, ea, {"a": a, "b": b}))

        if fc == 0:
            return Resultado(iteraciones, c, fc, RAIZ_EXACTA)
        if ea is not None and ea <= tol_pct:
            return Resultado(iteraciones, c, fc, CONVERGIO)

        # El subintervalo que conserva el cambio de signo
        if fa * fc < 0:
            b, fb = c, fc
        else:
            a, fa = c, fc

        c_anterior = c

    ultima = iteraciones[-1]
    return Resultado(iteraciones, ultima.valor, ultima.fx, MAX_ITERACIONES)


def leer_intervalo(parametros: dict) -> tuple[float, float]:
    """Convierte los textos de la interfaz en los numeros a y b."""
    a = numero(parametros.get("a"), "a")
    b = numero(parametros.get("b"), "b")
    return a, b
