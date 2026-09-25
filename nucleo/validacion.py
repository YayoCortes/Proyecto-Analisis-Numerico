"""Validaciones compartidas por los metodos y por la interfaz."""

import math

from nucleo.resultado import ErrorMetodo


def numero(texto, etiqueta: str) -> float:
    """Texto de una caja de entrada -> float, con mensaje claro si falla."""
    if isinstance(texto, (int, float)):
        return float(texto)

    texto = str(texto).strip().replace(",", ".")
    if not texto:
        raise ErrorMetodo(f"Falta el valor de {etiqueta}.")
    try:
        valor = float(texto)
    except ValueError:
        raise ErrorMetodo(f"{etiqueta} debe ser un número. Se recibió: {texto}")

    if not math.isfinite(valor):
        raise ErrorMetodo(f"{etiqueta} debe ser un número finito.")
    return valor


def entero(texto, etiqueta: str) -> int:
    valor = numero(texto, etiqueta)
    if valor != int(valor):
        raise ErrorMetodo(f"{etiqueta} debe ser un número entero.")
    return int(valor)


def validar_comunes(tol_pct: float, max_iter: int) -> None:
    """Tolerancia y maximo de iteraciones, iguales para todos los metodos."""
    if tol_pct <= 0:
        raise ErrorMetodo("La tolerancia debe ser mayor que cero.")
    if max_iter < 1:
        raise ErrorMetodo("El máximo de iteraciones debe ser al menos 1.")
    if max_iter > 100000:
        raise ErrorMetodo("El máximo de iteraciones no puede pasar de 100000.")


def exigir_finito(valor: float, punto: float, etiqueta: str = "f") -> float:
    """Corta con un mensaje util si la funcion no se puede evaluar ahi."""
    if not math.isfinite(valor):
        raise ErrorMetodo(
            f"No se puede evaluar {etiqueta}(x) en x = {punto:g}.\n"
            "Revisa que la función esté definida en ese punto "
            "(divisiones entre cero, logaritmos o raíces de negativos)."
        )
    return valor


def error_relativo(actual: float, anterior: float) -> float:
    """Error relativo porcentual aproximado: |(actual - anterior)/actual|*100.

    Si el valor actual es cero se devuelve infinito para no dar por buena
    una convergencia falsa (el codigo original dividia entre cero aqui).
    """
    if actual == 0:
        return math.inf
    return abs((actual - anterior) / actual) * 100.0
