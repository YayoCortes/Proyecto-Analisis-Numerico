"""Ventana principal: une controles, grafica y tabla."""

import tkinter as tk
from tkinter import ttk

import metodos
from gui import tema
from gui.panel_controles import EJEMPLOS, PanelControles
from gui.panel_grafica import PanelGrafica
from gui.panel_tabla import PanelTabla
from nucleo import parser, validacion
from nucleo.resultado import ErrorMetodo

TEXTO_EJEMPLOS = "Cargar un ejemplo resuelto"


class Aplicacion(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Métodos Numéricos")

        tema.aplicar(self)

        # El tamano se ajusta a la escala de la pantalla, sin pasarse del
        # espacio disponible (en portatiles pequenos la ventana se reduce).
        ancho = min(tema.px(1240), self.winfo_screenwidth() - tema.px(60))
        alto = min(tema.px(800), self.winfo_screenheight() - tema.px(100))
        self.geometry(f"{ancho}x{alto}")
        self.minsize(tema.px(980), tema.px(640))

        self._ya_calculo = False
        self._construir()
        self._centrar()

    # ------------------------------------------------------------------

    def _construir(self) -> None:
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # La pizarra ocupa toda la altura, pegada al borde izquierdo
        self.controles = PanelControles(
            self,
            al_calcular=self.calcular,
            al_cambiar_metodo=self._metodo_cambiado,
        )
        self.controles.grid(row=0, column=0, sticky="nsw")

        derecha = ttk.Frame(
            self, style="TFrame", padding=(tema.px(24), tema.px(18), tema.px(24), tema.px(14))
        )
        derecha.grid(row=0, column=1, sticky="nsew")
        derecha.columnconfigure(0, weight=1)
        derecha.rowconfigure(1, weight=1)

        self._encabezado(derecha)

        division = ttk.PanedWindow(derecha, orient="vertical")
        division.grid(row=1, column=0, sticky="nsew")

        self.grafica = PanelGrafica(division)
        self.tabla = PanelTabla(division, al_seleccionar=self.grafica.resaltar)
        division.add(self.grafica, weight=3)
        division.add(self.tabla, weight=2)
        self._division = division

        self._actualizar_encabezado(self.controles.datos())

        # La grafica se lleva algo mas de la mitad; el usuario puede
        # arrastrar la division para darle mas espacio a la tabla.
        self.after(80, self._repartir_espacio)

        # Arranca con el ejemplo por defecto ya resuelto, para no abrir
        # con la pantalla vacia.
        self.after(140, lambda: self.calcular(self.controles.datos()))

        self.bind("<Return>", lambda _e: self.calcular(self.controles.datos()))

    def _encabezado(self, padre) -> None:
        """Nombre del metodo elegido, en que consiste y su formula."""
        marco = ttk.Frame(padre, style="TFrame")
        marco.grid(row=0, column=0, sticky="ew", pady=(0, tema.px(14)))
        marco.columnconfigure(0, weight=1)

        self.lbl_titulo = ttk.Label(marco, text="", style="Titulo.TLabel")
        self.lbl_titulo.grid(row=0, column=0, sticky="w")

        self.lbl_explicacion = ttk.Label(
            marco, text="", style="Explicacion.TLabel", justify="left", wraplength=tema.px(600)
        )
        self.lbl_explicacion.grid(row=1, column=0, sticky="w", pady=(tema.px(2), 0))

        self.lbl_formula = ttk.Label(marco, text="", style="Formula.TLabel")
        self.lbl_formula.grid(row=2, column=0, sticky="w", pady=(tema.px(6), 0))

        self.combo_ejemplos = ttk.Combobox(
            marco,
            values=[e["titulo"] for e in EJEMPLOS],
            state="readonly",
            font=tema.FUENTE_PEQUENA,
            width=46,
            cursor="hand2",
        )
        self.combo_ejemplos.set(TEXTO_EJEMPLOS)
        self.combo_ejemplos.grid(row=0, column=1, rowspan=2, sticky="ne", padx=(tema.px(16), 0))
        self.combo_ejemplos.bind("<<ComboboxSelected>>", self._cargar_ejemplo)

        # La explicacion se acomoda al ancho que deja el desplegable
        marco.bind("<Configure>", self._ajustar_explicacion)

    def _ajustar_explicacion(self, evento) -> None:
        libre = evento.width - self.combo_ejemplos.winfo_width() - tema.px(32)
        self.lbl_explicacion.configure(wraplength=max(tema.px(320), libre))

    def _actualizar_encabezado(self, datos: dict) -> str:
        titulo, resumen, formula = metodos.explicacion(datos["modulo"], datos["parametros"])
        self.lbl_titulo.configure(text=titulo)
        self.lbl_explicacion.configure(text=resumen)
        self.lbl_formula.configure(text=formula)
        return titulo

    def _cargar_ejemplo(self, _evento=None) -> None:
        indice = self.combo_ejemplos.current()
        if indice < 0:
            return
        # El desplegable vuelve a su texto: lo cargado se ve en el resto
        self.combo_ejemplos.set(TEXTO_EJEMPLOS)
        self.combo_ejemplos.selection_clear()
        self.focus_set()
        self.controles.aplicar_ejemplo(EJEMPLOS[indice])

    def _repartir_espacio(self) -> None:
        alto = self._division.winfo_height()
        if alto > 100:
            self._division.sashpos(0, int(alto * 0.56))

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
        titulo = self._actualizar_encabezado(datos)
        funcion = None

        try:
            funcion = parser.compilar(datos["funcion"])
            if metodos.usa_tolerancia(modulo):
                tolerancia = validacion.numero(datos["tolerancia"], "La tolerancia")
                max_iter = validacion.entero(datos["max_iter"], "El máximo de iteraciones")
            else:
                tolerancia = max_iter = None
            resultado = modulo.ejecutar(funcion, datos["parametros"], tolerancia, max_iter)

        except ErrorMetodo as error:
            # Errores previsibles: se explica junto a la grafica y, si se
            # puede, se dibuja la curva para que se vea por que fallo (por
            # ejemplo, sin cambio de signo).
            self.tabla.mostrar_error(str(error))
            self._dibujar_solo_curva(funcion, datos)
            return

        except Exception as error:  # imprevisto: no se cierra la aplicacion
            self.tabla.mostrar_error(f"Error inesperado: {error}")
            return

        self._ya_calculo = True
        self.grafica.dibujar(funcion, resultado, modulo, titulo)
        self.tabla.mostrar(resultado, modulo, titulo)

        if not resultado.convergio:
            self.tabla.avisar(
                f"Se hicieron {resultado.n_iteraciones} iteraciones y el error todavía "
                "no baja de la tolerancia. Aumenta el máximo de iteraciones o revisa "
                "la tolerancia; también puede que el método no converja desde ese punto."
            )

    def _dibujar_solo_curva(self, funcion, datos: dict) -> None:
        """Aunque el metodo falle, mostrar la funcion ayuda a entender por que."""
        if funcion is None:
            self.grafica.mensaje_inicial()
            return

        parametros = datos["parametros"]
        intervalo = "a" in parametros and "b" in parametros
        if intervalo:
            claves = ["a", "b"]
        else:
            # Metodos abiertos: alrededor de los valores iniciales
            claves = [p.clave for p in datos["modulo"].PARAMETROS if not p.opciones]

        valores = []
        for clave in claves:
            try:
                valores.append(validacion.numero(parametros[clave], clave))
            except ErrorMetodo:
                pass

        if len(valores) >= 2 and max(valores) > min(valores):
            lo, hi = min(valores), max(valores)
            margen = (hi - lo) * 0.25
            lo, hi = lo - margen, hi + margen
        elif valores:
            lo, hi = valores[0] - 5, valores[0] + 5
        else:
            lo, hi = -5.0, 5.0

        # Con un intervalo se marcan a y b, para ver por que no sirvio
        marcas = list(zip(valores, claves)) if intervalo and len(valores) == 2 else []
        self.grafica.dibujar_curva(funcion, lo, hi, marcas)

    def _metodo_cambiado(self) -> None:
        """Al cambiar de metodo se recalcula solo, conservando la misma f(x)."""
        if self._ya_calculo:
            self.calcular(self.controles.datos())
        else:
            self._actualizar_encabezado(self.controles.datos())


def iniciar() -> None:
    tema.activar_dpi()  # antes de crear la ventana, si no no tiene efecto
    Aplicacion().mainloop()
