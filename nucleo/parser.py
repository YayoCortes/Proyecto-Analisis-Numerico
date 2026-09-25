"""Convierte el texto que escribe el usuario en una funcion evaluable.

Se usa SymPy en lugar de eval() por dos razones:

1. Seguridad: eval() ejecutaria cualquier codigo escrito en la caja de texto.
2. Permite derivar f(x) automaticamente, asi el usuario solo escribe la
   funcion y el metodo de Newton-Raphson obtiene f'(x) solo.
"""

import re

import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)

from nucleo.resultado import ErrorMetodo


# La variable siempre es x
X = sp.Symbol("x", real=True)

# Transformaciones que hacen tolerante la escritura:
#   convert_xor                      ->  x^2   se entiende como x**2
#   implicit_multiplication_application ->  2x  se entiende como 2*x
TRANSFORMACIONES = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)

# Nombres que el usuario puede escribir, incluidos algunos en espanol
NOMBRES = {
    "x": X,
    "sen": sp.sin,
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "asen": sp.asin,
    "asin": sp.asin,
    "acos": sp.acos,
    "atan": sp.atan,
    "senh": sp.sinh,
    "sinh": sp.sinh,
    "cosh": sp.cosh,
    "tanh": sp.tanh,
    "exp": sp.exp,
    "ln": sp.log,
    "log": sp.log,
    "log10": lambda arg: sp.log(arg, 10),
    "sqrt": sp.sqrt,
    "raiz": sp.sqrt,
    "abs": sp.Abs,
    "pi": sp.pi,
    "e": sp.E,
}


def _a_texto(expresion) -> str:
    """Texto legible: usa ^ en vez de ** y quita el * de 2*x.

    Queda como se escribe a mano (-0.4x^2 + 2.2x + 4.7) y ademas se puede
    copiar de vuelta a la caja de texto, porque la lectura acepta 2x.
    """
    texto = str(expresion).replace("**", "^")
    return re.sub(r"(\d)\*([a-zA-Z(])", r"\1\2", texto)


class Funcion:
    """Funcion f(x) del usuario, lista para evaluar y para graficar."""

    def __init__(self, texto: str):
        self.texto = texto.strip()
        self.expresion = _parsear(self.texto)
        self.derivada = sp.diff(self.expresion, X)

        # lambdify convierte la expresion simbolica en una funcion rapida.
        # Sirve tanto para un numero suelto como para un arreglo completo.
        self._f = sp.lambdify(X, self.expresion, "numpy")
        self._df = sp.lambdify(X, self.derivada, "numpy")

    # --- texto para mostrar en pantalla -------------------------------

    @property
    def texto_f(self) -> str:
        return _a_texto(self.expresion)

    @property
    def texto_df(self) -> str:
        return _a_texto(self.derivada)

    # --- evaluacion de un solo valor ----------------------------------

    def f(self, valor: float) -> float:
        return _evaluar(self._f, valor)

    def df(self, valor: float) -> float:
        return _evaluar(self._df, valor)

    # --- evaluacion de un arreglo (para la grafica) -------------------

    def f_array(self, valores: np.ndarray) -> np.ndarray:
        return _evaluar_array(self._f, valores)

    def df_array(self, valores: np.ndarray) -> np.ndarray:
        return _evaluar_array(self._df, valores)


def compilar(texto: str) -> Funcion:
    """Punto de entrada: texto del usuario -> objeto Funcion.

    Lanza ErrorMetodo con un mensaje claro si el texto no sirve.
    """
    if not texto or not texto.strip():
        raise ErrorMetodo("Escribe una función f(x).")
    return Funcion(texto)


def _parsear(texto: str):
    """Texto -> expresion de SymPy, validando que solo aparezca la x."""
    try:
        expresion = parse_expr(
            texto,
            local_dict=NOMBRES,
            transformations=TRANSFORMACIONES,
            evaluate=True,
        )
    except Exception:
        raise ErrorMetodo(
            f"No se entiende la función:  {texto}\n"
            "Ejemplos válidos:  -0.4x^2 + 2.2x + 4.7 ,  x^3 - 2x + 1 ,  cos(x) - x"
        )

    # Solo se admite la variable x
    desconocidas = sorted(
        str(s) for s in expresion.free_symbols if str(s) != "x"
    )
    if desconocidas:
        lista = ", ".join(desconocidas)
        raise ErrorMetodo(
            f"La función usa una variable desconocida:  {lista}\n"
            "La única variable permitida es x."
        )

    # Debe poder convertirse a numero al evaluarla
    if not isinstance(expresion, sp.Expr):
        raise ErrorMetodo(f"La expresión no es una función válida: {texto}")

    return expresion


def _evaluar(funcion, valor: float) -> float:
    """Evalua en un punto. Fuera del dominio devuelve nan en vez de romper."""
    try:
        with np.errstate(all="ignore"):
            resultado = funcion(valor)
    except (ValueError, ZeroDivisionError, OverflowError, TypeError):
        return float("nan")

    # Raices de negativos y similares dan un numero complejo:
    # se tratan como fuera del dominio real.
    if isinstance(resultado, complex):
        if abs(resultado.imag) > 1e-12:
            return float("nan")
        resultado = resultado.real

    try:
        return float(resultado)
    except (TypeError, ValueError):
        return float("nan")


def _evaluar_array(funcion, valores: np.ndarray) -> np.ndarray:
    """Evalua un arreglo completo para dibujar la curva."""
    valores = np.asarray(valores, dtype=float)
    try:
        with np.errstate(all="ignore"):
            resultado = funcion(valores)
    except (ValueError, ZeroDivisionError, OverflowError, TypeError):
        # Si falla en bloque, se evalua punto por punto
        return np.array([_evaluar(funcion, v) for v in valores], dtype=float)

    resultado = np.asarray(resultado, dtype=complex if np.iscomplexobj(resultado) else float)

    if np.iscomplexobj(resultado):
        resultado = np.where(np.abs(resultado.imag) > 1e-12, np.nan, resultado.real)

    # Una funcion constante devuelve un escalar: se expande al tamano del arreglo
    if resultado.ndim == 0:
        resultado = np.full_like(valores, float(resultado))

    return resultado.astype(float)
