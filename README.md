# Métodos Numéricos — Proyecto de Análisis Numérico

Interfaz gráfica para hallar raíces de una función y calcular integrales
definidas. **La función f(x) la escribe el usuario**: no está fija en el código.

Métodos disponibles:

| Grupo | Método |
|---|---|
| Raíces de ecuaciones | Bisección, Falsa Posición, Newton-Raphson y Müller |
| Integración numérica | Regla del Trapecio y Regla de Simpson 1/3 (se elige con un selector) |

La estructura ya está lista para agregar el problema de aplicación.

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
| Cambiar de método fácilmente | Paso 1 de la columna izquierda; la f(x) escrita **se conserva** y se recalcula sola |
| Ver las iteraciones | Tabla inferior, con todas las columnas del método y el error de cada paso |
| Seguir una iteración en la gráfica | Al elegir una fila de la tabla (o moverse con ↑ ↓) se dibuja esa iteración: el intervalo, la tangente, la parábola o el punto. `Esc` la quita |
| Escribir la función | Paso 2; mientras se escribe se muestra cómo se entendió (y f'(x) en Newton) |
| Ejemplos resueltos | Desplegable arriba a la derecha: llena todos los campos y calcula |

### Müller

Tabla completa, con las 15 cantidades de cada iteración:

    x0  x1  x2  f(x0)  f(x1)  f(x2)  h0  h1  δ0  δ1  a  b  c  x3  ea %

    h0 = x1 - x0              h1 = x2 - x1
    δ0 = (f(x1) - f(x0))/h0   δ1 = (f(x2) - f(x1))/h1
    a = (δ1 - δ0)/(h1 + h0)   b = a·h1 + δ1   c = f(x2)
    x3 = x2 - 2c / (b ± √(b² - 4ac))     (el signo de ± igual al de b)

Si b² - 4ac sale negativo la siguiente aproximación sería compleja; el
programa lo avisa y pide otros puntos iniciales.

### Integración

Se dan a, b y el número de segmentos n. La tabla muestra cada punto xᵢ, f(xᵢ),
su coeficiente (1, 2, ..., 2, 1 en el trapecio; 1, 4, 2, ..., 4, 1 en Simpson) y
el producto. Además del resultado se muestra el **valor verdadero** (calculado
con cuadratura de alta precisión) y el **error verdadero εt**. Simpson 1/3
necesita n par.

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
                         + integral de referencia (mpmath)
  resultado.py           estructuras comunes: Iteracion, Resultado, ResultadoIntegral,
                         Parametro, Columna
  validacion.py          validaciones y mensajes de error compartidos
metodos/
  cerrados.py            bucle común de los métodos cerrados
  biseccion.py           c = (a + b) / 2
  falsa_posicion.py      c = b - f(b)(a - b) / (f(a) - f(b))
  newton_raphson.py      x(i+1) = x(i) - f(x(i)) / f'(x(i))
  muller.py              x3 = x2 - 2c / (b ± √(b² - 4ac))
  integracion.py         reglas del Trapecio y de Simpson 1/3
gui/
  tema.py                paleta, tipografías y escala de pantalla
  app.py                 ventana principal
  panel_controles.py     columna izquierda (método, f(x), datos)
  panel_grafica.py       gráfica de matplotlib embebida
  panel_tabla.py         resultado y tabla de iteraciones
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
2. Definir `NOMBRE`, `CLAVE`, `TIPO`, `GRAFICA`, `RESUMEN`, `FORMULA`,
   `PARAMETROS`, `COLUMNAS` y la función
   `ejecutar(funcion, parametros, tol_pct, max_iter)`.
3. Agregarlo a la lista `METODOS` de `metodos/__init__.py`.

`TIPO` decide en qué grupo aparece el botón (`cerrado`, `abierto` o
`integracion`) y `GRAFICA` qué se dibuja (`intervalo`, `tangentes`,
`parabolas` o `area`). Opcionales: `USA_TOLERANCIA = False` si no itera,
`USA_DERIVADA = True` si necesita f'(x), y `explicacion(parametros)` si el
título o la fórmula cambian según lo que elija el usuario. Un `Parametro` con
`opciones` se dibuja como selector en vez de caja de texto.

No hay que tocar la interfaz: el botón, los campos y las columnas aparecen solos.

### Aspecto

Los datos se piden sobre una "pizarra" verde, en el orden en que se resuelve
un ejercicio (método, función, datos), y la solución se dibuja en papel
milimetrado con la respuesta en rojo. Todos los colores y letras están en
`gui/tema.py`.

## Comprobación

```
python pruebas.py
```

Verifica los métodos contra los resultados de los scripts originales, contra
los ejemplos del libro de Chapra y contra raíces conocidas:

| Método | Función | Datos | Resultado |
|---|---|---|---|
| Bisección | `-0.4x² + 2.2x + 4.7` | [5, 10], tol 0.01 % | 7.14416504 en 13 iteraciones |
| Falsa Posición | `-0.4x² + 2.2x + 4.7` | [5, 10], tol 0.01 % | 7.14444774 en 7 iteraciones |
| Newton-Raphson | `x³ - 2x + 1` | x₀ = -1.5, tol 0.5 % | -1.61803401 en 3 iteraciones |
| Müller | `x³ - 13x - 12` | 4.5, 5.5, 5 | 3.976487, 4.001050, 4.000001, 4 (Chapra, ej. 6.8) |
| Trapecio | `0.2 + 25x - 200x² + 675x³ - 900x⁴ + 400x⁵` | [0, 0.8], n = 1, 2, 4 | 0.1728, 1.0688, 1.4848 |
| Simpson 1/3 | el mismo polinomio | [0, 0.8], n = 2, 4 | 1.367467, 1.623467 (verdadero 1.640533) |

Los tres primeros son exactamente los mismos números que imprimen los
scripts de `original/`.

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
