"""Columna izquierda (la pizarra): metodo, f(x) y datos.

Los datos se piden en el orden en que se resuelve un ejercicio: elegir el
metodo, escribir la funcion y dar los valores. La parte del medio se puede
desplazar (para pantallas pequenas) y el boton Calcular queda siempre fijo
abajo, a la vista.
"""

import tkinter as tk
from tkinter import ttk

import metodos
from gui import tema
from gui.desplazable import AreaDesplazable
from nucleo import parser
from nucleo.resultado import ErrorMetodo

# Polinomio de los ejemplos de integracion (Chapra, cap. 21)
POLINOMIO = "0.2 + 25x - 200x^2 + 675x^3 - 900x^4 + 400x^5"

# Ejemplos que llenan todos los campos de un clic.
# Aqui es donde se agregara el problema de aplicacion cuando este definido.
EJEMPLOS = [
    {
        "titulo": "Bisección: -0.4x² + 2.2x + 4.7 en [5, 10]",
        "metodo": "biseccion",
        "funcion": "-0.4x^2 + 2.2x + 4.7",
        "parametros": {"a": "5", "b": "10"},
        "tolerancia": "0.01",
        "max_iter": "100",
    },
    {
        "titulo": "Falsa Posición: -0.4x² + 2.2x + 4.7 en [5, 10]",
        "metodo": "falsa_posicion",
        "funcion": "-0.4x^2 + 2.2x + 4.7",
        "parametros": {"a": "5", "b": "10"},
        "tolerancia": "0.01",
        "max_iter": "100",
    },
    {
        "titulo": "Newton-Raphson: x³ - 2x + 1 desde x₀ = -1.5",
        "metodo": "newton_raphson",
        "funcion": "x^3 - 2x + 1",
        "parametros": {"x0": "-1.5"},
        "tolerancia": "0.5",
        "max_iter": "100",
    },
    {
        "titulo": "Müller: x³ - 13x - 12 con x₀ = 4.5, x₁ = 5.5, x₂ = 5",
        "metodo": "muller",
        "funcion": "x^3 - 13x - 12",
        "parametros": {"m0": "4.5", "m1": "5.5", "m2": "5"},
        "tolerancia": "0.01",
        "max_iter": "100",
    },
    {
        "titulo": "Bisección: cos(x) - x en [0, 1]",
        "metodo": "biseccion",
        "funcion": "cos(x) - x",
        "parametros": {"a": "0", "b": "1"},
        "tolerancia": "0.01",
        "max_iter": "100",
    },
    {
        "titulo": "Trapecio: polinomio de grado 5 de 0 a 0.8, n = 4",
        "metodo": "integracion",
        "funcion": POLINOMIO,
        "parametros": {"regla": "trapecio", "a": "0", "b": "0.8", "n": "4"},
    },
    {
        "titulo": "Simpson 1/3: polinomio de grado 5 de 0 a 0.8, n = 4",
        "metodo": "integracion",
        "funcion": POLINOMIO,
        "parametros": {"regla": "simpson", "a": "0", "b": "0.8", "n": "4"},
    },
    {
        "titulo": "Simpson 1/3: exp(-x²) de 0 a 1, n = 10",
        "metodo": "integracion",
        "funcion": "exp(-x^2)",
        "parametros": {"regla": "simpson", "a": "0", "b": "1", "n": "10"},
    },
]

# Ancho util del texto dentro de la pizarra
ANCHO_TEXTO = 262


class PanelControles(ttk.Frame):
    """Panel lateral con todos los datos de entrada."""

    def __init__(self, padre, al_calcular, al_cambiar_metodo=None):
        super().__init__(padre, style="Pizarra.TFrame")
        self._al_calcular = al_calcular
        self._al_cambiar_metodo = al_cambiar_metodo

        self.var_metodo = tk.StringVar(value=metodos.METODOS[0].CLAVE)
        self.var_funcion = tk.StringVar(value="-0.4x^2 + 2.2x + 4.7")
        self.var_tolerancia = tk.StringVar(value="0.01")
        self.var_max_iter = tk.StringVar(value="100")

        # Se recuerdan los valores aunque se cambie de metodo:
        # a y b los comparten biseccion, falsa posicion e integracion.
        self._vars_parametros: dict[str, tk.StringVar] = {}
        self._barras_metodo: dict[str, tk.Frame] = {}
        self._tarea_lectura = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._construir_marca()

        area = AreaDesplazable(
            self,
            fondo=tema.PIZARRA,
            estilo_interior="Pizarra.TFrame",
            ancho=tema.px(300),
            estilo_barra="Pizarra.Vertical.TScrollbar",
        )
        area.grid(row=1, column=0, sticky="nsew")
        self.cuerpo = ttk.Frame(
            area.interior,
            style="Pizarra.TFrame",
            padding=(tema.px(20), tema.px(2), tema.px(18), tema.px(8)),
        )
        self.cuerpo.pack(fill="both", expand=True)
        self.cuerpo.columnconfigure(0, weight=1)

        self.pie = ttk.Frame(
            self,
            style="Pizarra.TFrame",
            padding=(tema.px(20), tema.px(4), tema.px(20), tema.px(14)),
        )
        self.pie.grid(row=2, column=0, sticky="ew")
        self.pie.columnconfigure(0, weight=1)

        self._construir_cuerpo()
        self._construir_pie()
        self._reconstruir_parametros()

        self.var_metodo.trace_add("write", lambda *_: self._marcar_metodo())
        self.var_funcion.trace_add("write", self._programar_lectura)
        self._actualizar_lectura()

    # ------------------------------------------------------------------
    # Construccion
    # ------------------------------------------------------------------

    def _construir_marca(self) -> None:
        marca = ttk.Frame(
            self,
            style="Pizarra.TFrame",
            padding=(tema.px(20), tema.px(18), tema.px(20), tema.px(2)),
        )
        marca.grid(row=0, column=0, sticky="ew")
        ttk.Label(marca, text="Métodos Numéricos", style="Marca.Pizarra.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            marca, text="Proyecto de Análisis Numérico", style="Suave.Pizarra.TLabel"
        ).grid(row=1, column=0, sticky="w", pady=(tema.px(1), 0))

    def _construir_cuerpo(self) -> None:
        cuerpo = self.cuerpo
        fila = 0

        # --- 1. metodo ---
        self._paso(cuerpo, 1, "Elige el método", fila)
        fila += 1

        lista = ttk.Frame(cuerpo, style="Pizarra.TFrame")
        lista.grid(row=fila, column=0, sticky="ew")
        lista.columnconfigure(1, weight=1)
        fila += 1

        renglon = 0
        for titulo_grupo, tipos in metodos.GRUPOS:
            del_grupo = [m for m in metodos.METODOS if m.TIPO in tipos]
            if not del_grupo:
                continue
            ttk.Label(lista, text=titulo_grupo, style="Grupo.Pizarra.TLabel").grid(
                row=renglon,
                column=0,
                columnspan=2,
                sticky="w",
                pady=(tema.px(6) if renglon else 0, tema.px(2)),
            )
            renglon += 1
            for modulo in del_grupo:
                # Rayita de tiza a la izquierda del metodo elegido
                barra = tk.Frame(lista, width=tema.px(3), background=tema.PIZARRA)
                barra.grid(row=renglon, column=0, sticky="ns", pady=tema.px(1))
                self._barras_metodo[modulo.CLAVE] = barra
                ttk.Radiobutton(
                    lista,
                    text=modulo.NOMBRE,
                    value=modulo.CLAVE,
                    variable=self.var_metodo,
                    style="Metodo.Toolbutton",
                    command=self._cambio_de_metodo,
                    cursor="hand2",
                ).grid(row=renglon, column=1, sticky="ew", pady=tema.px(1))
                renglon += 1

        # --- 2. funcion ---
        self._paso(cuerpo, 2, "Escribe la función f(x)", fila)
        fila += 1

        # La letra de un Entry no la toma del estilo: va en el propio widget
        self.entrada_funcion = ttk.Entry(
            cuerpo, textvariable=self.var_funcion, style="Pizarra.TEntry", font=tema.FUENTE_MONO
        )
        self.entrada_funcion.grid(row=fila, column=0, sticky="ew", pady=(0, tema.px(6)))
        self.entrada_funcion.bind("<Return>", self._enter)
        fila += 1

        ttk.Label(
            cuerpo,
            text="Vale x^2 o x**2, y 2x o 2*x.\nFunciones: sin, cos, tan, exp, ln, sqrt.",
            style="Suave.Pizarra.TLabel",
            justify="left",
        ).grid(row=fila, column=0, sticky="ew", pady=(0, tema.px(6)))
        fila += 1

        # Como entendio el programa lo que se escribio (y f'(x) para Newton)
        self.lbl_lectura = ttk.Label(
            cuerpo,
            text="",
            style="Lectura.Pizarra.TLabel",
            wraplength=tema.px(ANCHO_TEXTO),
            justify="left",
        )
        self.lbl_lectura.grid(row=fila, column=0, sticky="ew")
        fila += 1

        # --- 3. datos ---
        self._paso(cuerpo, 3, "Completa los datos", fila)
        fila += 1

        # Los campos de esta zona cambian segun el metodo elegido
        self.zona_parametros = ttk.Frame(cuerpo, style="Pizarra.TFrame")
        self.zona_parametros.grid(row=fila, column=0, sticky="ew")
        fila += 1

        self.zona_comunes = ttk.Frame(cuerpo, style="Pizarra.TFrame")
        self.zona_comunes.grid(row=fila, column=0, sticky="ew", pady=(tema.px(2), 0))
        self.zona_comunes.columnconfigure(0, weight=1, uniform="comunes")
        self.zona_comunes.columnconfigure(1, weight=1, uniform="comunes")
        self._campo(self.zona_comunes, "Tolerancia (%)", self.var_tolerancia, 0, 0, 2)
        self._campo(self.zona_comunes, "Máx. iteraciones", self.var_max_iter, 0, 1, 2)

    def _construir_pie(self) -> None:
        ttk.Button(
            self.pie,
            text="Calcular",
            style="Calcular.TButton",
            command=self._calcular,
            cursor="hand2",
        ).grid(row=0, column=0, sticky="ew", pady=(tema.px(6), 0))

        ttk.Label(
            self.pie, text="También con la tecla Enter", style="Suave.Pizarra.TLabel"
        ).grid(row=1, column=0, pady=(tema.px(5), 0))

    def _paso(self, padre, numero: int, titulo: str, fila: int) -> None:
        """Encabezado de cada paso, con su numero en un circulo de tiza."""
        marco = ttk.Frame(padre, style="Pizarra.TFrame")
        marco.grid(
            row=fila,
            column=0,
            sticky="w",
            pady=(tema.px(14) if fila else tema.px(8), tema.px(7)),
        )
        lado = tema.px(22)
        circulo = tk.Canvas(
            marco,
            width=lado,
            height=lado,
            background=tema.PIZARRA,
            highlightthickness=0,
            borderwidth=0,
        )
        grosor = max(1, tema.px(1.4))
        circulo.create_oval(
            grosor, grosor, lado - grosor, lado - grosor,
            outline=tema.TIZA_AMARILLA, width=grosor,
        )
        circulo.create_text(
            lado / 2, lado / 2, text=str(numero),
            fill=tema.TIZA_AMARILLA, font=("Bahnschrift SemiBold", 9),
        )
        circulo.grid(row=0, column=0, padx=(0, tema.px(9)))
        ttk.Label(marco, text=titulo, style="Paso.Pizarra.TLabel").grid(
            row=0, column=1, sticky="w"
        )

    def _campo(self, padre, etiqueta, variable, fila, columna, columnas) -> ttk.Entry:
        marco = ttk.Frame(padre, style="Pizarra.TFrame")
        marco.grid(
            row=fila,
            column=columna,
            sticky="ew",
            padx=(0, tema.px(8)) if columna < columnas - 1 else (0, 0),
            pady=(0, tema.px(8)),
        )
        marco.columnconfigure(0, weight=1)

        ttk.Label(marco, text=etiqueta, style="Suave.Pizarra.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, tema.px(3))
        )
        entrada = ttk.Entry(
            marco, textvariable=variable, style="Pizarra.TEntry", width=6, font=tema.FUENTE_MONO
        )
        entrada.grid(row=1, column=0, sticky="ew")
        entrada.bind("<Return>", self._enter)
        return entrada

    def _selector(self, padre, parametro, variable, fila, columnas) -> None:
        """Botones para elegir entre las opciones de un parametro."""
        marco = ttk.Frame(padre, style="Pizarra.TFrame")
        marco.grid(row=fila, column=0, columnspan=columnas, sticky="ew", pady=(0, tema.px(10)))

        ttk.Label(marco, text=parametro.etiqueta, style="Suave.Pizarra.TLabel").grid(
            row=0, column=0, columnspan=len(parametro.opciones), sticky="w", pady=(0, tema.px(3))
        )
        for j, (valor, texto) in enumerate(parametro.opciones):
            marco.columnconfigure(j, weight=1, uniform="opcion")
            ttk.Radiobutton(
                marco,
                text=texto,
                value=valor,
                variable=variable,
                style="Opcion.Toolbutton",
                command=self._cambio_de_opcion,
                cursor="hand2",
            ).grid(row=1, column=j, sticky="ew")

    # ------------------------------------------------------------------
    # Campos que dependen del metodo
    # ------------------------------------------------------------------

    def _variable(self, parametro) -> tk.StringVar:
        if parametro.clave not in self._vars_parametros:
            self._vars_parametros[parametro.clave] = tk.StringVar(value=parametro.valor_inicial)
        return self._vars_parametros[parametro.clave]

    def _reconstruir_parametros(self) -> None:
        """Dibuja los campos que pide el metodo actual (a y b, x0, ...)."""
        for hijo in self.zona_parametros.winfo_children():
            hijo.destroy()

        modulo = self.metodo_actual()
        selectores = [p for p in modulo.PARAMETROS if p.opciones]
        numericos = [p for p in modulo.PARAMETROS if not p.opciones]

        # Tres valores caben en una sola fila; si no, de dos en dos
        columnas = 3 if len(numericos) == 3 else 2
        for c in range(3):
            if c < columnas:
                self.zona_parametros.columnconfigure(c, weight=1, uniform="parametros")
            else:
                self.zona_parametros.columnconfigure(c, weight=0, uniform="")

        fila = 0
        for parametro in selectores:
            self._selector(self.zona_parametros, parametro, self._variable(parametro), fila, columnas)
            fila += 1

        for i, parametro in enumerate(numericos):
            self._campo(
                self.zona_parametros,
                parametro.etiqueta,
                self._variable(parametro),
                fila=fila + i // columnas,
                columna=i % columnas,
                columnas=columnas,
            )

        # Integracion no itera: no pide tolerancia ni maximo de iteraciones
        if metodos.usa_tolerancia(modulo):
            self.zona_comunes.grid()
        else:
            self.zona_comunes.grid_remove()

        self._marcar_metodo()

    def _marcar_metodo(self) -> None:
        elegido = self.var_metodo.get()
        for clave, barra in self._barras_metodo.items():
            barra.configure(background=tema.TIZA_AMARILLA if clave == elegido else tema.PIZARRA)

    def _cambio_de_metodo(self) -> None:
        self._reconstruir_parametros()
        self._actualizar_lectura()
        if self._al_cambiar_metodo:
            self._al_cambiar_metodo()

    def _cambio_de_opcion(self) -> None:
        # Cambiar de regla se trata igual que cambiar de metodo: se recalcula
        if self._al_cambiar_metodo:
            self._al_cambiar_metodo()

    # ------------------------------------------------------------------
    # Lectura de f(x) mientras se escribe
    # ------------------------------------------------------------------

    def _programar_lectura(self, *_) -> None:
        """Revisa f(x) poco despues de que el usuario deja de escribir."""
        if self._tarea_lectura is not None:
            self.after_cancel(self._tarea_lectura)
        self._tarea_lectura = self.after(350, self._actualizar_lectura)

    def _actualizar_lectura(self) -> None:
        self._tarea_lectura = None
        texto = self.var_funcion.get().strip()
        if not texto:
            self.lbl_lectura.configure(
                text="Escribe una función para empezar.",
                foreground=tema.TIZA_SUAVE,
                font=tema.FUENTE_PEQUENA,
            )
            self.entrada_funcion.configure(style="Pizarra.TEntry")
            return
        try:
            funcion = parser.compilar(texto)
        except ErrorMetodo:
            self.lbl_lectura.configure(
                text="No se entiende la función. Revisa los paréntesis y los operadores.",
                foreground=tema.TIZA_ROJA,
                font=tema.FUENTE_PEQUENA,
            )
            self.entrada_funcion.configure(style="Invalida.Pizarra.TEntry")
            return

        lineas = [f"f(x) = {funcion.texto_f}"]
        if metodos.usa_derivada(self.metodo_actual()):
            lineas.append(f"f'(x) = {funcion.texto_df}")
        self.lbl_lectura.configure(
            text="\n".join(lineas), foreground=tema.TIZA_AZUL, font=tema.FUENTE_MONO_PEQUENA
        )
        self.entrada_funcion.configure(style="Pizarra.TEntry")

    # ------------------------------------------------------------------
    # Ejemplos
    # ------------------------------------------------------------------

    def aplicar_ejemplo(self, ejemplo: dict) -> None:
        """Llena todos los campos con un ejemplo y calcula."""
        self.var_metodo.set(ejemplo["metodo"])
        self._reconstruir_parametros()
        self.var_funcion.set(ejemplo["funcion"])
        if "tolerancia" in ejemplo:
            self.var_tolerancia.set(ejemplo["tolerancia"])
        if "max_iter" in ejemplo:
            self.var_max_iter.set(ejemplo["max_iter"])
        for clave, valor in ejemplo["parametros"].items():
            if clave not in self._vars_parametros:
                self._vars_parametros[clave] = tk.StringVar()
            self._vars_parametros[clave].set(valor)

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
                p.clave: self._variable(p).get() for p in modulo.PARAMETROS
            },
            "tolerancia": self.var_tolerancia.get(),
            "max_iter": self.var_max_iter.get(),
        }

    def _calcular(self, _evento=None) -> None:
        # La lectura se refresca ya, sin esperar al temporizador, para que
        # lo que se muestra corresponda siempre a lo que se acaba de calcular.
        if self._tarea_lectura is not None:
            self.after_cancel(self._tarea_lectura)
            self._tarea_lectura = None
        self._actualizar_lectura()
        self._al_calcular(self.datos())

    def _enter(self, _evento=None) -> str:
        # "break" evita que la ventana principal, que tambien escucha Enter,
        # calcule una segunda vez
        self._calcular()
        return "break"
