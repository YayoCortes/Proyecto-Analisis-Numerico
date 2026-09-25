#Metodo Falsa Posicion
import numpy as np
import matplotlib.pyplot as plt
def f(x):
    return -0.4 * (x)**2 + 2.2 * (x) + 4.7

    # grafica
x = np.linspace(0, 10, 400)
plt.axhline(0, color='black', linewidth=0.8)   # eje x
plt.axvline(0, color='black', linewidth=0.8)   # eje y
plt.plot(x, f(x))
plt.title("Grafica")
plt.grid()
plt.show()

a = 5
b = 10
n = 100
et = 0.01        # ahora en PORCENTAJE: 0.1%
ca = 0
iteraciones = 0

if f(a) * f(b) < 0:
    for i in range(1, n+1):
        c = b - (f(b) * (a - b) / (f(a) - f(b)))
        iteraciones = i

        if i == 1:
            print(f"Iteracion {i}: c = {c:.8f}   ea = ---")
        else:
            ea = abs((c - ca) / c) * 100
            print(f"Iteracion {i}: c = {c:.8f}   ea = {ea:.6f}%")
            if ea <= et:
                break

        if f(a) * f(c) < 0:
            b = c
        else:
            a = c

        ca = c



    print(f"\nRaiz aproximada = {c:.8f}")
    print(f"f(c) = {f(c):.8f}")
    print(f"Iteraciones utilizadas = {iteraciones}")
else:
    print("No hay raiz en el intervalo dado")