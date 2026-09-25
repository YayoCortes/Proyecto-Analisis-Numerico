"""Columna izquierda: seleccion de metodo, f(x) y parametros.

La parte de arriba se puede desplazar (para pantallas pequenas) y el
boton Calcular queda siempre fijo abajo, a la vista.
"""

import tkinter as tk
from tkinter import ttk

import metodos
from gui import tema
from gui.desplazable import AreaDesplazable
from nucleo import parser
from nucleo.resultado import ErrorMetodo


# Ejemplos que llenan todos los campos de un clic.
# Aqui es donde se agregara el problema de aplicacion cuando este definido.
EJEMPLOS = [
    {
        "titulo": "Parábola   -0.4x² + 2.2x + 4.7   ·   Bisección",
        "metodo": "biseccion",
        "funcion": "-0.4x^2 + 2.2x + 4.7",
        "parametros": {"a": "5", "b": "10"},
        "tolerancia": "0.01",
        "max_iter": "100",
    },
    {
        "titulo": "Parábola   -0.4x² + 2.2x + 4.7   ·   Falsa Posición",
        "metodo": "falsa_posicion",
        "funcion": "-0.4x^2 + 2.2x + 4.7",
        "parametros": {"a": "5", "b": "10"},
        "tolerancia": "0.01",
        "max_iter": "100",
    },
    {
        "titulo": "Cúbica   x³ - 2x + 1   ·   Newton-Raphson",
        "metodo": "newton_raphson",
        "funcion": "x^3 - 2x + 1",
        "parametros": {"x0": "-1.5"},
        "tolerancia": "0.5",
        "max_iter": "100",
    },
    {
        "titulo": "Trigonométrica   cos(x) - x   ·   Bisección",
        "metodo": "biseccion",
        "funcion": "cos(x) - x",
        "parametros": {"a": "0", "b": "1"},
        "tolerancia": "0.01",
        "max_iter": "100",
    },
]


class PanelControles(ttk.Frame):
    """Panel lateral con todos los datos de entrada."""

    def __init__(self, padre, al_calcular, al_cambiar_metodo=None):
        super().__init__(padre, style="Lateral.TFrame")
        self._al_calcular = al_calcular
        self._al_cambiar_metodo = al_cambiar_metodo

        self.var_metodo = tk.StringVar(value=metodos.METODOS[0].CLAVE)
        self.var_funcion = tk.StringVar(value="-0.4x^2 + 2.2x + 4.7")
        self.var_tolerancia = tk.StringVar(value="0.01")
        self.var_max_iter = tk.StringVar(value="100")

        # Se recuerdan los valores aunque se cambie de metodo:
        # a y b los comparten biseccion y falsa posicion.
        self._vars_parametros: dict[str, tk.StringVar] = {}
        self._tarea_derivada = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        area = AreaDesplazable(
            self,
            fondo=tema.SUPERFICIE,
            estilo_interior="Lateral.TFrame",
            ancho=tema.px(306),
        )
        area.grid(row=0, column=0, sticky="nsew")
        self.cuerpo = ttk.Frame(
            area.interior,
            style="Lateral.TFrame",
            padding=(tema.px(18), tema.px(16), tema.px(18), tema.px(4)),
        )
        self.cuerpo.pack(fill="both", expand=True)
        self.cuerpo.columnconfigure(0, weight=1)

        self.pie = ttk.Frame(
            self,
            style="Lateral.TFrame",
            padding=(tema.px(18), tema.px(4), tema.px(18), tema.px(16)),
        )
        self.pie.grid(row=1, column=0, sticky="ew")
        self.pie.columnconfigure(0, weight=1)

        self._construir_cuerpo()
        self._construir_pie()
        self._reconstruir_parametros()

        self.var_funcion.trace_add("write", self._programar_derivada)
        self._actualizar_derivada()

    # ------------------------------------------------------------------
    # Construccion
    # ------------------------------------------------------------------

    def _construir_cuerpo(self) -> None:
        cuerpo = self.cuerpo
        fila = 0

        # --- metodo ---
        self._seccion(cuerpo, "MÉTODO", fila)
        fila += 1

        contenedor_metodos = ttk.Frame(cuerpo, style="Lateral.TFrame")
        contenedor_metodos.grid(row=fila, column=0, sticky="ew", pady=(0, tema.px(4)))
        contenedor_metodos.columnconfigure(0, weight=1)
        for i, modulo in enumerate(metodos.METODOS):
            ttk.Radiobutton(
                contenedor_metodos,
                text=modulo.NOMBRE,
                value=modulo.CLAVE,
                variable=self.var_metodo,
                style="Segmento.Toolbutton",
                command=self._cambio_de_metodo,
            ).grid(row=i, column=0, sticky="ew", pady=tema.px(1))
        fila += 1

        self.lbl_resumen_metodo = ttk.Label(
            cuerpo, text="", style="Suave.TLabel",
            wraplength=tema.px(270), justify="left",
        )
        self.lbl_resumen_metodo.grid(
            row=fila, column=0, sticky="ew", pady=(tema.px(8), 0)
        )
        fila += 1

        self.lbl_formula = ttk.Label(
            cuerpo, text="", style="Mono.TLabel", wraplength=tema.px(270)
        )
        self.lbl_formula.grid(
            row=fila, column=0, sticky="ew", pady=(tema.px(3), tema.px(12))
        )
        fila += 1

        ttk.Separator(cuerpo).grid(
            row=fila, column=0, sticky="ew", pady=(0, tema.px(12))
        )
        fila += 1

        # --- funcion ---
        self._seccion(cuerpo, "FUNCIÓN   f(x)", fila)
        fila += 1

        entrada_funcion = ttk.Entry(
            cuerpo, textvariable=self.var_funcion, style="Mono.TEntry"
        )
        entrada_funcion.grid(row=fila, column=0, sticky="ew", pady=(0, tema.px(5)))
        entrada_funcion.bind("<Return>", self._calcular)
        fila += 1

        ttk.Label(
            cuerpo,
            text="Se acepta  x^2  o  x**2 ,  2x  o  2*x ,\ny sin, cos, tan, exp, ln, sqrt.",
            style="Suave.TLabel",
            justify="left",
        ).grid(row=fila, column=0, sticky="ew", pady=(0, tema.px(7)))
        fila += 1

        self.lbl_derivada = ttk.Label(
            cuerpo, text="", style="Mono.TLabel", wraplength=tema.px(270)
        )
        self.lbl_derivada.grid(row=fila, column=0, sticky="ew", pady=(0, tema.px(14)))
        fila += 1

        ttk.Separator(cuerpo).grid(
            row=fila, column=0, sticky="ew", pady=(0, tema.px(12))
        )
        fila += 1

        # --- parametros ---
        self._seccion(cuerpo, "PARÁMETROS", fila)
        fila += 1

        # Los campos de esta zona cambian segun el metodo elegido
        self.zona_parametros = ttk.Frame(cuerpo, style="Lateral.TFrame")
        self.zona_parametros.grid(row=fila, column=0, sticky="ew")
        self.zona_parametros.columnconfigure(0, weight=1)
        self.zona_parametros.columnconfigure(1, weight=1)
        fila += 1

        comunes = ttk.Frame(cuerpo, style="Lateral.TFrame")
        comunes.grid(row=fila, column=0, sticky="ew", pady=(tema.px(4), 0))
        comunes.columnconfigure(0, weight=1)
        comunes.columnconfigure(1, weight=1)
        self._campo(comunes, "Tolerancia  ea %", self.var_tolerancia, 0, 0)
        self._campo(comunes, "Máx. iteraciones", self.var_max_iter, 0, 1)

    def _construir_pie(self) -> None:
        ttk.Button(
            self.pie, text="Calcular", style="Acento.TButton", command=self._calcular
        ).grid(row=0, column=0, sticky="ew", pady=(tema.px(10), 0))

        self.marco_mensaje = tk.Frame(self.pie, background=tema.AVISO_SUAVE)
        self.lbl_mensaje = tk.Label(
            self.marco_mensaje,
            text="",
            background=tema.AVISO_SUAVE,
            foreground=tema.AVISO,
            font=tema.FUENTE_PEQUENA,
            justify="left",
            wraplength=tema.px(255),
            anchor="w",
            padx=tema.px(10),
            pady=tema.px(8),
        )
        self.lbl_mensaje.pack(fill="both", expand=True)

    def _seccion(self, padre, titulo: str, fila: int) -> None:
        ttk.Label(padre, text=titulo, style="Seccion.TLabel").grid(
            row=fila, column=0, sticky="w", pady=(0, tema.px(7))
        )

    def _campo(self, padre, etiqueta, variable, fila, columna) -> ttk.Entry:
        marco = ttk.Frame(padre, style="Lateral.TFrame")
        marco.grid(
            row=fila,
            column=columna,
            sticky="ew",
            padx=(0, tema.px(8)) if columna == 0 else (0, 0),
            pady=(0, tema.px(4)),
        )
        marco.columnconfigure(0, weight=1)

        ttk.Label(marco, text=etiqueta, style="Suave.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, tema.px(3))
        )
        entrada = ttk.Entry(marco, textvariable=variable, style="Mono.TEntry", width=8)
        entrada.grid(row=1, column=0, sticky="ew")
        entrada.bind("<Return>", self._calcular)
        return entrada

    # ------------------------------------------------------------------
    # Campos que dependen del metodo
    # ------------------------------------------------------------------

    def _reconstruir_parametros(self) -> None:
        """Dibuja las cajas que pide el metodo actual (a y b, o x0)."""
        for hijo in self.zona_parametros.winfo_children():
            hijo.destroy()

        modulo = self.metodo_actual()
        self.lbl_resumen_metodo.configure(text=modulo.RESUMEN)
        self.lbl_formula.configure(text=modulo.FORMULA)

        for i, parametro in enumerate(modulo.PARAMETROS):
            if parametro.clave not in self._vars_parametros:
                self._vars_parametros[parametro.clave] = tk.StringVar(
                    value=parametro.valor_inicial
                )
            self._campo(
                self.zona_parametros,
                parametro.etiqueta,
                self._vars_parametros[parametro.clave],
                fila=i // 2,
                columna=i % 2,
            )

    def _cambio_de_metodo(self) -> None:
        self._reconstruir_parametros()
        self.ocultar_mensaje()
        if self._al_cambiar_metodo:
            self._al_cambiar_metodo()

    # ------------------------------------------------------------------
    # Derivada en vivo
    # ------------------------------------------------------------------

    def _programar_derivada(self, *_) -> None:
        """Recalcula f'(x) poco despues de que el usuario deja de escribir."""
        if self._tarea_derivada is not None:
            self.after_cancel(self._tarea_derivada)
        self._tarea_derivada = self.after(350, self._actualizar_derivada)

    def _actualizar_derivada(self) -> None:
        self._tarea_derivada = None
        texto = self.var_funcion.get().strip()
        if not texto:
            self.lbl_derivada.configure(text="")
            return
        try:
            funcion = parser.compilar(texto)
        except ErrorMetodo:
            self.lbl_derivada.configure(
                text="f'(x) = ?   (revisa la función)", foreground=tema.TEXTO_SUAVE
            )
            return
        self.lbl_derivada.configure(
            text=f"f'(x) = {funcion.texto_df}", foreground=tema.ACENTO
        )

    # ------------------------------------------------------------------
    # Ejemplos
    # ------------------------------------------------------------------

    def aplicar_ejemplo(self, ejemplo: dict) -> None:
        """Llena todos los campos con un ejemplo y calcula."""
        self.var_metodo.set(ejemplo["metodo"])
        self._reconstruir_parametros()
        self.var_funcion.set(ejemplo["funcion"])
        self.var_tolerancia.set(ejemplo["tolerancia"])
        self.var_max_iter.set(ejemplo["max_iter"])
        for clave, valor in ejemplo["parametros"].items():
            if clave not in self._vars_parametros:
                self._vars_parametros[clave] = tk.StringVar()
            self._vars_parametros[clave].set(valor)

        self.ocultar_mensaje()
        self._actualizar_derivada()
        self._calcular()

    # ------------------------------------------------------------------
    # Datos hacia la aplicacion
    # ------------------------------------------------------------------

    def metodo_actual(self):
        return metodos.obtener(self.var_metodo.get())

    def datos(self) -> dict:
        modulo = self.metodo_actual()
        return {
            "modulo": modulo,
            "funcion": self.var_funcion.get(),
            "parametros": {
                p.clave: self._vars_parametros[p.clave].get()
                for p in modulo.PARAMETROS
            },
            "tolerancia": self.var_tolerancia.get(),
            "max_iter": self.var_max_iter.get(),
        }

    def _calcular(self, _evento=None) -> None:
        # La derivada se refresca ya, sin esperar al temporizador, para que
        # lo que se muestra corresponda siempre a lo que se acaba de calcular.
        if self._tarea_derivada is not None:
            self.after_cancel(self._tarea_derivada)
            self._tarea_derivada = None
        self._actualizar_derivada()
        self._al_calcular(self.datos())

    # ------------------------------------------------------------------
    # Franja de mensajes
    # ------------------------------------------------------------------

    def mostrar_aviso(self, texto: str) -> None:
        self._mensaje(texto, tema.AVISO_SUAVE, tema.AVISO)

    def mostrar_ok(self, texto: str) -> None:
        self._mensaje(texto, tema.OK_SUAVE, tema.OK)

    def _mensaje(self, texto: str, fondo: str, color: str) -> None:
        self.lbl_mensaje.configure(text=texto, background=fondo, foreground=color)
        self.marco_mensaje.configure(background=fondo)
        self.marco_mensaje.grid(row=1, column=0, sticky="ew", pady=(tema.px(10), 0))

    def ocultar_mensaje(self) -> None:
        self.marco_mensaje.grid_remove()
