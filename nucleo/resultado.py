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

# Version corta para la etiqueta de estado junto al resultado
ETIQUETAS_ESTADO = {
    CONVERGIO: "Convergió",
    MAX_ITERACIONES: "Sin converger",
    RAIZ_EXACTA: "Raíz exacta",
}


class ErrorMetodo(Exception):
    """Error previsible de un metodo (mensaje listo para mostrar al usuario)."""


@dataclass
class Parametro:
    """Un campo de entrada propio del metodo (a y b, o x0).

    La interfaz lee esta lista para dibujar las cajas de texto correctas,
    asi agregar un metodo nuevo no obliga a tocar la interfaz.

    opciones: si tiene elementos, el campo no es una caja de texto sino un
    selector. Cada opcion es (valor, texto), por ejemplo la regla de
    integracion: [("trapecio", "Trapecio"), ("simpson", "Simpson 1/3")].
    """

    clave: str
    etiqueta: str
    valor_inicial: str = ""
    ayuda: str = ""
    opciones: list[tuple[str, str]] = field(default_factory=list)


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


@dataclass
class ResultadoIntegral:
    """Lo que devuelven las reglas de integracion (trapecio y Simpson).

    iteraciones : una fila por cada punto x_i de la particion. Se llama
                  igual que en Resultado para que la tabla las muestre
                  del mismo modo (valor = x_i, fx = f(x_i)).
    exacto      : valor de referencia calculado con alta precision, para
                  obtener el error verdadero. None si no se pudo obtener.
    """

    iteraciones: list[Iteracion]
    integral: float
    regla: str
    a: float
    b: float
    n: int
    h: float
    suma: float
    exacto: float | None = None

    @property
    def error_verdadero(self) -> float | None:
        """Error relativo porcentual verdadero: |(exacto - aprox)/exacto|*100."""
        if self.exacto is None or self.exacto == 0:
            return None
        return abs((self.exacto - self.integral) / self.exacto) * 100.0

    @property
    def convergio(self) -> bool:
        # Las reglas cerradas no iteran: siempre entregan su aproximacion
        return True
