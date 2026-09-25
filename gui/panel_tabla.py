"""Panel inferior: resumen del resultado y tabla de iteraciones."""

import math
import tkinter as tk
from tkinter import ttk

from gui import tema


def formato_numero(valor, decimales: int = 8) -> str:
    """Numeros legibles: notacion normal salvo que sean muy grandes o chicos."""
    if valor is None:
        return "---"
    if isinstance(valor, (int,)) and not isinstance(valor, bool):
        return str(valor)
    if not math.isfinite(valor):
        return "∞" if valor > 0 else "-∞" if valor < 0 else "---"
    if valor != 0 and (abs(valor) >= 1e7 or abs(valor) < 1e-7):
        return f"{valor:.{decimales - 2}e}"
    return f"{valor:.{decimales}f}"


def formato_error(ea) -> str:
    """El error de la primera iteracion no existe: se muestra como ---."""
    if ea is None:
        return "---"
    if not math.isfinite(ea):
        return "∞"
    return f"{ea:.6f}"


class PanelTabla(ttk.Frame):
    def __init__(self, padre):
        super().__init__(padre, style="TFrame")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._resultado = None
        self._columnas = []

        self._construir_resumen()
        self._construir_tabla()

    # ------------------------------------------------------------------

    def _construir_resumen(self) -> None:
        cabecera = ttk.Frame(self, style="TFrame")
        cabecera.grid(row=0, column=0, sticky="ew", pady=(tema.px(10), tema.px(8)))
        cabecera.columnconfigure(0, weight=1)

        textos = ttk.Frame(cabecera, style="TFrame")
        textos.grid(row=0, column=0, sticky="w")

        self.lbl_raiz = ttk.Label(textos, text="", style="Resumen.TLabel")
        self.lbl_raiz.grid(row=0, column=0, sticky="w")

        self.lbl_estado = ttk.Label(textos, text="", style="ResumenSuave.TLabel")
        self.lbl_estado.grid(row=1, column=0, sticky="w", pady=(2, 0))

        self.btn_copiar = ttk.Button(
            cabecera, text="Copiar tabla", style="Suave.TButton", command=self.copiar
        )
        self.btn_copiar.grid(row=0, column=1, sticky="e")
        self.btn_copiar.state(["disabled"])

    def _construir_tabla(self) -> None:
        marco = ttk.Frame(self, style="Tarjeta.TFrame")
        marco.grid(row=1, column=0, sticky="nsew")
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(0, weight=1)

        # height es solo el tamano que pide de entrada: la tabla crece con
        # la ventana. Pedir pocas filas deja mas espacio para la grafica.
        self.tabla = ttk.Treeview(
            marco, columns=(), show="headings", style="Iteraciones.Treeview", height=6
        )
        self.tabla.grid(row=0, column=0, sticky="nsew")

        barra = ttk.Scrollbar(marco, orient="vertical", command=self.tabla.yview)
        barra.grid(row=0, column=1, sticky="ns")
        self.tabla.configure(yscrollcommand=barra.set)

        # Filas alternas muy suaves, para seguir la linea con la vista
        self.tabla.tag_configure("par", background=tema.SUPERFICIE)
        self.tabla.tag_configure("impar", background=tema.FILA_ALTERNA)
        self.tabla.tag_configure("final", background=tema.ACENTO_SUAVE)

    # ------------------------------------------------------------------

    def limpiar(self, mensaje: str = "") -> None:
        self._resultado = None
        self._columnas = []
        self.tabla.delete(*self.tabla.get_children())
        self.tabla.configure(columns=())  # no dejar los titulos del metodo anterior
        self.lbl_raiz.configure(text=mensaje)
        self.lbl_estado.configure(text="")
        self.btn_copiar.state(["disabled"])

    def mostrar(self, resultado, modulo) -> None:
        self._resultado = resultado
        self._columnas = modulo.COLUMNAS

        # Las columnas las define el metodo, no la interfaz
        claves = [c.clave for c in modulo.COLUMNAS]
        self.tabla.configure(columns=claves)
        for columna in modulo.COLUMNAS:
            self.tabla.heading(columna.clave, text=columna.titulo, anchor="e")
            self.tabla.column(
                columna.clave,
                width=tema.px(columna.ancho),
                minwidth=tema.px(45),
                anchor="e" if columna.clave != "numero" else "center",
                stretch=columna.clave not in ("numero",),
            )

        self.tabla.delete(*self.tabla.get_children())
        ultima = len(resultado.iteraciones) - 1
        for i, iteracion in enumerate(resultado.iteraciones):
            etiqueta = "final" if i == ultima else ("par" if i % 2 == 0 else "impar")
            self.tabla.insert(
                "", "end", values=self._valores(iteracion, modulo), tags=(etiqueta,)
            )

        if resultado.iteraciones:
            self.tabla.see(self.tabla.get_children()[0])  # empezar por la primera

        self.lbl_raiz.configure(
            text=(
                f"Raíz ≈ {formato_numero(resultado.raiz)}        "
                f"f(raíz) = {formato_numero(resultado.fraiz)}"
            )
        )
        self.lbl_estado.configure(
            text=f"{resultado.n_iteraciones} iteraciones  ·  {resultado.mensaje_estado}"
        )
        self.btn_copiar.state(["!disabled"])

    def _valores(self, iteracion, modulo) -> list:
        fila = []
        for columna in modulo.COLUMNAS:
            clave = columna.clave
            if clave == "numero":
                fila.append(str(iteracion.numero))
            elif clave == "valor":
                fila.append(formato_numero(iteracion.valor))
            elif clave == "fx":
                fila.append(formato_numero(iteracion.fx))
            elif clave == "ea":
                fila.append(formato_error(iteracion.ea))
            else:
                fila.append(formato_numero(iteracion.extra.get(clave)))
        return fila

    # ------------------------------------------------------------------

    def copiar(self) -> None:
        """Copia la tabla al portapapeles para pegarla en el informe."""
        if self._resultado is None:
            return

        lineas = ["\t".join(c.titulo for c in self._columnas)]
        for hijo in self.tabla.get_children():
            valores = self.tabla.item(hijo, "values")
            lineas.append("\t".join(str(v) for v in valores))
        lineas.append("")
        lineas.append(f"Raiz aproximada = {formato_numero(self._resultado.raiz)}")
        lineas.append(f"f(raiz) = {formato_numero(self._resultado.fraiz)}")
        lineas.append(f"Iteraciones utilizadas = {self._resultado.n_iteraciones}")

        self.clipboard_clear()
        self.clipboard_append("\n".join(lineas))

        self.btn_copiar.configure(text="Copiado ✓")
        self.after(1600, lambda: self.btn_copiar.configure(text="Copiar tabla"))
