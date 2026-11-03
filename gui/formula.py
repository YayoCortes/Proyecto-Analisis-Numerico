"""f(x) dibujada como en un libro: fracciones, raices y exponentes.

SymPy da la formula en LaTeX y matplotlib la convierte en una imagen con
su motor mathtext, que ya viene incluido: no hace falta instalar LaTeX.
Se usa el motor directamente, sin armar una figura, porque asi tarda unos
20 ms y la formula se puede redibujar mientras se escribe.

Aqui estan las dos formas de verla:

- PantallaFuncion: el recuadro de la pizarra, debajo de la caja de texto,
  como la pantalla de una calculadora cientifica.
- VentanaFuncion: una vista ampliada en papel, para leerla con calma o
  proyectarla en clase. Se actualiza sola mientras se escribe.
"""

import tkinter as tk
from tkinter import ttk

import numpy as np
from matplotlib.colors import to_rgb
from matplotlib.font_manager import FontProperties
from matplotlib.mathtext import MathTextParser

from gui import tema

# Letra matematica tipo libro de texto (STIX viene con matplotlib)
LETRA_FORMULA = "stix"

# Tamanos en puntos: el de la izquierda es el normal; si la formula no
# cabe se achica hasta el de la derecha
TAMANO_PANTALLA = (15, 8)
TAMANO_PANTALLA_DERIVADA = (12, 7)
TAMANO_VISTA = (34, 11)
TAMANO_VISTA_DERIVADA = (22, 9)

_MATHTEXT = MathTextParser("agg")


def imagen(texto, tamano, color, fondo, ancho_max=None, tamano_min=8):
    """Dibuja un texto de mathtext y lo devuelve como imagen de Tk.

    Si sale mas ancho que ancho_max se vuelve a dibujar mas pequeno, sin
    bajar de tamano_min. Devuelve None si mathtext no sabe dibujarlo.
    """
    try:
        tinta = _tinta(texto, tamano)
        ancho = tinta.shape[1]
        if ancho_max and ancho > ancho_max and tamano > tamano_min:
            # El ancho no crece justo en proporcion a la letra: algo de margen
            tamano = max(tamano_min, tamano * ancho_max / ancho * 0.97)
            tinta = _tinta(texto, tamano)
    except ValueError:
        return None
    return _foto(tinta, color, fondo)


def _tinta(texto, tamano) -> np.ndarray:
    """Cuanta tinta lleva cada pixel de la formula, de 0 a 255."""
    letra = FontProperties(size=tamano, math_fontfamily=LETRA_FORMULA)
    # Con los dpi de la pantalla, 12 puntos aqui miden lo mismo que una
    # letra de 12 puntos de Tk
    dibujo = _MATHTEXT.parse(texto, dpi=96 * tema.ESCALA, prop=letra)
    return np.pad(np.asarray(dibujo.image), tema.px(2))  # aire para el suavizado


def _foto(tinta, color, fondo) -> tk.PhotoImage:
    """Pinta la tinta del color pedido sobre el fondo.

    Sale en formato PPM, que Tk lee por si solo (sin Pillow).
    """
    peso = tinta[..., None] / 255.0
    rgb = np.array(to_rgb(color)) * 255 * peso + np.array(to_rgb(fondo)) * 255 * (1 - peso)
    alto, ancho = tinta.shape
    cabecera = f"P6 {ancho} {alto} 255\n".encode("ascii")
    return tk.PhotoImage(data=cabecera + rgb.round().astype(np.uint8).tobytes(), format="ppm")


def _renglones(funcion, con_derivada: bool) -> list[tuple[str, str]]:
    """f(x) y, si se pide, f'(x): (para mathtext, en texto plano)."""
    renglones = [(f"$f(x) = {funcion.latex_f}$", f"f(x) = {funcion.texto_f}")]
    if con_derivada:
        # Con \prime la comilla queda pegada a la f, como se escribe a mano
        renglones.append(
            (rf"$f\prime(x) = {funcion.latex_df}$", f"f'(x) = {funcion.texto_df}")
        )
    return renglones


class PantallaFuncion(tk.Frame):
    """Recuadro de la pizarra donde se ve f(x) mientras se escribe."""

    def __init__(self, padre, ancho: int, al_ampliar):
        super().__init__(
            padre,
            background=tema.PIZARRA_CAMPO,
            highlightthickness=1,
            highlightbackground=tema.PIZARRA_BORDE,
            highlightcolor=tema.PIZARRA_BORDE,
        )
        margen = tema.px(10)
        self._ancho = ancho - 2 * margen - 2  # el borde ocupa 1 px a cada lado
        # Tk borra una imagen si nadie guarda una referencia a ella
        self._fotos: list[tk.PhotoImage] = []

        self.columnconfigure(0, weight=1)
        self._lineas = []
        for fila in range(2):
            linea = tk.Label(
                self,
                background=tema.PIZARRA_CAMPO,
                anchor="w",
                justify="left",
                borderwidth=0,
                padx=0,
                pady=0,
            )
            linea.grid(
                row=fila,
                column=0,
                sticky="ew",
                padx=margen,
                pady=(tema.px(10) if fila == 0 else tema.px(4), 0),
            )
            self._lineas.append(linea)

        ttk.Button(
            self,
            text="⤢",
            style="Enlace.Pizarra.TButton",
            command=al_ampliar,
            cursor="hand2",
            takefocus=False,
        ).grid(row=2, column=0, sticky="e", padx=tema.px(3), pady=(tema.px(2), tema.px(3)))

    def mostrar(self, funcion, con_derivada: bool) -> None:
        tamanos = (TAMANO_PANTALLA, TAMANO_PANTALLA_DERIVADA)
        colores = (tema.TIZA, tema.TIZA_AZUL)
        renglones = _renglones(funcion, con_derivada)

        self._fotos = []
        for i, linea in enumerate(self._lineas):
            if i >= len(renglones):
                linea.grid_remove()
                continue
            formula, plano = renglones[i]
            tamano, minimo = tamanos[i]
            foto = imagen(
                formula, tamano, colores[i], tema.PIZARRA_CAMPO,
                ancho_max=self._ancho, tamano_min=minimo,
            )
            if foto is None:  # algo que mathtext no dibuja: se deja en texto
                linea.configure(
                    image="", text=plano, foreground=colores[i],
                    font=tema.FUENTE_MONO_PEQUENA, wraplength=self._ancho,
                )
            else:
                self._fotos.append(foto)
                linea.configure(image=foto, text="")
            linea.grid()

    def avisar(self, texto: str, error: bool = False) -> None:
        """Un mensaje en lugar de la formula (vacia o mal escrita)."""
        self._fotos = []
        self._lineas[0].configure(
            image="",
            text=texto,
            foreground=tema.TIZA_ROJA if error else tema.TIZA_SUAVE,
            font=tema.FUENTE_PEQUENA,
            wraplength=self._ancho,
        )
        self._lineas[0].grid()
        self._lineas[1].grid_remove()


class VentanaFuncion(tk.Toplevel):
    """Vista ampliada de f(x) y f'(x) sobre una hoja blanca."""

    MARGEN = 26

    def __init__(self, padre, al_cerrar):
        super().__init__(padre)
        self.title("Vista de la función")
        self.configure(background=tema.PAPEL)
        # Queda por encima de la ventana principal, sin bloquearla: se puede
        # seguir escribiendo alla y la vista se actualiza
        self.transient(padre.winfo_toplevel())
        self.minsize(tema.px(460), tema.px(320))

        self._al_cerrar = al_cerrar
        self._estado = ("", None, "")  # texto escrito, funcion, aviso
        self._fotos: list[tk.PhotoImage] = []
        self._tarea = None
        self._ancho_dibujado = 0

        self.protocol("WM_DELETE_WINDOW", self.cerrar)
        self.bind("<Escape>", lambda _e: self.cerrar())

        self._construir()
        self._colocar(padre)

    def _construir(self) -> None:
        marco = ttk.Frame(self, style="TFrame", padding=tema.px(20))
        marco.pack(fill="both", expand=True)
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(0, weight=1)

        margen = tema.px(self.MARGEN)
        self.hoja = tk.Frame(
            marco,
            background=tema.HOJA,
            highlightthickness=1,
            highlightbackground=tema.LINEA,
            highlightcolor=tema.LINEA,
        )
        self.hoja.grid(row=0, column=0, sticky="nsew")
        self.hoja.columnconfigure(0, weight=1)
        self.hoja.rowconfigure(1, weight=3)
        self.hoja.rowconfigure(4, weight=2)

        ttk.Label(self.hoja, text="FUNCIÓN", style="Seccion.Hoja.TLabel").grid(
            row=0, column=0, sticky="w", padx=margen, pady=(tema.px(18), 0)
        )
        self.lbl_f = tk.Label(self.hoja, background=tema.HOJA, borderwidth=0, justify="center")
        self.lbl_f.grid(row=1, column=0, padx=margen, pady=tema.px(14))

        tk.Frame(self.hoja, background=tema.LINEA, height=1).grid(
            row=2, column=0, sticky="ew", padx=margen
        )

        ttk.Label(self.hoja, text="DERIVADA", style="Seccion.Hoja.TLabel").grid(
            row=3, column=0, sticky="w", padx=margen, pady=(tema.px(14), 0)
        )
        self.lbl_df = tk.Label(self.hoja, background=tema.HOJA, borderwidth=0)
        self.lbl_df.grid(row=4, column=0, padx=margen, pady=(tema.px(10), tema.px(18)))

        pie = ttk.Frame(marco, style="TFrame")
        pie.grid(row=1, column=0, sticky="ew", pady=(tema.px(12), 0))
        pie.columnconfigure(1, weight=1)

        ttk.Label(pie, text="Así se escribe:", style="Suave.TLabel").grid(row=0, column=0, sticky="w")
        self.lbl_texto = ttk.Label(pie, text="", style="Escrito.TLabel")
        self.lbl_texto.grid(row=0, column=1, sticky="w", padx=(tema.px(8), tema.px(12)))

        self.btn_copiar = ttk.Button(
            pie, text="Copiar", style="Suave.TButton", command=self._copiar, cursor="hand2"
        )
        self.btn_copiar.grid(row=0, column=2, padx=(0, tema.px(6)))
        ttk.Button(
            pie, text="Cerrar", style="Suave.TButton", command=self.cerrar, cursor="hand2"
        ).grid(row=0, column=3)

        # Al cambiar el tamano de la ventana la formula se vuelve a ajustar
        self.hoja.bind("<Configure>", self._programar_dibujo)

    def _colocar(self, padre) -> None:
        """Al lado de la pizarra, para no tapar donde se escribe."""
        ancho, alto = tema.px(760), tema.px(430)
        x = padre.winfo_rootx() + padre.winfo_width() + tema.px(24)
        y = padre.winfo_toplevel().winfo_rooty() + tema.px(60)
        x = max(0, min(x, self.winfo_screenwidth() - ancho - tema.px(10)))
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

    # ------------------------------------------------------------------

    def mostrar(self, texto: str, funcion=None, aviso: str = "") -> None:
        """Cambia lo que se ve: la funcion ya leida o un aviso."""
        self._estado = (texto, funcion, aviso)
        escrito = texto if len(texto) <= 70 else texto[:69] + "…"
        self.lbl_texto.configure(text=escrito)
        self.btn_copiar.state(["!disabled"] if texto else ["disabled"])
        self._dibujar()

    def _programar_dibujo(self, evento) -> None:
        # Solo si cambio el ancho: el alto no afecta el tamano de la letra
        if evento.width == self._ancho_dibujado:
            return
        if self._tarea is not None:
            self.after_cancel(self._tarea)
        self._tarea = self.after(120, self._dibujar)

    def _dibujar(self) -> None:
        self._tarea = None
        texto, funcion, aviso = self._estado
        self._ancho_dibujado = self.hoja.winfo_width()
        if self._ancho_dibujado <= 1:  # aun sin tamano: se dibuja con <Configure>
            return
        disponible = max(tema.px(200), self._ancho_dibujado - 2 * tema.px(self.MARGEN))
        self._fotos = []

        if funcion is None:
            self.lbl_f.configure(
                image="",
                text=aviso,
                foreground=tema.ERROR if texto else tema.GRAFITO,
                font=tema.FUENTE_PASO,
                wraplength=disponible,
            )
            self.lbl_df.configure(image="", text="")
            return

        lineas = (self.lbl_f, self.lbl_df)
        tamanos = (TAMANO_VISTA, TAMANO_VISTA_DERIVADA)
        colores = (tema.TINTA_AZUL, tema.TINTA)
        for linea, (formula, plano), (tamano, minimo), color in zip(
            lineas, _renglones(funcion, con_derivada=True), tamanos, colores
        ):
            foto = imagen(
                formula, tamano, color, tema.HOJA,
                ancho_max=disponible, tamano_min=minimo,
            )
            if foto is None:
                linea.configure(
                    image="", text=plano, foreground=color,
                    font=tema.FUENTE_MONO_GRANDE, wraplength=disponible,
                )
            else:
                self._fotos.append(foto)
                linea.configure(image=foto, text="")

    def _copiar(self) -> None:
        self.clipboard_clear()
        self.clipboard_append(self._estado[0])
        self.btn_copiar.configure(text="Copiado")
        self.after(1400, self._rotulo_copiar)

    def _rotulo_copiar(self) -> None:
        if self.winfo_exists():  # la ventana pudo cerrarse mientras tanto
            self.btn_copiar.configure(text="Copiar")

    def cerrar(self) -> None:
        if self._tarea is not None:
            self.after_cancel(self._tarea)
        self._al_cerrar()
        self.destroy()
