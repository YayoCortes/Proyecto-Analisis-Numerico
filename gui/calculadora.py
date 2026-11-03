"""Modo calculadora: teclas para escribir f(x) sin usar el teclado.

Cada tecla escribe en la misma caja de texto, justo donde esta el cursor,
asi que se puede mezclar con el teclado: tocar sin, escribir x a mano,
cerrar el parentesis con la tecla... Lo que se ve en la caja es lo mismo
que se escribiria a mano (sin( , ^2 , sqrt( ...), para que se aprenda.
"""

import tkinter as tk
from tkinter import ttk
from typing import NamedTuple

from gui import tema


class Tecla(NamedTuple):
    etiqueta: str
    texto: str                              # lo que escribe, o una orden
    estilo: str = "Funcion"                 # Funcion, Numero, Operador, ...
    segunda: tuple[str, str] | None = None  # (etiqueta, texto) con 2nd encendida
    columnas: int = 1


# Ordenes de las teclas que no escriben nada
SEGUNDA = "<2nd>"
BORRAR = "<borrar>"
LIMPIAR = "<limpiar>"
IZQUIERDA = "<izquierda>"
DERECHA = "<derecha>"

# Como en una calculadora cientifica: arriba las funciones, abajo las cifras.
# 2nd cambia las teclas marcadas por su inversa durante una pulsacion.
TECLAS = [
    [
        Tecla("2nd", SEGUNDA, "Segunda"),
        Tecla("sin", "sin(", segunda=("sin⁻¹", "asin(")),
        Tecla("cos", "cos(", segunda=("cos⁻¹", "acos(")),
        Tecla("tan", "tan(", segunda=("tan⁻¹", "atan(")),
        Tecla("ln", "ln(", segunda=("log", "log10(")),
    ],
    [
        Tecla("x²", "^2", segunda=("x³", "^3")),
        Tecla("xʸ", "^"),
        Tecla("√", "sqrt("),
        Tecla("eˣ", "exp(", segunda=("10ˣ", "10^(")),
        Tecla("|x|", "abs("),
    ],
    [
        Tecla("x", "x", "Variable"),
        Tecla("π", "pi"),
        Tecla("e", "e"),
        Tecla("(", "("),
        Tecla(")", ")"),
    ],
    [
        Tecla("7", "7", "Numero"),
        Tecla("8", "8", "Numero"),
        Tecla("9", "9", "Numero"),
        Tecla("÷", "/", "Operador"),
        Tecla("⌫", BORRAR, "Borrar"),
    ],
    [
        Tecla("4", "4", "Numero"),
        Tecla("5", "5", "Numero"),
        Tecla("6", "6", "Numero"),
        Tecla("×", "*", "Operador"),
        Tecla("AC", LIMPIAR, "Borrar"),
    ],
    [
        Tecla("1", "1", "Numero"),
        Tecla("2", "2", "Numero"),
        Tecla("3", "3", "Numero"),
        # La raya – queda centrada como el +; el signo − no existe en
        # Bahnschrift y Windows lo dibuja con otra letra, mas abajo
        Tecla("–", "-", "Operador"),
        Tecla("←", IZQUIERDA, "Cursor"),
    ],
    [
        Tecla("0", "0", "Numero", columnas=2),
        Tecla(".", ".", "Numero"),
        Tecla("+", "+", "Operador"),
        Tecla("→", DERECHA, "Cursor"),
    ],
]

COLUMNAS = 5
FILA_CIFRAS = 3  # un poco de aire entre las funciones y las cifras


class Calculadora(tk.Frame):
    """Teclado en pantalla que escribe en la caja de f(x)."""

    def __init__(self, padre, entrada: ttk.Entry):
        super().__init__(
            padre,
            background=tema.PIZARRA_CAMPO,
            highlightthickness=1,
            highlightbackground=tema.PIZARRA_BORDE,
            highlightcolor=tema.PIZARRA_BORDE,
            padx=tema.px(5),
            pady=tema.px(5),
        )
        self.entrada = entrada
        self.var_segunda = tk.BooleanVar(value=False)
        self._con_segunda: list[tuple[ttk.Button, Tecla]] = []

        # Lo que escribe una tecla se borra entero con ⌫ (sin( de una vez),
        # como en una calculadora. Las mas largas primero: asin( antes que sin(.
        textos = {t.texto for fila in TECLAS for t in fila}
        textos |= {t.segunda[1] for fila in TECLAS for t in fila if t.segunda}
        self._palabras = sorted(
            (t for t in textos if len(t) > 1 and not t.startswith("<")),
            key=len,
            reverse=True,
        )

        self._construir_teclas()

    def _construir_teclas(self) -> None:
        for c in range(COLUMNAS):
            self.columnconfigure(c, weight=1, uniform="tecla")

        hueco = tema.px(2)
        for fila, renglon in enumerate(TECLAS):
            columna = 0
            for tecla in renglon:
                self._boton(tecla).grid(
                    row=fila,
                    column=columna,
                    columnspan=tecla.columnas,
                    sticky="nsew",
                    padx=hueco,
                    pady=(tema.px(8) if fila == FILA_CIFRAS else hueco, hueco),
                )
                columna += tecla.columnas

    def _boton(self, tecla: Tecla):
        # takefocus=False: con Tab se pasa de la caja a los datos, no por
        # las 34 teclas
        if tecla.texto == SEGUNDA:
            return ttk.Checkbutton(
                self,
                text=tecla.etiqueta,
                variable=self.var_segunda,
                style="Segunda.Tecla.Toolbutton",
                command=self._rotular,
                cursor="hand2",
                takefocus=False,
            )
        boton = ttk.Button(
            self,
            text=tecla.etiqueta,
            style=f"{tecla.estilo}.Tecla.TButton",
            command=lambda t=tecla: self._pulsar(t),
            cursor="hand2",
            takefocus=False,
        )
        if tecla.segunda:
            self._con_segunda.append((boton, tecla))
        return boton

    def _rotular(self) -> None:
        """Pone en las teclas la funcion que escriben ahora (con o sin 2nd)."""
        segunda = self.var_segunda.get()
        for boton, tecla in self._con_segunda:
            boton.configure(text=tecla.segunda[0] if segunda else tecla.etiqueta)

    # ------------------------------------------------------------------
    # Lo que hace cada tecla
    # ------------------------------------------------------------------

    def _pulsar(self, tecla: Tecla) -> None:
        texto = tecla.texto
        if tecla.segunda and self.var_segunda.get():
            texto = tecla.segunda[1]

        if texto == BORRAR:
            self._borrar()
        elif texto == LIMPIAR:
            self.entrada.delete(0, "end")
        elif texto == IZQUIERDA:
            self._mover(-1)
        elif texto == DERECHA:
            self._mover(1)
        else:
            self._escribir(texto)

        # Como en las calculadoras, 2nd vale solo para la tecla siguiente
        if self.var_segunda.get():
            self.var_segunda.set(False)
            self._rotular()

        # El cursor queda en la caja, a la vista, para seguir escribiendo
        self.entrada.focus_set()
        self.entrada.tk.call("ttk::entry::See", self.entrada, "insert")

    def _escribir(self, texto: str) -> None:
        e = self.entrada
        if e.selection_present():  # lo seleccionado se reemplaza
            inicio = e.index("sel.first")
            e.delete("sel.first", "sel.last")
            e.icursor(inicio)

        posicion = e.index("insert")
        anterior = e.get()[posicion - 1] if posicion else ""
        # Pegado a una letra, pi o sin( se leerian como otra palabra
        # (xpi, xsin): se separan con un *
        if anterior.isalpha() and texto[0].isalnum():
            texto = "*" + texto
        e.insert(posicion, texto)
        e.icursor(posicion + len(texto))

    def _borrar(self) -> None:
        e = self.entrada
        if e.selection_present():
            e.delete("sel.first", "sel.last")
            return
        posicion = e.index("insert")
        if not posicion:
            return
        antes = e.get()[:posicion]
        largo = next((len(p) for p in self._palabras if antes.endswith(p)), 1)
        e.delete(posicion - largo, posicion)

    def _mover(self, paso: int) -> None:
        e = self.entrada
        e.selection_clear()
        e.icursor(max(0, e.index("insert") + paso))
