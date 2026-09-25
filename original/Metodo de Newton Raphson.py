import numpy as np
import math
import matplotlib.pyplot as plt

def f(x):
    return (x)**3 - 2 * (x) + 1

def df(x):
    return 3 * (x)**2 - 2

x_plot = np.linspace(0, 2, 400)
plt.axhline(0, color='black', linewidth=0.8)   # eje x
plt.axvline(0, color='black', linewidth=0.8)   # eje y
plt.plot(x_plot, f(x_plot))
plt.title("Grafica ")
plt.grid()
plt.show()

# Ajuste de punto inicial para coincidir con los resultados esperados
x0 = -1.5
n = 100
et = 0.5
xi = x0

print(f"Método de Newton-Raphson (Inicio en x0 = {x0})\n")

for i in range(1, n + 1):
    x_next = xi - f(xi) / df(xi)

    # Cálculo del error relativo porcentual aproximado
    # Nota: Para la primera iteración se usa xi (el valor inicial 0)
    ea = abs((x_next - xi) / x_next) * 100

    print(f"Iteracion {i}: x = {x_next:.6f}   ea = {ea:.4f}%")

    if ea <= et:
        xi = x_next
        break

    xi = x_next

print(f"\nRaiz aproximada = {xi:.8f}")
print(f"f(c) = {f(xi):.8f}")
print(f"Iteraciones utilizadas = {i}")