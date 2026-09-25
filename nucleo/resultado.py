"""Estructuras de datos que comparten todos los metodos numericos.

La idea es que la interfaz grafica no necesite saber que metodo se ejecuto:
todos devuelven un objeto Resultado con la misma forma.
"""

from dataclasses import dataclass, field


# Estados posibles al terminar un metodo
CONVERGIO = "convergio"
MAX_ITERACIONES = "max_iteraciones"
RAIZ_EXACTA = "raiz_exacta"

MENSAJES_ESTADO = {
    CONVERGIO: "convergió, el error alcanzó la tolerancia",
    MAX_ITERACIONES: "se alcanzó el máximo de iteraciones sin converger",
    RAIZ_EXACTA: "se encontró la raíz exacta: f(x) = 0",
}


class ErrorMetodo(Exception):
    """Error previsible de un metodo (mensaje listo para mostrar al usuario)."""


@dataclass
class Parametro:
    """Un campo de entrada propio del metodo (a y b, o x0).

    La interfaz lee esta lista para dibujar las cajas de texto correctas,
    asi agregar un metodo nuevo no obliga a tocar la interfaz.
    """

    clave: str
    etiqueta: str
    valor_inicial: str = ""
    ayuda: str = ""


@dataclass
class Columna:
    """Una columna de la tabla de iteraciones.

    clave: 'numero', 'valor', 'fx', 'ea' o una clave del diccionario extra.
    """

    clave: str
    titulo: str
    ancho: int = 120


@dataclass
class Iteracion:
    """Una fila de la tabla de iteraciones.

    numero : numero de iteracion (empieza en 1)
    valor  : aproximacion de la raiz en esta iteracion
    fx     : f(valor)
    ea     : error relativo porcentual aproximado (None en la primera
             iteracion de biseccion y falsa posicion, donde no hay
             valor anterior con el cual comparar)
    extra  : columnas propias del metodo (a, b para los cerrados;
             derivada y punto anterior para Newton)
    """

    numero: int
    valor: float
    fx: float
    ea: float | None = None
    extra: dict = field(default_factory=dict)


@dataclass
class Resultado:
    """Lo que devuelve cualquier metodo numerico."""

    iteraciones: list[Iteracion]
    raiz: float
    fraiz: float
    estado: str

    @property
    def n_iteraciones(self) -> int:
        return len(self.iteraciones)

    @property
    def mensaje_estado(self) -> str:
        return MENSAJES_ESTADO.get(self.estado, self.estado)

    @property
    def convergio(self) -> bool:
        return self.estado in (CONVERGIO, RAIZ_EXACTA)
