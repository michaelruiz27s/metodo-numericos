import numpy as np
import matplotlib.pyplot as plt

# Entrada de función
funcion_str = input("Ingresa la función en términos de x (por ejemplo: x**3 - 5*x + 3): ")

def f(x):
    try:
        return eval(funcion_str, {"x": x, "np": np})
    except Exception as e:
        print("Error al evaluar la función:", e)
        return np.nan

# Entrada de valores
x_A = float(input("Ingresa el valor de x_A: "))
x_B = float(input("Ingresa el valor de x_B: "))
y_A = f(x_A)
y_B = f(x_B)
c = (x_A + x_B) / 2
y_C = f(c)

# Rango de la función amplio como GeoGebra
x = np.linspace(-55, 125, 1000)
y = f(x)

# Gráfica
plt.plot(x, y, label=f'f(x) = {funcion_str}', linewidth=1.5)
plt.plot(x_A, y_A, 'ro', label=f'A = ({x_A}, f({x_A})) = ({x_A}, {y_A:.3f})')
plt.plot(x_B, y_B, 'go', label=f'B = ({x_B}, f({x_B})) = ({x_B}, {y_B:.3f})')
plt.plot(c, y_C, 'bo', label=f'C = (({x_A} + {x_B})/2, f(c)) = ({c:.3f}, {y_C:.3f})')

# (Eliminamos la línea azul vertical en x = c)

# Ejes y cuadrícula
plt.axhline(0, color='black', linewidth=0.5)
plt.axvline(0, color='black', linewidth=0.5)
plt.grid(True)

# Ajustar ejes como GeoGebra
plt.xlim(-55, 126)
plt.ylim(-66, 81)

# Etiquetas
plt.title('Vista completa como GeoGebra')
plt.xlabel('x')
plt.ylabel('f(x)')
plt.legend()
plt.tight_layout()
plt.show()
