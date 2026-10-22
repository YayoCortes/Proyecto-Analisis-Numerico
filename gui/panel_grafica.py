"""Panel de la grafica: matplotlib embebido dentro de la ventana.

No se usa pyplot a proposito: al incrustar la figura en Tkinter se trabaja
directamente con Figure y FigureCanvasTkAgg, asi la grafica vive dentro de
la aplicacion y no abre una ventana aparte que bloquea el programa.

El fondo imita papel milimetrado: una rejilla fina en cada subdivision y
otra mas marcada en cada valor de los ejes. La respuesta va en rojo.
"""

import tkinter as tk
from tkinter import ttk

import numpy as np
from matplotlib import font_manager, rcParams
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk,
)
from matplotlib.figure import Figure
from matplotlib.ticker import AutoMinorLocator, MaxNLocator

from gui import tema

PUNTOS_CURVA = 800
MARGEN = 0.25          # 25 % de aire a cada lado del intervalo
MARGEN_INTEGRAL = 0.12
MAX_TANGENTES = 6      # rectas tangentes dibujadas en Newton-Raphson
MAX_PARABOLAS = 3      # parabolas dibujadas en Muller
MAX_PUNTOS_MARCADOS = 60  # en integracion, con mas puntos se tapa la curva
LARGO_TITULO = 60


def _fuentes() -> list[str]:
    """Bahnschrift como en el resto de la ventana; DejaVu Sans (incluida en
    matplotlib) pone los simbolos que le falten, como los subindices."""
    instaladas = {f.name for f in font_manager.fontManager.ttflist}
    return [f for f in ("Bahnschrift", "Segoe UI") if f in instaladas] + ["DejaVu Sans"]


rcParams["font.family"] = _fuentes()


class PanelGrafica(ttk.Frame):
    def __init__(self, padre):
        super().__init__(padre, style="Hoja.TFrame")

        # El dpi sigue la escala de la pantalla para que la grafica se vea
        # nitida y del mismo tamano que el resto de la interfaz.
        self.figura = Figure(
            figsize=(6.4, 3.0), dpi=round(100 * tema.ESCALA), facecolor=tema.HOJA
        )
        self.ejes = self.figura.add_subplot(111)

        self.lienzo = FigureCanvasTkAgg(self.figura, master=self)
        self.lienzo.get_tk_widget().configure(background=tema.HOJA, highlightthickness=0)

        # La barra se coloca antes que el lienzo: asi tiene su espacio
        # reservado y el lienzo se queda con el resto.
        barra_marco = tk.Frame(self, background=tema.HOJA)
        barra_marco.pack(side="bottom", fill="x")
        self.lienzo.get_tk_widget().pack(side="top", fill="both", expand=True)

        self.barra = NavigationToolbar2Tk(self.lienzo, barra_marco, pack_toolbar=False)
        self.barra.configure(background=tema.HOJA)
        for hijo in self.barra.winfo_children():
            try:
                hijo.configure(background=tema.HOJA)
            except tk.TclError:
                pass
        self.barra.update()
        self.barra.pack(side="left", padx=tema.px(6), pady=(0, tema.px(4)))

        # Lo ultimo que se dibujo, para poder resaltar una fila de la tabla
        self._resultado = None
        self._modulo = None
        self._resaltado: list = []

        self.mensaje_inicial()

    # ------------------------------------------------------------------
    # Estados de la grafica
    # ------------------------------------------------------------------

    def mensaje_inicial(self) -> None:
        # Lienzo completamente limpio: sin ejes, sin rejilla, solo el aviso
        self._olvidar()
        self.ejes.clear()
        self.ejes.set_facecolor(tema.HOJA)
        self.ejes.set_xticks([])
        self.ejes.set_yticks([])
        for lado in self.ejes.spines.values():
            lado.set_visible(False)
        self.ejes.text(
            0.5,
            0.5,
            "Elige un método, escribe f(x) y presiona Calcular",
            ha="center",
            va="center",
            color=tema.GRAFITO,
            fontsize=11,
            transform=self.ejes.transAxes,
        )
        self.figura.tight_layout()
        self.lienzo.draw_idle()

    def dibujar_curva(self, funcion, lo: float, hi: float, marcas=()) -> None:
        """Solo la curva, sin resultado (util cuando el metodo no pudo correr).

        marcas: pares (x, nombre) que se senalan con una linea, por ejemplo
        a y b, para ver donde quedo el intervalo respecto a la curva.
        """
        self._preparar_ejes()
        ys = self._curva(funcion, lo, hi)
        for valor, nombre in marcas:
            self.ejes.axvline(valor, color=tema.PASOS, linewidth=1, linestyle="--", zorder=2)
            self.ejes.annotate(
                f"{nombre} = {valor:g}", xy=(valor, 0), xytext=(5, 8),
                textcoords="offset points", fontsize=8.5, color=tema.GRAFITO,
            )
        self._titulo("Gráfica de f(x)", funcion)
        self._limites_y(ys)
        self._leyenda()
        self.lienzo.draw_idle()

    def dibujar(self, funcion, resultado, modulo, titulo: str = "") -> None:
        """Grafica completa segun el metodo: curva, construccion y respuesta."""
        self._preparar_ejes()
        self._resultado = resultado
        self._modulo = modulo

        if modulo.GRAFICA == "area":
            ys = self._area(funcion, resultado)
        else:
            lo, hi = self._rango(modulo, resultado)
            ys = self._curva(funcion, lo, hi)

            if modulo.GRAFICA == "intervalo":
                self._intervalo_inicial(resultado)
            elif modulo.GRAFICA == "tangentes":
                self._tangentes(resultado, lo, hi)
            elif modulo.GRAFICA == "parabolas":
                self._parabolas(resultado, lo, hi)

            self._pasos(resultado)
            self._raiz(resultado)

        self._titulo(titulo or modulo.NOMBRE, funcion)
        self._limites_y(ys)
        self._leyenda()
        # Lo que se agregue al resaltar una fila no debe mover la vista
        self.ejes.set_autoscale_on(False)
        self.lienzo.draw_idle()

    # ------------------------------------------------------------------
    # Piezas del dibujo
    # ------------------------------------------------------------------

    def _olvidar(self) -> None:
        """ejes.clear() borra los resaltados: se olvidan aqui tambien."""
        self._resultado = None
        self._modulo = None
        self._resaltado = []

    def _preparar_ejes(self) -> None:
        self._olvidar()
        self.ejes.clear()
        self.ejes.set_facecolor(tema.HOJA)

        # La figura es baja: sin esto matplotlib deja muy pocas marcas
        self.ejes.xaxis.set_major_locator(MaxNLocator(nbins=8, steps=[1, 2, 2.5, 5, 10]))
        self.ejes.yaxis.set_major_locator(MaxNLocator(nbins=6, steps=[1, 2, 2.5, 5, 10]))
        self.ejes.xaxis.set_minor_locator(AutoMinorLocator(5))
        self.ejes.yaxis.set_minor_locator(AutoMinorLocator(5))

        # Papel milimetrado
        self.ejes.grid(True, which="minor", color=tema.MILIMETRO, linewidth=0.6)
        self.ejes.grid(True, which="major", color=tema.CENTIMETRO, linewidth=0.9)
        self.ejes.set_axisbelow(True)

        self.ejes.axhline(0, color=tema.EJES, linewidth=1.0, zorder=2)  # eje x
        self.ejes.axvline(0, color=tema.EJES, linewidth=1.0, zorder=2)  # eje y
        for lado in self.ejes.spines.values():
            lado.set_color(tema.CENTIMETRO)
        self.ejes.tick_params(which="both", colors=tema.GRAFITO, labelsize=9)
        self.ejes.tick_params(which="minor", length=0)

    def _curva(self, funcion, lo: float, hi: float) -> np.ndarray:
        xs = np.linspace(lo, hi, PUNTOS_CURVA)
        ys = funcion.f_array(xs)
        self.ejes.plot(xs, ys, color=tema.CURVA, linewidth=2, label="f(x)", zorder=4)
        self.ejes.set_xlim(lo, hi)
        return ys

    def _intervalo_inicial(self, resultado) -> None:
        extra = resultado.iteraciones[0].extra
        a, b = extra.get("a"), extra.get("b")
        if a is None or b is None:
            return
        self.ejes.axvspan(a, b, color=tema.TINTA_AZUL, alpha=0.05, zorder=1)
        # Cada rotulo va del lado de adentro de su linea, sin taparla
        for valor, nombre, lado in ((a, "a", 1), (b, "b", -1)):
            self.ejes.axvline(
                valor, color=tema.PASOS, linewidth=1, linestyle="--", alpha=0.8, zorder=2
            )
            self.ejes.annotate(
                f"{nombre} = {valor:g}",
                xy=(valor, 0),
                xytext=(5 * lado, 8),
                textcoords="offset points",
                ha="left" if lado > 0 else "right",
                fontsize=8.5,
                color=tema.GRAFITO,
            )

    def _tangentes(self, resultado, lo: float, hi: float) -> None:
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
                zorder=5,
                label=None if etiquetado else "tangentes",
            )
            self.ejes.plot(
                [xi, xi], [0.0, fxi],
                color=tema.TANGENTE, linewidth=0.8, linestyle=":", alpha=0.7, zorder=5,
            )
            self.ejes.plot(
                xi, fxi, "o", color=tema.TANGENTE, markersize=4, alpha=0.9, zorder=5
            )
            etiquetado = True

    @staticmethod
    def _parabola(extra: dict, xs: np.ndarray) -> np.ndarray:
        """p(x) = a(x - x2)^2 + b(x - x2) + c, la parabola de Muller."""
        d = xs - extra["x2"]
        return extra["a"] * d * d + extra["b"] * d + extra["c"]

    def _parabolas(self, resultado, lo: float, hi: float) -> None:
        """Parabolas por los tres puntos: la idea del metodo de Muller."""
        xs = np.linspace(lo, hi, PUNTOS_CURVA)
        opacidades = (0.95, 0.6, 0.38)
        for k, iteracion in enumerate(resultado.iteraciones[:MAX_PARABOLAS]):
            self.ejes.plot(
                xs,
                self._parabola(iteracion.extra, xs),
                color=tema.TANGENTE,
                linewidth=1.4,
                linestyle="--",
                alpha=opacidades[k],
                zorder=5,
                label="parábolas" if k == 0 else None,
            )

        # Los tres puntos iniciales, huecos para distinguirlos de los pasos
        primera = resultado.iteraciones[0].extra
        for clave, nombre in (("0", "x₀"), ("1", "x₁"), ("2", "x₂")):
            x, y = primera["x" + clave], primera["f" + clave]
            self.ejes.plot(
                x, y, "o", markerfacecolor=tema.HOJA, markeredgecolor=tema.TANGENTE,
                markeredgewidth=1.6, markersize=6, zorder=6,
            )
            self.ejes.annotate(
                nombre, xy=(x, y), xytext=(6, 6), textcoords="offset points",
                fontsize=9, color=tema.TANGENTE,
            )

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
                zorder=6,
                label="aproximaciones" if i == 0 else None,
            )

    def _raiz(self, resultado) -> None:
        # Un punto encerrado en un circulo rojo, como se marca la respuesta
        self.ejes.plot(
            resultado.raiz, 0, "o", color=tema.RAIZ, markersize=5, zorder=7,
        )
        self.ejes.plot(
            resultado.raiz,
            0,
            "o",
            markerfacecolor="none",
            markeredgecolor=tema.RAIZ,
            markeredgewidth=1.8,
            markersize=14,
            zorder=7,
            label=(
                f"raíz ≈ {resultado.raiz:.6f}"
                if resultado.convergio
                else f"última aproximación {resultado.raiz:.6f}"
            ),
        )
        self.ejes.annotate(
            f"{resultado.raiz:.6f}",
            xy=(resultado.raiz, 0),
            xytext=(0, -20),
            textcoords="offset points",
            ha="center",
            fontsize=9,
            color=tema.RAIZ,
        )

    def _area(self, funcion, resultado) -> np.ndarray:
        """Area que suma la regla elegida, rayada como un ejercicio a mano."""
        lo, hi = sorted((resultado.a, resultado.b))
        margen = (hi - lo) * MARGEN_INTEGRAL
        ys = self._curva(funcion, lo - margen, hi + margen)

        xs_puntos = np.array([it.valor for it in resultado.iteraciones])
        ys_puntos = np.array([it.fx for it in resultado.iteraciones])

        if resultado.regla == "simpson":
            xs_borde, ys_borde = self._tramos_simpson(xs_puntos, ys_puntos)
            nombre_borde = "parábolas"
        else:
            xs_borde, ys_borde = xs_puntos, ys_puntos
            nombre_borde = "trapecios"

        self.ejes.fill_between(
            xs_borde,
            ys_borde,
            0,
            facecolor=(*_rgb(tema.ROJO), 0.07),
            edgecolor=(*_rgb(tema.ROJO), 0.45),  # color del rayado
            hatch="////",
            linewidth=0,
            zorder=1,
            label=f"I ≈ {resultado.integral:.6f}",
        )
        self.ejes.plot(
            xs_borde, ys_borde, color=tema.TANGENTE, linewidth=1.3,
            linestyle="--", zorder=3, label=nombre_borde,
        )

        if len(xs_puntos) <= MAX_PUNTOS_MARCADOS:
            self.ejes.vlines(
                xs_puntos, 0, ys_puntos, colors=tema.TANGENTE, linewidth=0.9, alpha=0.75, zorder=3
            )
            self.ejes.plot(
                xs_puntos, ys_puntos, "o", color=tema.TANGENTE, markersize=4, zorder=5,
            )
        return ys

    @staticmethod
    def _tramos_simpson(xs: np.ndarray, ys: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Une cada tres puntos con su parabola (forma de Lagrange)."""
        partes_x, partes_y = [], []
        for k in range(0, len(xs) - 2, 2):
            x0, x1, x2 = xs[k:k + 3]
            y0, y1, y2 = ys[k:k + 3]
            t = np.linspace(x0, x2, 30)
            p = (
                y0 * (t - x1) * (t - x2) / ((x0 - x1) * (x0 - x2))
                + y1 * (t - x0) * (t - x2) / ((x1 - x0) * (x1 - x2))
                + y2 * (t - x0) * (t - x1) / ((x2 - x0) * (x2 - x1))
            )
            # El primer punto de cada tramo repite el ultimo del anterior
            inicio = 0 if k == 0 else 1
            partes_x.append(t[inicio:])
            partes_y.append(p[inicio:])
        return np.concatenate(partes_x), np.concatenate(partes_y)

    def _titulo(self, texto: str, funcion) -> None:
        expresion = f"f(x) = {funcion.texto_f}"
        if len(expresion) > LARGO_TITULO:
            expresion = expresion[: LARGO_TITULO - 1] + "…"
        self.ejes.set_title(texto, color=tema.TINTA, fontsize=11, pad=12, loc="left")
        self.ejes.set_title(expresion, color=tema.GRAFITO, fontsize=9.5, pad=12, loc="right")
        self.ejes.set_xlabel("x", color=tema.GRAFITO, fontsize=9)
        self.ejes.set_ylabel("f(x)", color=tema.GRAFITO, fontsize=9)
        self.figura.tight_layout()

    def _leyenda(self) -> None:
        manejadores, etiquetas = self.ejes.get_legend_handles_labels()
        if not manejadores:
            return
        leyenda = self.ejes.legend(
            loc="best", fontsize=8.5, frameon=True, framealpha=0.94, borderpad=0.6
        )
        leyenda.get_frame().set_facecolor(tema.HOJA)
        leyenda.get_frame().set_edgecolor(tema.LINEA)
        leyenda.get_frame().set_linewidth(0.8)
        for texto in leyenda.get_texts():
            texto.set_color(tema.TINTA)

    # ------------------------------------------------------------------
    # Resaltar la fila elegida en la tabla
    # ------------------------------------------------------------------

    def resaltar(self, indice: int | None) -> None:
        """Dibuja encima la construccion de una sola iteracion (o punto)."""
        for artista in self._resaltado:
            artista.remove()
        self._resaltado = []

        if (
            indice is None
            or self._resultado is None
            or not 0 <= indice < len(self._resultado.iteraciones)
        ):
            self.lienzo.draw_idle()
            return

        it = self._resultado.iteraciones[indice]
        tipo = self._modulo.GRAFICA
        nuevos = []

        if tipo == "intervalo":
            a, b = it.extra["a"], it.extra["b"]
            nuevos.append(self.ejes.axvspan(a, b, color=tema.TINTA_AZUL, alpha=0.10, zorder=1))
            nuevos += self.ejes.plot(
                [it.valor, it.valor], [0, it.fx], color=tema.RESALTE, linewidth=1, linestyle=":", zorder=8
            )
            nota = f"Iteración {it.numero}\n[a, b] = [{a:.6g}, {b:.6g}]\nc = {it.valor:.8g}"

        elif tipo == "tangentes":
            xi, fxi = it.extra["xi"], it.extra["fxi"]
            nuevos += self.ejes.plot([xi, it.valor], [fxi, 0], color=tema.RESALTE, linewidth=2, zorder=8)
            nuevos += self.ejes.plot([xi, xi], [0, fxi], color=tema.RESALTE, linewidth=1, linestyle=":", zorder=8)
            nuevos += self.ejes.plot(xi, fxi, "o", color=tema.RESALTE, markersize=5, zorder=8)
            nota = f"Iteración {it.numero}\nxᵢ = {xi:.8g}\nxᵢ₊₁ = {it.valor:.8g}"

        elif tipo == "parabolas":
            xs = np.linspace(*self.ejes.get_xlim(), PUNTOS_CURVA)
            nuevos += self.ejes.plot(
                xs, self._parabola(it.extra, xs), color=tema.RESALTE, linewidth=1.8, zorder=8
            )
            for clave in ("0", "1", "2"):
                nuevos += self.ejes.plot(
                    it.extra["x" + clave], it.extra["f" + clave], "o",
                    markerfacecolor=tema.HOJA, markeredgecolor=tema.RESALTE,
                    markeredgewidth=1.6, markersize=6, zorder=9,
                )
            nota = f"Iteración {it.numero}\nx₃ = {it.valor:.8g}\nea = {it.ea:.4g} %"

        else:  # area
            nuevos += self.ejes.plot(
                [it.valor, it.valor], [0, it.fx], color=tema.RESALTE, linewidth=1.8, zorder=8
            )
            nota = (
                f"Punto i = {it.numero}\nx = {it.valor:.6g}\n"
                f"f(x) = {it.fx:.6g}\ncoeficiente {it.extra['coef']}"
            )

        nuevos += self.ejes.plot(
            it.valor, it.fx, "o", markerfacecolor=tema.HOJA, markeredgecolor=tema.RESALTE,
            markeredgewidth=2, markersize=8, zorder=10,
        )
        nuevos.append(self._nota(it.valor, it.fx, nota))

        self._resaltado = nuevos
        self.lienzo.draw_idle()

    def _nota(self, x: float, y: float, texto: str):
        """Recuadro junto al punto, del lado donde hay espacio."""
        x_rel, y_rel = self.ejes.transLimits.transform((x, y))
        derecha = x_rel > 0.62
        arriba = y_rel > 0.55
        return self.ejes.annotate(
            texto,
            xy=(x, y),
            xytext=(-16 if derecha else 16, -16 if arriba else 16),
            textcoords="offset points",
            ha="right" if derecha else "left",
            va="top" if arriba else "bottom",
            fontsize=8.5,
            color=tema.TINTA,
            linespacing=1.4,
            bbox={"boxstyle": "round,pad=0.5", "facecolor": tema.HOJA, "edgecolor": tema.LINEA, "linewidth": 0.8},
            arrowprops={"arrowstyle": "-", "color": tema.GRAFITO, "linewidth": 0.8},
            zorder=11,
        )

    # ------------------------------------------------------------------
    # Rangos
    # ------------------------------------------------------------------

    def _rango(self, modulo, resultado) -> tuple[float, float]:
        """Rango en x que hay que mostrar para que se vea lo importante."""
        primera = resultado.iteraciones[0].extra
        if modulo.GRAFICA == "intervalo":
            valores = [primera.get("a", resultado.raiz), primera.get("b", resultado.raiz)]
        else:
            # Metodos abiertos: el rango debe incluir los puntos iniciales Y
            # la raiz. (El script original de Newton graficaba de 0 a 2 y la
            # raiz quedaba fuera.)
            if modulo.GRAFICA == "parabolas":
                iniciales = [primera["x0"], primera["x1"], primera["x2"]]
            else:
                iniciales = [primera.get("xi", resultado.raiz)]
            valores = iniciales + [resultado.raiz]

            # Se suman los pasos intermedios, salvo los que se van muy lejos
            base = abs(max(valores) - min(valores)) or 1.0
            centro = (max(valores) + min(valores)) / 2
            for iteracion in resultado.iteraciones:
                if abs(iteracion.valor - centro) <= 2 * base:
                    valores.append(iteracion.valor)

        lo, hi = min(valores), max(valores)
        if hi - lo < 1e-9:
            lo, hi = lo - 1.0, hi + 1.0

        if modulo.GRAFICA != "intervalo":
            # Si los puntos iniciales caen muy cerca de la raiz, ese tramo es
            # diminuto y la curva se veria como una recta. Se abre la vista
            # para que se note la forma de la funcion.
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

    def _limites_y(self, ys: np.ndarray) -> None:
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


def _rgb(color: str) -> tuple[float, float, float]:
    """'#C0392B' -> (0.75, 0.22, 0.17), para poder darle transparencia."""
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) / 255 for i in (0, 2, 4))
