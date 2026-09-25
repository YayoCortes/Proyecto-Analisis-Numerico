"""Registro de metodos numericos disponibles.

Para agregar un metodo nuevo (secante, punto fijo, ...):
  1. crear su archivo aqui con NOMBRE, CLAVE, PARAMETROS, COLUMNAS y ejecutar()
  2. agregarlo a la lista METODOS de abajo

La interfaz grafica se adapta sola: no hay que tocarla.
"""

from metodos import biseccion, falsa_posicion, newton_raphson

METODOS = [biseccion, falsa_posicion, newton_raphson]

POR_CLAVE = {m.CLAVE: m for m in METODOS}


def obtener(clave: str):
    """Devuelve el modulo del metodo a partir de su clave."""
    return POR_CLAVE[clave]


def nombres() -> list[str]:
    return [m.NOMBRE for m in METODOS]
