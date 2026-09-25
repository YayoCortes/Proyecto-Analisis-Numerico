"""Comprobacion de los metodos contra los resultados conocidos.

Ejecutar con:   python pruebas.py

No necesita la interfaz grafica: prueba solo la parte matematica.
"""

import math

from metodos import biseccion, falsa_posicion, newton_raphson
from nucleo import parser
from nucleo.resultado import CONVERGIO, MAX_ITERACIONES, ErrorMetodo

fallos = 0
total = 0


def revisar(titulo, condicion, detalle=""):
    global fallos, total
    total += 1
    if condicion:
        print(f"  OK   {titulo}")
    else:
        fallos += 1
        print(f"  FALLA {titulo}   {detalle}")


print("\n1. Lectura de la funcion que escribe el usuario")
print("-" * 62)

f1 = parser.compilar("-0.4x^2 + 2.2x + 4.7")
revisar("-0.4x^2 + 2.2x + 4.7 se interpreta (x^2 y 2x implicito)",
        math.isclose(f1.f(5), 5.7), f"f(5) = {f1.f(5)}")
revisar("f(10) = -13.3", math.isclose(f1.f(10), -13.3), f"f(10) = {f1.f(10)}")

f2 = parser.compilar("x^3 - 2x + 1")
revisar("derivada automatica de x^3-2x+1 es 3x^2-2",
        f2.texto_df.replace(" ", "") in ("3x^2-2", "-2+3x^2"), f2.texto_df)
revisar("la derivada mostrada se puede volver a leer",
        math.isclose(parser.compilar(f2.texto_df).f(2), 10), f2.texto_df)
revisar("f'(-1.5) = 4.75", math.isclose(f2.df(-1.5), 4.75), f"{f2.df(-1.5)}")

revisar("x**2 tambien funciona", math.isclose(parser.compilar("x**2").f(3), 9))
revisar("sin/cos funcionan", math.isclose(parser.compilar("cos(x)").f(0), 1))

try:
    parser.compilar("y^2 + 1")
    revisar("se rechaza una variable distinta de x", False)
except ErrorMetodo as e:
    revisar("se rechaza una variable distinta de x", "desconocida" in str(e))

try:
    parser.compilar("2x +")
    revisar("se rechaza la sintaxis invalida", False)
except ErrorMetodo:
    revisar("se rechaza la sintaxis invalida", True)


print("\n2. Biseccion   -0.4x^2+2.2x+4.7 en [5,10], tol 0.01 %")
print("-" * 62)

r = biseccion.biseccion(f1, 5, 10, 0.01, 100)
exacta = (2.2 + math.sqrt(2.2**2 + 4 * 0.4 * 4.7)) / 0.8
revisar("converge", r.estado == CONVERGIO, r.estado)
revisar(f"raiz = {r.raiz:.8f} (exacta {exacta:.8f})", abs(r.raiz - exacta) < 1e-3)
revisar("primera iteracion c = 7.5", math.isclose(r.iteraciones[0].valor, 7.5))
revisar("la primera iteracion no tiene error (---)", r.iteraciones[0].ea is None)
revisar("segunda iteracion c = 6.25", math.isclose(r.iteraciones[1].valor, 6.25))
revisar("guarda el intervalo a,b de cada paso",
        r.iteraciones[0].extra == {"a": 5.0, "b": 10.0}, str(r.iteraciones[0].extra))
print(f"       -> {r.n_iteraciones} iteraciones, f(raiz) = {r.fraiz:.2e}")


print("\n3. Falsa Posicion   mismos datos")
print("-" * 62)

r = falsa_posicion.falsa_posicion(f1, 5, 10, 0.01, 100)
revisar("converge", r.estado == CONVERGIO, r.estado)
revisar(f"raiz = {r.raiz:.8f} (exacta {exacta:.8f})", abs(r.raiz - exacta) < 1e-3)
# Primera iteracion segun la formula del codigo original
c1 = 10 - (f1.f(10) * (5 - 10) / (f1.f(5) - f1.f(10)))
revisar(f"primera iteracion c = {c1:.6f}", math.isclose(r.iteraciones[0].valor, c1))
revisar("usa menos iteraciones que biseccion", r.n_iteraciones < 17, str(r.n_iteraciones))
print(f"       -> {r.n_iteraciones} iteraciones, f(raiz) = {r.fraiz:.2e}")


print("\n4. Newton-Raphson   x^3-2x+1 desde x0 = -1.5, tol 0.5 %")
print("-" * 62)

r = newton_raphson.newton_raphson(f2, -1.5, 0.5, 100)
raiz_exacta = -(1 + math.sqrt(5)) / 2
revisar("converge", r.estado == CONVERGIO, r.estado)
revisar(f"raiz = {r.raiz:.8f} (exacta {raiz_exacta:.8f})", abs(r.raiz - raiz_exacta) < 1e-5)
revisar("3 iteraciones", r.n_iteraciones == 3, str(r.n_iteraciones))
revisar("iteracion 1: x = -1.631579",
        math.isclose(r.iteraciones[0].valor, -1.6315789, rel_tol=1e-6),
        f"{r.iteraciones[0].valor}")
revisar("iteracion 1 ya tiene error aproximado", r.iteraciones[0].ea is not None)
revisar("guarda xi, f(xi) y f'(xi)",
        set(r.iteraciones[0].extra) == {"xi", "fxi", "dfxi"})
for it in r.iteraciones:
    print(f"       i={it.numero}  x={it.valor:.8f}  ea={it.ea:.4f}%")


print("\n5. Manejo de errores (la aplicacion no debe caerse)")
print("-" * 62)

try:
    biseccion.biseccion(parser.compilar("x^2 + 1"), 0, 1, 0.01, 100)
    revisar("avisa cuando no hay cambio de signo", False)
except ErrorMetodo as e:
    revisar("avisa cuando no hay cambio de signo", "cambio de signo" in str(e))

try:
    newton_raphson.newton_raphson(parser.compilar("x^2 + 1"), 0, 0.01, 100)
    revisar("avisa cuando la derivada se anula", False)
except ErrorMetodo as e:
    revisar("avisa cuando la derivada se anula", "derivada" in str(e))

r = biseccion.biseccion(f1, 5, 10, 1e-12, 3)
revisar("marca que se agotaron las iteraciones", r.estado == MAX_ITERACIONES, r.estado)

r = biseccion.biseccion(parser.compilar("x^2 - 4"), 0, 2, 0.01, 100)
revisar("detecta la raiz exacta en un extremo", math.isclose(r.raiz, 2.0), str(r.raiz))

try:
    biseccion.biseccion(f1, 5, 10, 0, 100)
    revisar("rechaza tolerancia cero", False)
except ErrorMetodo:
    revisar("rechaza tolerancia cero", True)


print("\n6. Otras funciones escritas por el usuario")
print("-" * 62)

fc = parser.compilar("cos(x) - x")
r = biseccion.biseccion(fc, 0, 1, 0.0001, 200)
revisar(f"cos(x)-x en [0,1] -> {r.raiz:.6f} (0.739085)", abs(r.raiz - 0.7390851) < 1e-4)

r = falsa_posicion.falsa_posicion(fc, 0, 1, 0.0001, 200)
revisar(f"falsa posicion -> {r.raiz:.6f}", abs(r.raiz - 0.7390851) < 1e-4)

r = newton_raphson.newton_raphson(fc, 0.5, 0.0001, 200)
revisar(f"newton -> {r.raiz:.6f}", abs(r.raiz - 0.7390851) < 1e-6)

fe = parser.compilar("exp(x) - 3x")
r = biseccion.biseccion(fe, 0, 1, 0.0001, 200)
revisar(f"exp(x)-3x en [0,1] -> {r.raiz:.6f} (0.619061)", abs(r.raiz - 0.6190612) < 1e-4)


print("\n" + "=" * 62)
if fallos:
    print(f"  {fallos} de {total} comprobaciones fallaron")
    raise SystemExit(1)
print(f"  Las {total} comprobaciones pasaron")
