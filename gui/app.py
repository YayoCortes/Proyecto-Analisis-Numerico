"""Ventana principal: une controles, grafica y tabla."""

import tkinter as tk
from tkinter import ttk

from gui import tema
from gui.panel_controles import EJEMPLOS, PanelControles
from gui.panel_grafica import PanelGrafica
from gui.panel_tabla import PanelTabla
from nucleo import parser, validacion
from nucleo.resultado import ErrorMetodo

ANCHO_LATERAL = 340


class Aplicacion(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Métodos Numéricos — Análisis Numérico")

        tema.aplicar(self)

        # El tamano se ajusta a la escala de la pantalla, sin pasarse del
        # espacio disponible (en portatiles pequenos la ventana se reduce).
        ancho = min(tema.px(1220), self.winfo_screenwidth() - tema.px(60))
        alto = min(tema.px(780), self.winfo_screenheight() - tema.px(100))
        self.geometry(f"{ancho}x{alto}")
        self.minsize(tema.px(940), tema.px(620))

        self._ya_calculo = False
        self._construir()
        self._centrar()

    # ------------------------------------------------------------------

    def _construir(self) -> None:
        contenedor = ttk.Frame(
            self, style="TFrame", padding=(tema.px(16), tema.px(14), tema.px(16), tema.px(16))
        )
        contenedor.pack(fill="both", expand=True)
        contenedor.columnconfigure(0, minsize=tema.px(ANCHO_LATERAL))
        contenedor.columnconfigure(1, weight=1)
        contenedor.rowconfigure(1, weight=1)

        self._encabezado(contenedor)

        self.controles = PanelControles(
            contenedor,
            al_calcular=self.calcular,
            al_cambiar_metodo=self._metodo_cambiado,
        )
        self.controles.grid(row=1, column=0, sticky="nsew", padx=(0, tema.px(16)))

        derecha = ttk.PanedWindow(contenedor, orient="vertical")
        derecha.grid(row=1, column=1, sticky="nsew")

        self.grafica = PanelGrafica(derecha)
        self.tabla = PanelTabla(derecha)
        derecha.add(self.grafica, weight=3)
        derecha.add(self.tabla, weight=2)
        self._division = derecha

        # La grafica se lleva algo mas de la mitad; el usuario puede
        # arrastrar la division para darle mas espacio a la tabla.
        self.after(80, self._repartir_espacio)

        # Arranca con el ejemplo por defecto ya resuelto, para no abrir
        # con la pantalla vacia.
        self.after(140, lambda: self.calcular(self.controles.datos()))

        self.bind("<Return>", lambda _e: self.calcular(self.controles.datos()))

    def _encabezado(self, padre) -> None:
        marco = ttk.Frame(padre, style="TFrame")
        marco.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, tema.px(14)))
        marco.columnconfigure(0, weight=1)

        ttk.Label(marco, text="Métodos Numéricos", style="Titulo.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            marco,
            text="Búsqueda de raíces de una función  ·  la función f(x) la escribe el usuario",
            style="ResumenSuave.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(tema.px(2), 0))

        # Ejemplos: aprovecha el espacio libre de la cabecera y queda
        # siempre a la vista, sin ocupar sitio en la columna de controles.
        ttk.Label(marco, text="Ejemplos", style="ResumenSuave.TLabel").grid(
            row=0, column=1, sticky="e", padx=(0, tema.px(8))
        )
        self.combo_ejemplos = ttk.Combobox(
            marco,
            values=[e["titulo"] for e in EJEMPLOS],
            state="readonly",
            font=tema.FUENTE_PEQUENA,
            width=38,
        )
        self.combo_ejemplos.set("Cargar un ejemplo...")
        self.combo_ejemplos.grid(row=1, column=1, sticky="e", padx=(0, tema.px(8)))
        self.combo_ejemplos.bind("<<ComboboxSelected>>", self._cargar_ejemplo)

    def _cargar_ejemplo(self, _evento=None) -> None:
        indice = self.combo_ejemplos.current()
        if indice < 0:
            return
        self.combo_ejemplos.selection_clear()
        self.focus_set()
        self.controles.aplicar_ejemplo(EJEMPLOS[indice])

    def _repartir_espacio(self) -> None:
        alto = self._division.winfo_height()
        if alto > 100:
            self._division.sashpos(0, int(alto * 0.58))

    def _centrar(self) -> None:
        self.update_idletasks()
        ancho, alto = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth() - ancho) // 2
        y = max((self.winfo_screenheight() - alto) // 2 - 20, 0)
        self.geometry(f"+{x}+{y}")

    # ------------------------------------------------------------------
    # Calculo
    # ------------------------------------------------------------------

    def calcular(self, datos: dict) -> None:
        modulo = datos["modulo"]
        funcion = None

        try:
            funcion = parser.compilar(datos["funcion"])
            tolerancia = validacion.numero(datos["tolerancia"], "La tolerancia")
            max_iter = validacion.entero(datos["max_iter"], "El máximo de iteraciones")
            resultado = modulo.ejecutar(funcion, datos["parametros"], tolerancia, max_iter)

        except ErrorMetodo as error:
            # Errores previsibles: se avisa y, si se puede, se dibuja la curva
            # para que se vea por que fallo (por ejemplo, sin cambio de signo).
            self.tabla.limpiar("No se pudo calcular")
            self.controles.mostrar_aviso(str(error))
            self._dibujar_solo_curva(funcion, datos)
            return

        except Exception as error:  # imprevisto: no se cierra la aplicacion
            self.tabla.limpiar("No se pudo calcular")
            self.controles.mostrar_aviso(f"Error inesperado: {error}")
            return

        self._ya_calculo = True
        self.grafica.dibujar(funcion, resultado, modulo)
        self.tabla.mostrar(resultado, modulo)

        if resultado.convergio:
            self.controles.ocultar_mensaje()
        else:
            self.controles.mostrar_aviso(
                f"{resultado.mensaje_estado}.\n"
                "Aumenta el máximo de iteraciones o revisa la tolerancia."
            )

    def _dibujar_solo_curva(self, funcion, datos: dict) -> None:
        """Aunque el metodo falle, mostrar la funcion ayuda a entender por que."""
        if funcion is None:
            self.grafica.mensaje_inicial()
            return

        parametros = datos["parametros"]
        try:
            if "a" in parametros and "b" in parametros:
                lo = validacion.numero(parametros["a"], "a")
                hi = validacion.numero(parametros["b"], "b")
                if lo > hi:
                    lo, hi = hi, lo
                margen = (hi - lo) * 0.25 or 1.0
                lo, hi = lo - margen, hi + margen
            elif "x0" in parametros:
                centro = validacion.numero(parametros["x0"], "x₀")
                lo, hi = centro - 5, centro + 5
            else:
                lo, hi = -5.0, 5.0
        except ErrorMetodo:
            lo, hi = -5.0, 5.0

        self.grafica.dibujar_curva(funcion, lo, hi)

    def _metodo_cambiado(self) -> None:
        """Al cambiar de metodo se recalcula solo, conservando la misma f(x)."""
        if self._ya_calculo:
            self.calcular(self.controles.datos())


def iniciar() -> None:
    tema.activar_dpi()  # antes de crear la ventana, si no no tiene efecto
    Aplicacion().mainloop()
