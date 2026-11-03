"""Paleta y estilos de la interfaz.

Todo el aspecto visual esta concentrado aqui: cambiando estos colores
cambia la aplicacion completa, incluida la grafica de matplotlib.

La idea visual sale del salon de clase: los datos se plantean en una
pizarra (columna izquierda) y la solucion se dibuja en papel milimetrado,
con la respuesta marcada en rojo como lo haria el profesor.
"""

import ctypes
import sys
from tkinter import ttk

# Factor de escala de la pantalla (1.0 = 100 %, 1.25 = 125 %, ...).
# Lo calcula aplicar() y sirve para que las medidas en pixeles se vean
# del mismo tamano en cualquier monitor.
ESCALA = 1.0


def activar_dpi() -> None:
    """Avisa a Windows que la aplicacion sabe manejar pantallas escaladas.

    Sin esto, en un monitor al 125 % Windows agranda la ventana como si
    fuera una imagen y las letras salen borrosas. Hay que llamarla antes
    de crear la ventana.
    """
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # consciente del DPI
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()  # Windows mas antiguos
        except Exception:
            pass


def px(valor: float) -> int:
    """Convierte una medida pensada al 100 % a pixeles de esta pantalla."""
    return max(1, round(valor * ESCALA))

# --- Paleta -----------------------------------------------------------

# Pizarra: columna de controles
PIZARRA = "#22332C"         # verde pizarra, fondo de la columna
PIZARRA_ALTA = "#2E443A"    # metodo elegido y paso del raton
PIZARRA_CAMPO = "#182520"   # cajas de texto sobre la pizarra
PIZARRA_BORDE = "#3D564B"
TIZA = "#ECEFE7"            # texto principal sobre la pizarra
TIZA_SUAVE = "#9EB0A5"      # etiquetas y ayudas
TIZA_AMARILLA = "#EFC75E"   # acento: boton Calcular, metodo elegido
TIZA_AMARILLA_ALTA = "#F6D987"
TIZA_AZUL = "#A8C8E6"       # f'(x) en la pantalla, la x y la tecla 2nd
TIZA_ROJA = "#F0938A"       # funcion mal escrita

# Teclas del modo calculadora: funciones oscuras y cifras mas claras,
# como en una calculadora de verdad
TECLA = "#2B3E35"
TECLA_ALTA = "#374D43"
TECLA_CIFRA = "#3D5549"
TECLA_CIFRA_ALTA = "#4A6457"

# Papel: zona de resultados
PAPEL = "#E9EDE8"           # fondo general, gris verdoso muy claro
HOJA = "#FFFFFF"            # grafica y tabla
LINEA = "#D3DBD2"           # bordes y divisiones
TINTA = "#1E2723"           # texto principal
GRAFITO = "#64706A"         # texto secundario
FILA_ALTERNA = "#F5F7F3"
ENCABEZADO_TABLA = "#EEF2EC"

ROJO = "#C0392B"            # la respuesta, marcada como en una correccion
ROJO_SUAVE = "#FBEAE7"
TINTA_AZUL = "#22419B"      # tinta de boligrafo: la curva y las formulas
TINTA_AZUL_SUAVE = "#E1E8F7"

OK = "#2D6A45"
OK_SUAVE = "#E0EFE4"
AVISO = "#87580A"
AVISO_SUAVE = "#F8EDCF"
ERROR = "#9E2F27"
ERROR_SUAVE = "#F7E1DD"

# Colores de la grafica (papel milimetrado)
CURVA = TINTA_AZUL
RAIZ = ROJO
PASOS = "#7E8A83"           # grafito: aproximaciones intermedias
TANGENTE = "#B5791A"        # lapiz ocre: tangentes, parabolas, trapecios
RESALTE = "#1E2723"         # iteracion elegida en la tabla
EJES = "#2F3833"
MILIMETRO = "#E2EEE0"       # rejilla fina
CENTIMETRO = "#BFD6BE"      # rejilla gruesa

# --- Tipografia -------------------------------------------------------
# Bahnschrift es la letra de rotulacion tecnica (tipo DIN) que trae
# Windows; Consolas alinea las cifras de la tabla en columnas.

FUENTE = ("Bahnschrift", 10)
FUENTE_PEQUENA = ("Bahnschrift", 9)
FUENTE_FUERTE = ("Bahnschrift SemiBold", 10)
FUENTE_PASO = ("Bahnschrift SemiBold", 11)
FUENTE_MARCA = ("Bahnschrift SemiBold", 15)
FUENTE_TITULO = ("Bahnschrift SemiBold", 18)
FUENTE_RESULTADO = ("Bahnschrift SemiBold", 17)
FUENTE_MONO = ("Consolas", 10)
FUENTE_MONO_PEQUENA = ("Consolas", 9)
FUENTE_MONO_GRANDE = ("Consolas", 11)
FUENTE_TECLA = ("Bahnschrift", 10)
FUENTE_TECLA_CIFRA = ("Bahnschrift SemiBold", 11)
FUENTE_TECLA_OPERADOR = ("Bahnschrift SemiBold", 13)


def aplicar(raiz) -> ttk.Style:
    """Aplica el tema a la ventana principal."""
    global ESCALA
    ESCALA = raiz.winfo_fpixels("1i") / 96.0

    raiz.configure(background=PAPEL)

    # La lista desplegable de los ejemplos no es ttk: se colorea aparte
    raiz.option_add("*TCombobox*Listbox.background", HOJA)
    raiz.option_add("*TCombobox*Listbox.foreground", TINTA)
    raiz.option_add("*TCombobox*Listbox.selectBackground", TINTA_AZUL_SUAVE)
    raiz.option_add("*TCombobox*Listbox.selectForeground", TINTA)
    raiz.option_add("*TCombobox*Listbox.font", FUENTE)
    raiz.option_add("*TCombobox*Listbox.borderWidth", 0)

    estilo = ttk.Style(raiz)
    # clam es el unico tema integrado que deja recolorear a fondo en Windows
    estilo.theme_use("clam")

    _contenedores(estilo)
    _textos(estilo)
    _cajas(estilo)
    _botones(estilo)
    _selectores(estilo)
    _teclas(estilo)
    _tabla(estilo)
    _barras(estilo)

    estilo.configure("TPanedwindow", background=PAPEL)
    estilo.configure("Sash", sashthickness=px(10), gripcount=0, background=PAPEL)

    return estilo


def _contenedores(estilo) -> None:
    estilo.configure(".", background=PAPEL, foreground=TINTA, font=FUENTE)
    estilo.configure("TFrame", background=PAPEL)
    estilo.configure("Hoja.TFrame", background=HOJA)
    estilo.configure("Pizarra.TFrame", background=PIZARRA)


def _textos(estilo) -> None:
    # --- sobre el papel ---
    estilo.configure("TLabel", background=PAPEL, foreground=TINTA, font=FUENTE)
    estilo.configure("Titulo.TLabel", foreground=TINTA, font=FUENTE_TITULO)
    estilo.configure("Explicacion.TLabel", foreground=GRAFITO, font=FUENTE)
    estilo.configure("Formula.TLabel", foreground=TINTA_AZUL, font=FUENTE_MONO_GRANDE)
    estilo.configure("Suave.TLabel", foreground=GRAFITO, font=FUENTE_PEQUENA)
    estilo.configure("DatoTitulo.TLabel", foreground=GRAFITO, font=FUENTE_PEQUENA)
    estilo.configure("Dato.TLabel", foreground=TINTA, font=FUENTE_MONO_GRANDE)
    estilo.configure("Respuesta.TLabel", foreground=ROJO, font=FUENTE_RESULTADO)
    estilo.configure("Escrito.TLabel", foreground=TINTA, font=FUENTE_MONO)
    estilo.configure(
        "Seccion.Hoja.TLabel", background=HOJA, foreground=GRAFITO, font=("Bahnschrift SemiBold", 9)
    )

    # --- sobre la pizarra ---
    estilo.configure("Pizarra.TLabel", background=PIZARRA, foreground=TIZA, font=FUENTE)
    estilo.configure("Marca.Pizarra.TLabel", foreground=TIZA, font=FUENTE_MARCA)
    estilo.configure("Paso.Pizarra.TLabel", foreground=TIZA, font=FUENTE_PASO)
    estilo.configure("Grupo.Pizarra.TLabel", foreground=TIZA_SUAVE, font=FUENTE_PEQUENA)
    estilo.configure("Suave.Pizarra.TLabel", foreground=TIZA_SUAVE, font=FUENTE_PEQUENA)


def _cajas(estilo) -> None:
    estilo.configure(
        "Pizarra.TEntry",
        fieldbackground=PIZARRA_CAMPO,
        background=PIZARRA_CAMPO,
        foreground=TIZA,
        bordercolor=PIZARRA_BORDE,
        lightcolor=PIZARRA_CAMPO,
        darkcolor=PIZARRA_CAMPO,
        insertcolor=TIZA_AMARILLA,
        selectbackground=PIZARRA_BORDE,
        selectforeground=TIZA,
        font=FUENTE_MONO,
        padding=(px(8), px(6)),
    )
    estilo.map(
        "Pizarra.TEntry",
        bordercolor=[("focus", TIZA_AMARILLA)],
        lightcolor=[("focus", PIZARRA_CAMPO)],
    )
    # La misma caja con el borde en rojo cuando f(x) no se entiende
    estilo.configure("Invalida.Pizarra.TEntry", bordercolor=TIZA_ROJA)
    estilo.map(
        "Invalida.Pizarra.TEntry",
        bordercolor=[("focus", TIZA_ROJA)],
        lightcolor=[("focus", PIZARRA_CAMPO)],
    )

    # Desplegable de ejemplos, sobre el papel
    estilo.configure(
        "TCombobox",
        fieldbackground=HOJA,
        background=HOJA,
        foreground=TINTA,
        bordercolor=LINEA,
        lightcolor=HOJA,
        darkcolor=HOJA,
        arrowcolor=GRAFITO,
        selectbackground=HOJA,
        selectforeground=TINTA,
        padding=(px(8), px(5)),
    )
    estilo.map(
        "TCombobox",
        fieldbackground=[("readonly", HOJA)],
        selectbackground=[("readonly", HOJA)],
        selectforeground=[("readonly", TINTA)],
        bordercolor=[("focus", TINTA_AZUL), ("hover", GRAFITO)],
        arrowcolor=[("hover", TINTA)],
    )


def _botones(estilo) -> None:
    estilo.configure(
        "Calcular.TButton",
        background=TIZA_AMARILLA,
        foreground=PIZARRA,
        bordercolor=TIZA_AMARILLA,
        lightcolor=TIZA_AMARILLA,
        darkcolor=TIZA_AMARILLA,
        focuscolor=TIZA_AMARILLA,
        font=("Bahnschrift SemiBold", 11),
        padding=(px(10), px(10)),
        relief="flat",
    )
    estilo.map(
        "Calcular.TButton",
        background=[("pressed", TIZA_AMARILLA), ("active", TIZA_AMARILLA_ALTA)],
        bordercolor=[("active", TIZA_AMARILLA_ALTA)],
        lightcolor=[("active", TIZA_AMARILLA_ALTA)],
        darkcolor=[("active", TIZA_AMARILLA_ALTA)],
    )

    estilo.configure(
        "Suave.TButton",
        background=HOJA,
        foreground=TINTA,
        bordercolor=LINEA,
        lightcolor=HOJA,
        darkcolor=HOJA,
        focuscolor=HOJA,
        font=FUENTE_PEQUENA,
        padding=(px(10), px(5)),
        relief="flat",
    )
    estilo.map(
        "Suave.TButton",
        background=[("disabled", PAPEL), ("active", TINTA_AZUL_SUAVE)],
        foreground=[("disabled", "#A3ACA6"), ("active", TINTA_AZUL)],
        bordercolor=[("disabled", LINEA), ("active", TINTA_AZUL)],
        lightcolor=[("disabled", PAPEL), ("active", TINTA_AZUL_SUAVE)],
        darkcolor=[("disabled", PAPEL), ("active", TINTA_AZUL_SUAVE)],
    )

    # Boton ⤢ (vista ampliada), dentro de la pantalla de la pizarra
    estilo.configure(
        "Enlace.Pizarra.TButton",
        background=PIZARRA_CAMPO,
        foreground=TIZA_AMARILLA,
        bordercolor=PIZARRA_CAMPO,
        lightcolor=PIZARRA_CAMPO,
        darkcolor=PIZARRA_CAMPO,
        focuscolor=PIZARRA_CAMPO,
        font=("Bahnschrift", 13),
        padding=(px(6), 0),
        relief="flat",
    )
    estilo.map(
        "Enlace.Pizarra.TButton",
        background=[("active", PIZARRA_ALTA)],
        foreground=[("active", TIZA_AMARILLA_ALTA)],
        bordercolor=[("active", PIZARRA_ALTA)],
        lightcolor=[("active", PIZARRA_ALTA)],
        darkcolor=[("active", PIZARRA_ALTA)],
        focuscolor=[("active", PIZARRA_ALTA)],
    )


def _selectores(estilo) -> None:
    # Lista de metodos: radiobuttons con forma de renglon
    estilo.configure(
        "Metodo.Toolbutton",
        background=PIZARRA,
        foreground="#C9D3CC",
        bordercolor=PIZARRA,
        lightcolor=PIZARRA,
        darkcolor=PIZARRA,
        focuscolor=PIZARRA,
        font=FUENTE,
        padding=(px(12), px(6)),
        relief="flat",
        anchor="w",
    )
    estilo.map(
        "Metodo.Toolbutton",
        background=[("selected", PIZARRA_ALTA), ("active", "#293C34")],
        foreground=[("selected", TIZA), ("active", TIZA)],
        focuscolor=[("selected", PIZARRA_ALTA), ("active", "#293C34")],
        font=[("selected", FUENTE_FUERTE)],
    )

    # Selector de dos opciones (regla de integracion)
    estilo.configure(
        "Opcion.Toolbutton",
        background=PIZARRA_CAMPO,
        foreground=TIZA_SUAVE,
        bordercolor=PIZARRA_BORDE,
        lightcolor=PIZARRA_CAMPO,
        darkcolor=PIZARRA_CAMPO,
        focuscolor=PIZARRA_CAMPO,
        font=FUENTE,
        padding=(px(8), px(6)),
        relief="flat",
        anchor="center",
    )
    estilo.map(
        "Opcion.Toolbutton",
        background=[("selected", TIZA_AMARILLA), ("active", PIZARRA_ALTA)],
        foreground=[("selected", PIZARRA), ("active", TIZA)],
        bordercolor=[("selected", TIZA_AMARILLA)],
        lightcolor=[("selected", TIZA_AMARILLA), ("active", PIZARRA_ALTA)],
        darkcolor=[("selected", TIZA_AMARILLA), ("active", PIZARRA_ALTA)],
        focuscolor=[("selected", TIZA_AMARILLA), ("active", PIZARRA_ALTA)],
        font=[("selected", FUENTE_FUERTE)],
    )


def _teclas(estilo) -> None:
    """Teclas del modo calculadora.

    Cada tipo de tecla necesita su propio map: si un estilo hijo define
    background, ttk ya no mira el map del estilo padre al pasar el raton.
    """
    tipos = {
        # tipo: (fondo, fondo al pasar el raton, color de la letra, letra)
        "Funcion": (TECLA, TECLA_ALTA, TIZA, FUENTE_TECLA),
        "Variable": (TECLA, TECLA_ALTA, TIZA_AZUL, FUENTE_TECLA_CIFRA),
        "Numero": (TECLA_CIFRA, TECLA_CIFRA_ALTA, TIZA, FUENTE_TECLA_CIFRA),
        "Operador": (TECLA_CIFRA, TECLA_CIFRA_ALTA, TIZA_AMARILLA, FUENTE_TECLA_OPERADOR),
        "Borrar": (TECLA, TECLA_ALTA, TIZA_ROJA, FUENTE_TECLA_CIFRA),
        "Cursor": (TECLA, TECLA_ALTA, TIZA_SUAVE, FUENTE_TECLA_CIFRA),
    }
    for tipo, (fondo, alto, letra, fuente) in tipos.items():
        nombre = f"{tipo}.Tecla.TButton"
        estilo.configure(
            nombre,
            background=fondo,
            foreground=letra,
            bordercolor=fondo,
            lightcolor=fondo,
            darkcolor=fondo,
            focuscolor=fondo,
            font=fuente,
            padding=(0, px(5)),
            relief="flat",
            anchor="center",
        )
        estilo.map(
            nombre,
            background=[("pressed", PIZARRA), ("active", alto)],
            bordercolor=[("pressed", PIZARRA), ("active", alto)],
            lightcolor=[("pressed", PIZARRA), ("active", alto)],
            darkcolor=[("pressed", PIZARRA), ("active", alto)],
            focuscolor=[("pressed", PIZARRA), ("active", alto)],
        )

    # 2nd se queda encendida (en azul) hasta la siguiente tecla
    estilo.configure(
        "Segunda.Tecla.Toolbutton",
        background=TECLA,
        foreground=TIZA_AZUL,
        bordercolor=TECLA,
        lightcolor=TECLA,
        darkcolor=TECLA,
        focuscolor=TECLA,
        font=FUENTE_TECLA_CIFRA,
        padding=(0, px(5)),
        relief="flat",
        anchor="center",
    )
    estilo.map(
        "Segunda.Tecla.Toolbutton",
        background=[("selected", TIZA_AZUL), ("active", TECLA_ALTA)],
        foreground=[("selected", PIZARRA)],
        bordercolor=[("selected", TIZA_AZUL), ("active", TECLA_ALTA)],
        lightcolor=[("selected", TIZA_AZUL), ("active", TECLA_ALTA)],
        darkcolor=[("selected", TIZA_AZUL), ("active", TECLA_ALTA)],
        focuscolor=[("selected", TIZA_AZUL), ("active", TECLA_ALTA)],
    )


def _tabla(estilo) -> None:
    estilo.configure(
        "Iteraciones.Treeview",
        background=HOJA,
        fieldbackground=HOJA,
        foreground=TINTA,
        bordercolor=LINEA,
        lightcolor=HOJA,
        darkcolor=HOJA,
        borderwidth=0,
        rowheight=px(26),
        font=FUENTE_MONO_PEQUENA,
    )
    estilo.map(
        "Iteraciones.Treeview",
        background=[("selected", TINTA_AZUL_SUAVE)],
        foreground=[("selected", TINTA)],
    )
    estilo.configure(
        "Iteraciones.Treeview.Heading",
        background=ENCABEZADO_TABLA,
        foreground=GRAFITO,
        bordercolor=LINEA,
        lightcolor=ENCABEZADO_TABLA,
        darkcolor=ENCABEZADO_TABLA,
        relief="flat",
        font=("Bahnschrift SemiBold", 9),
        padding=(px(6), px(7)),
    )
    estilo.map(
        "Iteraciones.Treeview.Heading",
        background=[("active", ENCABEZADO_TABLA)],
    )
    estilo.layout(
        "Iteraciones.Treeview",
        [("Iteraciones.Treeview.treearea", {"sticky": "nswe"})],
    )


def _barras(estilo) -> None:
    """Barras de desplazamiento delgadas y sin flechas."""
    for orientacion, pegado in (("Vertical", "ns"), ("Horizontal", "ew")):
        estilo.layout(
            f"{orientacion}.TScrollbar",
            [(
                f"{orientacion}.Scrollbar.trough",
                {
                    "sticky": pegado,
                    "children": [
                        (f"{orientacion}.Scrollbar.thumb", {"expand": "1", "sticky": "nswe"})
                    ],
                },
            )],
        )
        estilo.configure(
            f"{orientacion}.TScrollbar",
            background="#C5CEC6",
            troughcolor=HOJA,
            bordercolor=HOJA,
            lightcolor="#C5CEC6",
            darkcolor="#C5CEC6",
            arrowsize=px(9),
            relief="flat",
        )
        estilo.map(
            f"{orientacion}.TScrollbar",
            background=[("active", "#A9B4AC")],
            lightcolor=[("active", "#A9B4AC")],
            darkcolor=[("active", "#A9B4AC")],
        )

    estilo.configure(
        "Pizarra.Vertical.TScrollbar",
        background=PIZARRA_BORDE,
        troughcolor=PIZARRA,
        bordercolor=PIZARRA,
        lightcolor=PIZARRA_BORDE,
        darkcolor=PIZARRA_BORDE,
    )
    estilo.map(
        "Pizarra.Vertical.TScrollbar",
        background=[("active", "#557064")],
        lightcolor=[("active", "#557064")],
        darkcolor=[("active", "#557064")],
    )
