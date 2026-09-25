"""Panel de la grafica: matplotlib embebido dentro de la ventana.

No se usa pyplot a proposito: al incrustar la figura en Tkinter se trabaja
directamente con Figure y FigureCanvasTkAgg, asi la grafica vive dentro de
la aplicacion y no abre una ventana aparte que bloquea el programa.
"""

import tkinter as tk
from tkinter import ttk

import numpy as np
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk,
)
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

from gui import tema

PUNTOS_CURVA = 800
MARGEN = 0.25          # 25 % de aire a cada lado del intervalo
MAX_TANGENTES = 6      # rectas tangentes dibujadas en Newton-Raphson


class PanelGrafica(ttk.Frame):
    def __init__(self, padre):
        super().__init__(padre, style="Tarjeta.TFrame")

        # El dpi sigue la escala de la pantalla para que la grafica se vea
        # nitida y del mismo tamano que el resto de la interfaz.
        self.figura = Figure(
            figsize=(6.4, 3.0), dpi=round(100 * tema.ESCALA), facecolor=tema.SUPERFICIE
        )
        self.ejes = self.figura.add_subplot(111)

        self.lienzo = FigureCanvasTkAgg(self.figura, master=self)
        self.lienzo.get_tk_widget().configure(background=tema.SUPERFICIE, highlightthickness=0)

        # La barra se coloca antes que el lienzo: asi tiene su espacio
        # reservado y el lienzo se queda con el resto.
        barra_marco = tk.Frame(self, background=tema.SUPERFICIE)
        barra_marco.pack(side="bottom", fill="x")
        self.lienzo.get_tk_widget().pack(side="top", fill="both", expand=True)

        self.barra = NavigationToolbar2Tk(self.lienzo, barra_marco, pack_toolbar=False)
        self.barra.configure(background=tema.SUPERFICIE)
        for hijo in self.barra.winfo_children():
            try:
                hijo.configure(background=tema.SUPERFICIE)
            except tk.TclError:
                pass
        self.barra.update()
        self.barra.pack(side="left", padx=tema.px(6), pady=(0, tema.px(4)))

        self.mensaje_inicial()

    # ------------------------------------------------------------------
    # Estados de la grafica
    # ------------------------------------------------------------------

    def mensaje_inicial(self) -> None:
        # Lienzo completamente limpio: sin ejes, sin rejilla, solo el aviso
        self.ejes.clear()
        self.ejes.set_facecolor(tema.SUPERFICIE)
        self.ejes.set_xticks([])
        self.ejes.set_yticks([])
        for lado in self.ejes.spines.values():
            lado.set_visible(False)
        self.ejes.text(
            0.5,
            0.5,
            "Escribe una función y presiona Calcular",
            ha="center",
            va="center",
            color=tema.TEXTO_SUAVE,
            fontsize=11,
            transform=self.ejes.transAxes,
        )
        self.figura.tight_layout()
        self.lienzo.draw_idle()

    def dibujar_curva(self, funcion, lo: float, hi: float, titulo: str = "") -> None:
        """Solo la curva, sin resultado (util cuando el metodo no pudo correr)."""
        self._preparar_ejes()
        self._curva(funcion, lo, hi)
        self._titulo(titulo or f"f(x) = {funcion.texto_f}")
        self._leyenda()
        self.lienzo.draw_idle()

    def dibujar(self, funcion, resultado, modulo) -> None:
        """Grafica completa: curva, intervalo o tangentes, pasos y raiz."""
        self._preparar_ejes()

        lo, hi = self._rango(modulo, resultado)
        ys = self._curva(funcion, lo, hi)

        if modulo.TIPO == "cerrado":
            self._intervalo_inicial(resultado)
        else:
            self._tangentes(funcion, resultado, lo, hi)

        self._pasos(resultado)
        self._raiz(resultado)

        self._titulo(f"{modulo.NOMBRE} — f(x) = {funcion.texto_f}")
        self._limites_y(ys, resultado)
        self._leyenda()
        self.lienzo.draw_idle()

    # ------------------------------------------------------------------
    # Piezas del dibujo
    # ------------------------------------------------------------------

    def _preparar_ejes(self) -> None:
        self.ejes.clear()
        self.ejes.set_facecolor(tema.SUPERFICIE)
        self.ejes.grid(True, color=tema.REJILLA, linewidth=0.8)
        self.ejes.set_axisbelow(True)
        self.ejes.axhline(0, color=tema.EJES, linewidth=0.9)  # eje x
        self.ejes.axvline(0, color=tema.EJES, linewidth=0.9)  # eje y
        for lado in ("top", "right"):
            self.ejes.spines[lado].set_visible(False)
        for lado in ("left", "bottom"):
            self.ejes.spines[lado].set_color(tema.BORDE)
        self.ejes.tick_params(colors=tema.TEXTO_SUAVE, labelsize=9)

        # La figura es baja: sin esto matplotlib deja muy pocas marcas
        self.ejes.xaxis.set_major_locator(MaxNLocator(nbins=8, steps=[1, 2, 2.5, 5, 10]))
        self.ejes.yaxis.set_major_locator(MaxNLocator(nbins=6, steps=[1, 2, 2.5, 5, 10]))

    def _curva(self, funcion, lo: float, hi: float) -> np.ndarray:
        xs = np.linspace(lo, hi, PUNTOS_CURVA)
        ys = funcion.f_array(xs)
        self.ejes.plot(xs, ys, color=tema.CURVA, linewidth=2, label="f(x)", zorder=3)
        self.ejes.set_xlim(lo, hi)
        return ys

    def _intervalo_inicial(self, resultado) -> None:
        extra = resultado.iteraciones[0].extra
        a, b = extra.get("a"), extra.get("b")
        if a is None or b is None:
            return
        self.ejes.axvspan(a, b, color=tema.ACENTO, alpha=0.06, zorder=1)
        for valor, nombre in ((a, "a"), (b, "b")):
            self.ejes.axvline(
                valor, color=tema.PASOS, linewidth=1, linestyle="--", alpha=0.8, zorder=2
            )
            self.ejes.annotate(
                f"{nombre} = {valor:g}",
                xy=(valor, 0),
                xytext=(0, 8),
                textcoords="offset points",
                ha="center",
                fontsize=8,
                color=tema.TEXTO_SUAVE,
            )

    def _tangentes(self, funcion, resultado, lo: float, hi: float) -> None:
        """Rectas tangentes: es la idea del metodo de Newton en una imagen."""
        etiquetado = False
        for iteracion in resultado.iteraciones[:MAX_TANGENTES]:
            xi = iteracion.extra.get("xi")
            fxi = iteracion.extra.get("fxi")
            siguiente = iteracion.valor
            if xi is None or fxi is None:
                continue
            if not (lo <= xi <= hi):
                continue

            # Van por encima de la curva: cerca de la raiz la tangente casi
            # se confunde con ella y quedaria escondida debajo.
            self.ejes.plot(
                [xi, siguiente],
                [fxi, 0.0],
                color=tema.TANGENTE,
                linewidth=1.4,
                linestyle="--",
                alpha=0.95,
                zorder=4,
                label=None if etiquetado else "tangentes",
            )
            self.ejes.plot(
                [xi, xi], [0.0, fxi],
                color=tema.TANGENTE, linewidth=0.8, linestyle=":", alpha=0.7, zorder=4,
            )
            self.ejes.plot(
                xi, fxi, "o", color=tema.TANGENTE, markersize=4, alpha=0.9, zorder=4
            )
            etiquetado = True

    def _pasos(self, resultado) -> None:
        """Aproximaciones sucesivas, cada vez mas opacas."""
        iteraciones = resultado.iteraciones
        if len(iteraciones) < 2:
            return
        total = len(iteraciones)
        for i, iteracion in enumerate(iteraciones):
            opacidad = 0.25 + 0.6 * (i / max(total - 1, 1))
            self.ejes.plot(
                iteracion.valor,
                iteracion.fx,
                "o",
                color=tema.PASOS,
                markersize=5,
                alpha=opacidad,
                zorder=5,
                label="aproximaciones" if i == 0 else None,
            )

    def _raiz(self, resultado) -> None:
        self.ejes.plot(
            resultado.raiz,
            0,
            "o",
            color=tema.RAIZ,
            markersize=9,
            zorder=6,
            label=f"raíz ≈ {resultado.raiz:.6f}",
        )
        self.ejes.annotate(
            f"{resultado.raiz:.6f}",
            xy=(resultado.raiz, 0),
            xytext=(0, -18),
            textcoords="offset points",
            ha="center",
            fontsize=9,
            color=tema.RAIZ,
        )

    def _titulo(self, texto: str) -> None:
        self.ejes.set_title(texto, color=tema.TEXTO, fontsize=11, pad=12, loc="left")
        self.ejes.set_xlabel("x", color=tema.TEXTO_SUAVE, fontsize=9)
        self.ejes.set_ylabel("f(x)", color=tema.TEXTO_SUAVE, fontsize=9)
        self.figura.tight_layout()

    def _leyenda(self) -> None:
        manejadores, etiquetas = self.ejes.get_legend_handles_labels()
        if not manejadores:
            return
        leyenda = self.ejes.legend(
            loc="best", fontsize=8, frameon=True, framealpha=0.9, borderpad=0.6
        )
        leyenda.get_frame().set_facecolor(tema.SUPERFICIE)
        leyenda.get_frame().set_edgecolor(tema.BORDE)
        for texto in leyenda.get_texts():
            texto.set_color(tema.TEXTO)

    # ------------------------------------------------------------------
    # Rangos
    # ------------------------------------------------------------------

    def _rango(self, modulo, resultado) -> tuple[float, float]:
        """Rango en x que hay que mostrar para que se vea lo importante."""
        if modulo.TIPO == "cerrado":
            extra = resultado.iteraciones[0].extra
            valores = [extra.get("a", resultado.raiz), extra.get("b", resultado.raiz)]
        else:
            # Newton: el rango debe incluir el punto inicial Y la raiz.
            # (El script original graficaba de 0 a 2 y la raiz quedaba fuera.)
            inicial = resultado.iteraciones[0].extra.get("xi", resultado.raiz)
            valores = [inicial, resultado.raiz]

            # Se suman los pasos intermedios, salvo los que se van muy lejos
            base = abs(max(valores) - min(valores)) or 1.0
            centro = (max(valores) + min(valores)) / 2
            for iteracion in resultado.iteraciones:
                if abs(iteracion.valor - centro) <= 2 * base:
                    valores.append(iteracion.valor)

        lo, hi = min(valores), max(valores)
        if hi - lo < 1e-9:
            lo, hi = lo - 1.0, hi + 1.0

        if modulo.TIPO != "cerrado":
            # Si x0 cae muy cerca de la raiz, ese tramo es diminuto y la
            # curva se veria como una recta. Se abre la vista para que se
            # note la forma de la funcion y las tangentes.
            lo, hi = self._ensanchar(lo, hi)

        margen = (hi - lo) * MARGEN
        return lo - margen, hi + margen

    @staticmethod
    def _ensanchar(lo: float, hi: float) -> tuple[float, float]:
        """Abre un poco la vista cuando el tramo es diminuto.

        Se busca el punto medio: lo bastante ancho para ver la curvatura y
        las tangentes, pero sin alejarse tanto que la raiz quede aplastada
        contra el eje. Por eso el ensanchamiento nunca pasa de 4 veces.
        """
        ancho = hi - lo
        escala = max(abs(lo), abs(hi))
        referencia = 0.25 * escala if escala > 0 else 1.0
        minimo = min(4 * ancho, max(ancho, referencia))
        if ancho >= minimo:
            return lo, hi
        centro = (lo + hi) / 2
        return centro - minimo / 2, centro + minimo / 2

    def _limites_y(self, ys: np.ndarray, resultado) -> None:
        """Si la funcion se dispara, se recorta el eje y para que se lea."""
        finitos = ys[np.isfinite(ys)]
        if finitos.size == 0:
            return

        bajo, alto = float(np.min(finitos)), float(np.max(finitos))

        # Con asintotas, los extremos aplastan la curva: se usan percentiles
        if alto - bajo > 1e4:
            bajo = float(np.percentile(finitos, 2))
            alto = float(np.percentile(finitos, 98))

        bajo = min(bajo, 0.0)
        alto = max(alto, 0.0)
        if alto - bajo < 1e-9:
            bajo, alto = bajo - 1.0, alto + 1.0

        respiro = (alto - bajo) * 0.12
        self.ejes.set_ylim(bajo - respiro, alto + respiro)
