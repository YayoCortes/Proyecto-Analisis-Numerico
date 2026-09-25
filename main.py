"""Proyecto de Analisis Numerico - Metodos para hallar raices.

Ejecutar con:

    python main.py
"""

import sys
from pathlib import Path

# Permite ejecutar el archivo desde cualquier carpeta
sys.path.insert(0, str(Path(__file__).resolve().parent))


def main() -> None:
    try:
        from gui.app import iniciar
    except ImportError as error:
        print("Falta una libreria:", error)
        print("Instalalas con:  pip install numpy matplotlib sympy")
        raise SystemExit(1)

    iniciar()


if __name__ == "__main__":
    main()
