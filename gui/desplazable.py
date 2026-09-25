"""Zona con desplazamiento vertical.

Sirve para que el panel de controles siga siendo usable en pantallas
pequenas: si el contenido no cabe aparece una barra lateral, y si cabe
no se ve nada distinto.
"""

import tkinter as tk
from tkinter import ttk


class AreaDesplazable(ttk.Frame):
    def __init__(self, padre, fondo: str, estilo_interior: str = "TFrame", ancho: int = 300):
        super().__init__(padre)
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

        self.barra = ttk.Scrollbar(self, orient="vertical", command=self.lienzo.yview)
        self.lienzo.configure(yscrollcommand=self._ajustar_barra)

        # Todo el contenido va dentro de este marco
        self.interior = ttk.Frame(self.lienzo, style=estilo_interior)
        self._ventana = self.lienzo.create_window(
            (0, 0), window=self.interior, anchor="nw"
        )

        self.interior.bind("<Configure>", self._al_cambiar_contenido)
        self.lienzo.bind("<Configure>", self._al_cambiar_ancho)

        # La rueda del raton solo actua mientras el puntero esta encima
        self.lienzo.bind("<Enter>", self._activar_rueda)
        self.lienzo.bind("<Leave>", self._desactivar_rueda)

    # ------------------------------------------------------------------

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

    def _activar_rueda(self, _evento=None) -> None:
        self.lienzo.bind_all("<MouseWheel>", self._rueda)

    def _desactivar_rueda(self, _evento=None) -> None:
        self.lienzo.unbind_all("<MouseWheel>")

    def _rueda(self, evento) -> None:
        if self.barra.winfo_ismapped():
            self.lienzo.yview_scroll(int(-evento.delta / 120), "units")
