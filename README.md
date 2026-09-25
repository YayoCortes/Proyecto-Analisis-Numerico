# Métodos Numéricos — Proyecto de Análisis Numérico

Interfaz gráfica para hallar raíces de una función. **La función f(x) la escribe
el usuario**: no está fija en el código.

Avance actual: **3 métodos** (Bisección, Falsa Posición y Newton-Raphson).
La estructura ya está lista para agregar el 4.º y 5.º método y el problema
de aplicación.

## Cómo ejecutarlo

```
pip install -r requirements.txt
python main.py
```

Necesita Python 3.10 o superior. Tkinter viene incluido con Python en Windows.

## Qué se puede hacer

| Requisito | Dónde está |
|---|---|
| Ver las gráficas | Panel derecho, dentro de la ventana (con zoom y botón para guardar la imagen en PNG) |
| Cambiar de método fácilmente | Botones de la columna izquierda; la f(x) escrita **se conserva** y se recalcula sola |
| Ver las iteraciones | Tabla inferior, con todas las columnas del método y el error de cada paso |
| Escribir la función | Caja `FUNCIÓN f(x)`; la derivada para Newton se calcula sola |

### Cómo escribir la función

Se acepta la forma natural y también la de Python:

| Se puede escribir | También vale |
|---|---|
| `x^2` | `x**2` |
| `2x` | `2*x` |
| `-0.4x^2 + 2.2x + 4.7` | `-0.4*x**2 + 2.2*x + 4.7` |

Funciones disponibles: `sin` (o `sen`), `cos`, `tan`, `exp`, `ln`, `log`,
`sqrt` (o `raiz`), `abs`, y las constantes `pi` y `e`.

La tolerancia se da en **porcentaje**, igual que en los códigos originales:
el método se detiene cuando el error relativo aproximado

    ea = |(x_nuevo - x_anterior) / x_nuevo| × 100

baja de ese valor.

## Organización del código

```
main.py                  punto de entrada
nucleo/
  parser.py              texto del usuario -> función evaluable + derivada (SymPy)
  resultado.py           estructuras comunes: Iteracion, Resultado, Parametro, Columna
  validacion.py          validaciones y mensajes de error compartidos
metodos/
  cerrados.py            bucle común de los métodos cerrados
  biseccion.py           c = (a + b) / 2
  falsa_posicion.py      c = b - f(b)(a - b) / (f(a) - f(b))
  newton_raphson.py      x(i+1) = x(i) - f(x(i)) / f'(x(i))
gui/
  tema.py                paleta, tipografías y escala de pantalla
  app.py                 ventana principal
  panel_controles.py     columna izquierda (método, f(x), parámetros)
  panel_grafica.py       gráfica de matplotlib embebida
  panel_tabla.py         tabla de iteraciones
  desplazable.py         zona con barra de desplazamiento
pruebas.py               comprueba los métodos sin abrir la interfaz
original/                los tres scripts de consola iniciales, sin modificar
```

Los métodos **no saben nada de la interfaz**: reciben la función y los
parámetros, y devuelven un `Resultado`. La interfaz tampoco sabe nada de los
métodos: dibuja los campos y las columnas leyendo los datos `PARAMETROS` y
`COLUMNAS` que cada método declara.

### Agregar un método nuevo

1. Copiar `metodos/biseccion.py` como modelo.
2. Definir `NOMBRE`, `CLAVE`, `TIPO`, `RESUMEN`, `FORMULA`, `PARAMETROS`,
   `COLUMNAS` y la función `ejecutar(funcion, parametros, tol_pct, max_iter)`.
3. Agregarlo a la lista `METODOS` de `metodos/__init__.py`.

No hay que tocar la interfaz: el botón, los campos y las columnas aparecen solos.

## Comprobación

```
python pruebas.py
```

Verifica los tres métodos contra los resultados de los scripts originales y
contra raíces conocidas:

| Método | Función | Datos | Resultado |
|---|---|---|---|
| Bisección | `-0.4x² + 2.2x + 4.7` | [5, 10], tol 0.01 % | 7.14416504 en 13 iteraciones |
| Falsa Posición | `-0.4x² + 2.2x + 4.7` | [5, 10], tol 0.01 % | 7.14444774 en 7 iteraciones |
| Newton-Raphson | `x³ - 2x + 1` | x₀ = -1.5, tol 0.5 % | -1.61803401 en 3 iteraciones |

Son exactamente los mismos números que imprimen los scripts de `original/`.

## Diferencias con los scripts originales

Los tres métodos ya estaban **correctos**; al pasarlos a la interfaz se
corrigieron estos detalles:

1. **Newton no mostraba su raíz en la gráfica.** Graficaba de 0 a 2, pero
   desde x₀ = -1.5 converge a -1.618, fuera del dibujo. Ahora el rango se
   calcula para incluir el punto inicial y la raíz.
2. **Newton fallaba si la derivada se anulaba** (`ZeroDivisionError`, por
   ejemplo en x = ±0.8165 con la cúbica). Ahora avisa y sugiere otro x₀.
3. **Ninguno avisaba si no convergía**: al agotar las iteraciones daban la
   última aproximación como si fuera la raíz buena. Ahora se indica el estado.
4. Bisección y Falsa Posición no cortaban al encontrar `f(c) = 0` exacto.
5. El comentario decía `0.1 %` cuando `et = 0.01` es `0.01 %`.
