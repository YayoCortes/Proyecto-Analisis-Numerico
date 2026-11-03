"""Zona con desplazamiento vertical.

Sirve para que el panel de controles siga siendo usable en pantallas
pequenas: si el contenido no cabe aparece una barra lateral, y si cabe
no se ve nada distinto.
"""

import tkinter as tk
from tkinter import ttk


class AreaDesplazable(ttk.Frame):
    def __init__(
        self,
        padre,
        fondo: str,
        estilo_interior: str = "TFrame",
        ancho: int = 300,
        estilo_barra: str = "Vertical.TScrollbar",
    ):
        super().__init__(padre, style=estilo_interior)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Sin un ancho explicito, un Canvas pide 378 px por omision y
        # ensancharia la columna de controles sin motivo.
        self.lienzo = tk.Canvas(
            self,
            background=fondo,
            highlightthickness=0,
            borderwidth=0,
            width=ancho,
            height=1,
        )
        self.lienzo.grid(row=0, column=0, sticky="nsew")

        self.barra = ttk.Scrollbar(
            self, orient="vertical", command=self.lienzo.yview, style=estilo_barra
        )
        self.lienzo.configure(yscrollcommand=self._ajustar_barra)

        # Todo el contenido va dentro de este marco
        self.interior = ttk.Frame(self.lienzo, style=estilo_interior)
        self._ventana = self.lienzo.create_window(
            (0, 0), window=self.interior, anchor="nw"
        )

        self.interior.bind("<Configure>", self._al_cambiar_contenido)
        self.lienzo.bind("<Configure>", self._al_cambiar_ancho)

        # La rueda del raton solo actua mientras el puntero esta encima de
        # la zona, incluidos los botones y cajas que hay dentro. (Con Enter y
        # Leave del lienzo se perdia al pasar sobre ellos: Tk avisa Leave
        # cuando el puntero entra a un widget hijo.)
        self.bind_all("<MouseWheel>", self._rueda, add="+")

    # ------------------------------------------------------------------

    def mostrar(self, desde, hasta=None) -> None:
        """Desplaza lo justo para que se vea desde un widget hasta otro.

        Si no cabe todo, se prefiere que se vea el comienzo.
        """
        hasta = hasta or desde
        self.update_idletasks()
        # El aviso <Configure> del contenido aun no ha llegado: sin esto se
        # desplazaria con el alto viejo
        self._al_cambiar_contenido()
        total = self.interior.winfo_height()
        visible = self.lienzo.winfo_height()
        if total <= visible:
            return
        arriba = desde.winfo_rooty() - self.interior.winfo_rooty()
        abajo = hasta.winfo_rooty() + hasta.winfo_height() - self.interior.winfo_rooty()
        inicio = self.lienzo.canvasy(0)
        if abajo > inicio + visible:
            self.lienzo.yview_moveto(min(arriba, abajo - visible) / total)
        elif arriba < inicio:
            self.lienzo.yview_moveto(arriba / total)

    def _al_cambiar_contenido(self, _evento=None) -> None:
        self.lienzo.configure(scrollregion=self.lienzo.bbox("all"))

    def _al_cambiar_ancho(self, evento) -> None:
        # El contenido ocupa todo el ancho disponible
        self.lienzo.itemconfigure(self._ventana, width=evento.width)

    def _ajustar_barra(self, primero, ultimo) -> None:
        """La barra aparece solo cuando el contenido no cabe."""
        if float(primero) <= 0.0 and float(ultimo) >= 1.0:
            self.barra.grid_remove()
        else:
            self.barra.grid(row=0, column=1, sticky="ns")
        self.barra.set(primero, ultimo)

    def _rueda(self, evento) -> None:
        if self.barra.winfo_ismapped() and self._bajo_el_puntero(evento):
            self.lienzo.yview_scroll(int(-evento.delta / 120), "units")

    def _bajo_el_puntero(self, evento) -> bool:
        try:
            widget = self.winfo_containing(evento.x_root, evento.y_root)
        except (KeyError, tk.TclError):  # widgets internos de Tk, sin nombre en Python
            return False
        while widget is not None:
            if widget is self:
                return True
            widget = widget.master
        return False
