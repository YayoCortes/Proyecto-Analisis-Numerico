"""Paleta y estilos de la interfaz.

Todo el aspecto visual esta concentrado aqui: cambiando estos colores
cambia la aplicacion completa, incluida la grafica de matplotlib.
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

FONDO = "#F5F6F8"        # fondo general de la ventana
SUPERFICIE = "#FFFFFF"   # tarjetas y cajas de texto
BORDE = "#DDE1E6"        # lineas divisorias, muy suaves
TEXTO = "#1F2933"        # texto principal
TEXTO_SUAVE = "#6B7580"  # etiquetas secundarias
ACENTO = "#3B6EA5"       # azul apagado
ACENTO_OSCURO = "#2F587F"
ACENTO_SUAVE = "#E8EFF7"
FILA_ALTERNA = "#FAFBFC"

OK = "#2F7A4D"
OK_SUAVE = "#EAF5EE"
AVISO = "#9A5B0B"
AVISO_SUAVE = "#FDF3E3"

# Colores de la grafica
CURVA = "#3B6EA5"
RAIZ = "#C2410C"
PASOS = "#7C9CBF"
TANGENTE = "#B08968"
EJES = "#3A4149"
REJILLA = "#E4E7EB"

# --- Tipografia -------------------------------------------------------

FUENTE = ("Segoe UI", 10)
FUENTE_PEQUENA = ("Segoe UI", 9)
FUENTE_TITULO = ("Segoe UI Semibold", 14)
FUENTE_SECCION = ("Segoe UI Semibold", 9)
FUENTE_MONO = ("Consolas", 10)
FUENTE_MONO_PEQUENA = ("Consolas", 9)


def aplicar(raiz) -> ttk.Style:
    """Aplica el tema a la ventana principal."""
    global ESCALA
    ESCALA = raiz.winfo_fpixels("1i") / 96.0

    raiz.configure(background=FONDO)

    estilo = ttk.Style(raiz)
    # clam es el unico tema integrado que deja recolorear a fondo en Windows
    estilo.theme_use("clam")

    # --- contenedores y textos ---
    estilo.configure(".", background=FONDO, foreground=TEXTO, font=FUENTE)
    estilo.configure("TFrame", background=FONDO)
    estilo.configure("Tarjeta.TFrame", background=SUPERFICIE)
    estilo.configure("Lateral.TFrame", background=SUPERFICIE)

    estilo.configure("TLabel", background=FONDO, foreground=TEXTO, font=FUENTE)
    estilo.configure("Tarjeta.TLabel", background=SUPERFICIE, foreground=TEXTO)
    estilo.configure("Titulo.TLabel", background=FONDO, foreground=TEXTO, font=FUENTE_TITULO)
    estilo.configure(
        "Seccion.TLabel",
        background=SUPERFICIE,
        foreground=TEXTO_SUAVE,
        font=FUENTE_SECCION,
    )
    estilo.configure(
        "Suave.TLabel",
        background=SUPERFICIE,
        foreground=TEXTO_SUAVE,
        font=FUENTE_PEQUENA,
    )
    estilo.configure(
        "Mono.TLabel",
        background=SUPERFICIE,
        foreground=ACENTO,
        font=FUENTE_MONO_PEQUENA,
    )
    estilo.configure(
        "Resumen.TLabel",
        background=FONDO,
        foreground=TEXTO,
        font=FUENTE_MONO,
    )
    estilo.configure(
        "ResumenSuave.TLabel",
        background=FONDO,
        foreground=TEXTO_SUAVE,
        font=FUENTE_PEQUENA,
    )

    # --- cajas de texto ---
    estilo.configure(
        "TEntry",
        fieldbackground=SUPERFICIE,
        background=SUPERFICIE,
        foreground=TEXTO,
        bordercolor=BORDE,
        lightcolor=BORDE,
        darkcolor=BORDE,
        insertcolor=TEXTO,
        padding=px(6),
    )
    estilo.map(
        "TEntry",
        bordercolor=[("focus", ACENTO)],
        lightcolor=[("focus", ACENTO)],
        darkcolor=[("focus", ACENTO)],
    )
    estilo.configure("Mono.TEntry", font=FUENTE_MONO)
    estilo.map(
        "Mono.TEntry",
        bordercolor=[("focus", ACENTO)],
        lightcolor=[("focus", ACENTO)],
        darkcolor=[("focus", ACENTO)],
    )

    # --- botones ---
    estilo.configure(
        "Acento.TButton",
        background=ACENTO,
        foreground="#FFFFFF",
        bordercolor=ACENTO,
        lightcolor=ACENTO,
        darkcolor=ACENTO,
        focuscolor=ACENTO,
        font=("Segoe UI Semibold", 10),
        padding=(px(10), px(9)),
        relief="flat",
    )
    estilo.map(
        "Acento.TButton",
        background=[("pressed", ACENTO_OSCURO), ("active", ACENTO_OSCURO)],
        bordercolor=[("pressed", ACENTO_OSCURO), ("active", ACENTO_OSCURO)],
        lightcolor=[("pressed", ACENTO_OSCURO), ("active", ACENTO_OSCURO)],
        darkcolor=[("pressed", ACENTO_OSCURO), ("active", ACENTO_OSCURO)],
    )

    estilo.configure(
        "Suave.TButton",
        background=SUPERFICIE,
        foreground=TEXTO_SUAVE,
        bordercolor=BORDE,
        lightcolor=BORDE,
        darkcolor=BORDE,
        font=FUENTE_PEQUENA,
        padding=(px(8), px(5)),
        relief="flat",
    )
    estilo.map(
        "Suave.TButton",
        background=[("active", ACENTO_SUAVE)],
        foreground=[("active", ACENTO)],
    )

    # --- selector de metodo (radiobuttons con forma de boton) ---
    estilo.configure(
        "Segmento.Toolbutton",
        background=SUPERFICIE,
        foreground=TEXTO,
        bordercolor=BORDE,
        lightcolor=SUPERFICIE,
        darkcolor=SUPERFICIE,
        focuscolor=SUPERFICIE,
        font=FUENTE,
        padding=(px(12), px(9)),
        relief="flat",
        anchor="w",
    )
    estilo.map(
        "Segmento.Toolbutton",
        background=[("selected", ACENTO_SUAVE), ("active", "#F0F3F7")],
        foreground=[("selected", ACENTO_OSCURO)],
        font=[("selected", ("Segoe UI Semibold", 10))],
    )

    # --- tabla de iteraciones ---
    estilo.configure(
        "Iteraciones.Treeview",
        background=SUPERFICIE,
        fieldbackground=SUPERFICIE,
        foreground=TEXTO,
        bordercolor=BORDE,
        lightcolor=SUPERFICIE,
        darkcolor=SUPERFICIE,
        borderwidth=0,
        rowheight=px(26),
        font=FUENTE_MONO_PEQUENA,
    )
    estilo.map(
        "Iteraciones.Treeview",
        background=[("selected", ACENTO_SUAVE)],
        foreground=[("selected", ACENTO_OSCURO)],
    )
    estilo.configure(
        "Iteraciones.Treeview.Heading",
        background=FONDO,
        foreground=TEXTO_SUAVE,
        bordercolor=BORDE,
        lightcolor=FONDO,
        darkcolor=FONDO,
        relief="flat",
        font=FUENTE_SECCION,
        padding=(px(6), px(7)),
    )
    estilo.map(
        "Iteraciones.Treeview.Heading",
        background=[("active", ACENTO_SUAVE)],
    )
    estilo.layout(
        "Iteraciones.Treeview",
        [("Iteraciones.Treeview.treearea", {"sticky": "nswe"})],
    )

    # --- barras de desplazamiento discretas ---
    estilo.configure(
        "Vertical.TScrollbar",
        background=BORDE,
        troughcolor=FONDO,
        bordercolor=FONDO,
        arrowcolor=TEXTO_SUAVE,
        lightcolor=BORDE,
        darkcolor=BORDE,
        relief="flat",
    )
    estilo.configure(
        "Horizontal.TScrollbar",
        background=BORDE,
        troughcolor=FONDO,
        bordercolor=FONDO,
        arrowcolor=TEXTO_SUAVE,
        lightcolor=BORDE,
        darkcolor=BORDE,
        relief="flat",
    )

    # --- desplegable de ejemplos ---
    estilo.configure(
        "TCombobox",
        fieldbackground=SUPERFICIE,
        background=SUPERFICIE,
        foreground=TEXTO,
        bordercolor=BORDE,
        lightcolor=BORDE,
        darkcolor=BORDE,
        arrowcolor=TEXTO_SUAVE,
        padding=px(5),
    )
    estilo.map(
        "TCombobox",
        fieldbackground=[("readonly", SUPERFICIE)],
        bordercolor=[("focus", ACENTO)],
    )

    estilo.configure("TSeparator", background=BORDE)
    estilo.configure("TPanedwindow", background=FONDO)
    estilo.configure("Sash", sashthickness=px(8), gripcount=0)

    return estilo
