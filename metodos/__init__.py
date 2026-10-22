"""Registro de metodos numericos disponibles.

Para agregar un metodo nuevo (secante, punto fijo, ...):
  1. crear su archivo aqui con NOMBRE, CLAVE, TIPO, GRAFICA, RESUMEN,
     FORMULA, PARAMETROS, COLUMNAS y ejecutar()
  2. agregarlo a la lista METODOS de abajo

Opcionales:
  USA_TOLERANCIA = False   si no itera (no pide tolerancia ni iteraciones)
  USA_DERIVADA = True      si necesita f'(x) (se muestra al escribir f)
  explicacion(parametros)  si el titulo, resumen o formula dependen de
                           lo que elija el usuario (regla de integracion)

La interfaz grafica se adapta sola: no hay que tocarla.
"""

from metodos import biseccion, falsa_posicion, integracion, muller, newton_raphson

METODOS = [biseccion, falsa_posicion, newton_raphson, muller, integracion]

POR_CLAVE = {m.CLAVE: m for m in METODOS}

# Como se agrupan los botones en la columna de controles
GRUPOS = [
    ("Raíces de ecuaciones", ("cerrado", "abierto")),
    ("Integración numérica", ("integracion",)),
]


def obtener(clave: str):
    """Devuelve el modulo del metodo a partir de su clave."""
    return POR_CLAVE[clave]


def nombres() -> list[str]:
    return [m.NOMBRE for m in METODOS]


def usa_tolerancia(modulo) -> bool:
    return getattr(modulo, "USA_TOLERANCIA", True)


def usa_derivada(modulo) -> bool:
    return getattr(modulo, "USA_DERIVADA", False)


def explicacion(modulo, parametros: dict) -> tuple[str, str, str]:
    """Titulo, resumen y formula que se muestran del metodo."""
    if hasattr(modulo, "explicacion"):
        return modulo.explicacion(parametros)
    return modulo.NOMBRE, modulo.RESUMEN, modulo.FORMULA
