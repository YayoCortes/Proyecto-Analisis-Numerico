"""Panel inferior: el resultado y la tabla de iteraciones (o de puntos)."""

import math
import tkinter as tk
from tkinter import ttk

from gui import tema
from nucleo.resultado import CONVERGIO, ETIQUETAS_ESTADO, MAX_ITERACIONES, RAIZ_EXACTA

COLORES_ESTADO = {
    CONVERGIO: (tema.OK_SUAVE, tema.OK),
    RAIZ_EXACTA: (tema.OK_SUAVE, tema.OK),
    MAX_ITERACIONES: (tema.AVISO_SUAVE, tema.AVISO),
}


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
    def __init__(self, padre, al_seleccionar=None):
        super().__init__(padre, style="TFrame")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self._al_seleccionar = al_seleccionar
        self._resultado = None
        self._columnas = []
        self._titulo = ""
        self._es_integral = False

        # Fila elegida y el color que tenia antes de elegirla
        self._elegida = None
        self._etiqueta_original: dict[str, str] = {}
        self._columnas_estiradas = None

        self._construir_resumen()
        self._construir_tabla()
        self._construir_pie()

    # ------------------------------------------------------------------

    def _construir_resumen(self) -> None:
        self.zona_datos = ttk.Frame(self, style="TFrame")
        self.zona_datos.grid(row=0, column=0, sticky="ew", pady=(tema.px(12), tema.px(10)))

        # Aviso cuando el metodo no converge; solo aparece si hace falta
        self.marco_aviso, self.lbl_aviso = self._recuadro(
            self, tema.AVISO_SUAVE, tema.AVISO, tema.TINTA
        )

    def _recuadro(self, padre, fondo: str, raya: str, color: str, titulo: str = ""):
        """Recuadro de mensaje con una raya de color a la izquierda."""
        marco = tk.Frame(padre, background=fondo)
        tk.Frame(marco, background=raya, width=tema.px(3)).pack(side="left", fill="y")
        columna = tk.Frame(marco, background=fondo, padx=tema.px(12), pady=tema.px(8))
        columna.pack(side="left", fill="both", expand=True)
        if titulo:
            tk.Label(
                columna, text=titulo, background=fondo, foreground=raya,
                font=tema.FUENTE_FUERTE, anchor="w",
            ).pack(fill="x", pady=(0, tema.px(2)))
        etiqueta = tk.Label(
            columna,
            text="",
            background=fondo,
            foreground=color,
            font=tema.FUENTE,
            justify="left",
            anchor="w",
            wraplength=tema.px(660),
        )
        etiqueta.pack(fill="both", expand=True)
        return marco, etiqueta

    def _construir_tabla(self) -> None:
        # Sin grid_propagate(False) la tabla le pediria a la ventana el ancho
        # de todas sus columnas (mas de 3000 px con Muller)
        marco = ttk.Frame(self, style="Hoja.TFrame", width=tema.px(400), height=tema.px(160))
        marco.grid(row=2, column=0, sticky="nsew")
        marco.grid_propagate(False)
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(0, weight=1)

        # height es solo el tamano que pide de entrada: la tabla crece con
        # la ventana. Pedir pocas filas deja mas espacio para la grafica.
        self.tabla = ttk.Treeview(
            marco,
            columns=(),
            show="headings",
            style="Iteraciones.Treeview",
            height=6,
            selectmode="browse",
        )
        self.tabla.grid(row=0, column=0, sticky="nsew")

        # Las barras aparecen solo si hacen falta (Muller tiene 16 columnas)
        barra_v = ttk.Scrollbar(marco, orient="vertical", command=self.tabla.yview)
        barra_h = ttk.Scrollbar(marco, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(
            yscrollcommand=self._barra_automatica(barra_v, 0, 1, "ns"),
            xscrollcommand=self._barra_automatica(barra_h, 1, 0, "ew"),
        )

        # Filas alternas muy suaves, para seguir la linea con la vista
        self.tabla.tag_configure("par", background=tema.HOJA)
        self.tabla.tag_configure("impar", background=tema.FILA_ALTERNA)
        self.tabla.tag_configure("final", background=tema.ROJO_SUAVE, foreground=tema.ROJO)
        self.tabla.tag_configure("elegida", background=tema.TINTA_AZUL_SUAVE, foreground=tema.TINTA)

        self.tabla.bind("<<TreeviewSelect>>", self._al_elegir_fila)
        self.tabla.bind("<Escape>", self._quitar_eleccion)
        self.tabla.bind("<Configure>", self._ajustar_columnas)

    def _construir_pie(self) -> None:
        pie = ttk.Frame(self, style="TFrame")
        pie.grid(row=3, column=0, sticky="ew", pady=(tema.px(8), 0))
        pie.columnconfigure(0, weight=1)

        self.lbl_pista = ttk.Label(pie, text="", style="Suave.TLabel")
        self.lbl_pista.grid(row=0, column=0, sticky="w")

        self.btn_copiar = ttk.Button(
            pie, text="Copiar tabla", style="Suave.TButton", command=self.copiar, cursor="hand2"
        )
        self.btn_copiar.grid(row=0, column=1, sticky="e")
        self.btn_copiar.state(["disabled"])

    @staticmethod
    def _barra_automatica(barra, fila: int, columna: int, pegado: str):
        def ajustar(primero, ultimo):
            if float(primero) <= 0.0 and float(ultimo) >= 1.0:
                barra.grid_remove()
            else:
                barra.grid(row=fila, column=columna, sticky=pegado)
            barra.set(primero, ultimo)
        return ajustar

    # ------------------------------------------------------------------
    # Resumen del resultado
    # ------------------------------------------------------------------

    def _limpiar_resumen(self) -> None:
        for hijo in self.zona_datos.winfo_children():
            hijo.destroy()

    def _datos(self, datos: list[tuple[str, str]]) -> None:
        """Cada dato es un titulo pequeno y su valor; el primero, en rojo."""
        for j, (titulo, valor) in enumerate(datos):
            separacion = (0, tema.px(30))
            ttk.Label(self.zona_datos, text=titulo, style="DatoTitulo.TLabel").grid(
                row=0, column=j, sticky="w", padx=separacion
            )
            ttk.Label(
                self.zona_datos,
                text=valor,
                style="Respuesta.TLabel" if j == 0 else "Dato.TLabel",
            ).grid(row=1, column=j, sticky="sw", padx=separacion, pady=(0, tema.px(2) if j else 0))

    def _insignia(self, texto: str, fondo: str, color: str, columna: int) -> None:
        tk.Label(
            self.zona_datos,
            text=texto,
            background=fondo,
            foreground=color,
            font=tema.FUENTE_FUERTE,
            padx=tema.px(10),
            pady=tema.px(3),
        ).grid(row=1, column=columna, sticky="sw", pady=(0, tema.px(3)))

    def _resumen_raiz(self, resultado) -> None:
        ultima = resultado.iteraciones[-1]
        # Sin converger no se puede llamar raiz a lo que se obtuvo
        nombre = "Raíz aproximada" if resultado.convergio else "Última aproximación"
        datos = [
            (nombre, formato_numero(resultado.raiz)),
            ("f(x)" if not resultado.convergio else "f(raíz)", formato_numero(resultado.fraiz)),
            ("Iteraciones", str(resultado.n_iteraciones)),
            ("Error aproximado", formato_error(ultima.ea) + (" %" if ultima.ea is not None else "")),
        ]
        self._datos(datos)
        fondo, color = COLORES_ESTADO.get(resultado.estado, (tema.AVISO_SUAVE, tema.AVISO))
        self._insignia(
            ETIQUETAS_ESTADO.get(resultado.estado, resultado.estado), fondo, color, len(datos)
        )

    def _resumen_integral(self, resultado) -> None:
        error = resultado.error_verdadero
        self._datos([
            ("Integral aproximada", formato_numero(resultado.integral)),
            ("Valor verdadero", formato_numero(resultado.exacto) if resultado.exacto is not None else "no disponible"),
            ("Error verdadero", f"{error:.6f} %" if error is not None else "---"),
            ("h", formato_numero(resultado.h)),
            ("Segmentos", str(resultado.n)),
        ])

    # ------------------------------------------------------------------

    def limpiar(self) -> None:
        self._resultado = None
        self._columnas = []
        self._elegida = None
        self._etiqueta_original = {}
        self.tabla.delete(*self.tabla.get_children())
        self.tabla.configure(columns=())  # no dejar los titulos del metodo anterior
        self._limpiar_resumen()
        self.ocultar_aviso()
        self.lbl_pista.configure(text="")
        self.btn_copiar.state(["disabled"])

    def mostrar_error(self, texto: str) -> None:
        """Deja la tabla vacia y explica, en lugar del resultado, que fallo."""
        self.limpiar()
        marco, etiqueta = self._recuadro(
            self.zona_datos, tema.ERROR_SUAVE, tema.ERROR, tema.TINTA, titulo="No se pudo calcular"
        )
        etiqueta.configure(text=texto)
        marco.grid(row=0, column=0, sticky="w")

    def avisar(self, texto: str) -> None:
        self.lbl_aviso.configure(text=texto)
        self.marco_aviso.grid(row=1, column=0, sticky="ew", pady=(0, tema.px(10)))

    def ocultar_aviso(self) -> None:
        self.marco_aviso.grid_remove()

    def mostrar(self, resultado, modulo, titulo: str = "") -> None:
        self._resultado = resultado
        self._columnas = modulo.COLUMNAS
        self._titulo = titulo or modulo.NOMBRE
        self._es_integral = modulo.TIPO == "integracion"
        self._elegida = None
        self._etiqueta_original = {}

        # Las columnas las define el metodo, no la interfaz
        claves = [c.clave for c in modulo.COLUMNAS]
        self.tabla.configure(columns=claves)
        for columna in modulo.COLUMNAS:
            centrada = columna.clave == "numero"
            self.tabla.heading(columna.clave, text=columna.titulo, anchor="center" if centrada else "e")
            self.tabla.column(
                columna.clave,
                width=tema.px(columna.ancho),
                minwidth=tema.px(40),
                anchor="center" if centrada else "e",
                stretch=False,
            )
        self._columnas_estiradas = None
        self._ajustar_columnas()

        self.tabla.delete(*self.tabla.get_children())
        # En integracion no hay "ultima iteracion": ninguna fila es la respuesta
        ultima = -1 if self._es_integral else len(resultado.iteraciones) - 1
        for i, iteracion in enumerate(resultado.iteraciones):
            etiqueta = "final" if i == ultima else ("par" if i % 2 == 0 else "impar")
            item = self.tabla.insert(
                "", "end", values=self._valores(iteracion, modulo), tags=(etiqueta,)
            )
            self._etiqueta_original[item] = etiqueta

        hijos = self.tabla.get_children()
        if hijos:
            self.tabla.see(hijos[0])  # empezar por la primera
        self.tabla.xview_moveto(0)

        self._limpiar_resumen()
        self.ocultar_aviso()
        if self._es_integral:
            self._resumen_integral(resultado)
            pista = "Elige una fila para ubicar ese punto en la gráfica."
        else:
            self._resumen_raiz(resultado)
            pista = "Elige una fila para ver esa iteración en la gráfica; con ↑ y ↓ pasas a la siguiente."
        self.lbl_pista.configure(text=pista)
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

    def _ajustar_columnas(self, _evento=None) -> None:
        """Si las columnas caben se reparten el ancho; si no, se desplaza.

        Sin esto, con muchas columnas (Muller) Tk las aplasta hasta que los
        numeros dejan de leerse.
        """
        if not self._columnas:
            return
        total = sum(tema.px(c.ancho) for c in self._columnas)
        caben = total <= self.tabla.winfo_width()
        if caben == self._columnas_estiradas:
            return
        self._columnas_estiradas = caben
        for c in self._columnas:
            self.tabla.column(
                c.clave, width=tema.px(c.ancho), stretch=caben and c.clave != "numero"
            )

    # ------------------------------------------------------------------
    # Fila elegida -> grafica
    # ------------------------------------------------------------------

    def _al_elegir_fila(self, _evento=None) -> None:
        if self._elegida is not None and self.tabla.exists(self._elegida):
            self.tabla.item(self._elegida, tags=(self._etiqueta_original[self._elegida],))

        seleccion = self.tabla.selection()
        self._elegida = seleccion[0] if seleccion else None
        indice = None
        if self._elegida is not None:
            self.tabla.item(self._elegida, tags=("elegida",))
            indice = self.tabla.index(self._elegida)

        if self._al_seleccionar:
            self._al_seleccionar(indice)

    def _quitar_eleccion(self, _evento=None) -> None:
        self.tabla.selection_remove(self.tabla.selection())

    # ------------------------------------------------------------------

    def copiar(self) -> None:
        """Copia la tabla al portapapeles para pegarla en el informe."""
        if self._resultado is None:
            return

        lineas = [self._titulo, ""]
        lineas.append("\t".join(c.titulo for c in self._columnas))
        for hijo in self.tabla.get_children():
            valores = self.tabla.item(hijo, "values")
            lineas.append("\t".join(str(v) for v in valores))
        lineas.append("")

        r = self._resultado
        if self._es_integral:
            lineas.append(f"Integral aproximada = {formato_numero(r.integral)}")
            lineas.append(f"h = {formato_numero(r.h)}")
            lineas.append(f"Segmentos n = {r.n}")
            if r.exacto is not None:
                lineas.append(f"Valor verdadero = {formato_numero(r.exacto)}")
            if r.error_verdadero is not None:
                lineas.append(f"Error verdadero = {r.error_verdadero:.6f} %")
        else:
            lineas.append(f"Raiz aproximada = {formato_numero(r.raiz)}")
            lineas.append(f"f(raiz) = {formato_numero(r.fraiz)}")
            lineas.append(f"Iteraciones utilizadas = {r.n_iteraciones}")

        self.clipboard_clear()
        self.clipboard_append("\n".join(lineas))

        self.btn_copiar.configure(text="Tabla copiada")
        self.after(1600, lambda: self.btn_copiar.configure(text="Copiar tabla"))
