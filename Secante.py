from flask import Blueprint, request, jsonify
import math
import re
import mysql.connector
import plotly.graph_objs as go    
import plotly.io as pio
import numpy as np
import os

secante_bp = Blueprint('secante', __name__)

@secante_bp.route('/secante', methods=['POST'])
def ejecutar_secante():
    try:
        funcion = request.form['funcion']
        x1 = float(request.form['x0'])
        x0 = float(request.form['x1'])
        es = float(request.form['es'])
        ejercicio = request.form['ejercicio']
        max_iter = 100

        def aplicar_reemplazos(f_str):
            f_str = f_str.replace("sen", "sin")
            f_str = f_str.replace("raiz", "sqrt")
            f_str = f_str.replace("ln", "log_ln_")
            f_str = f_str.replace("log(", "log10(")
            f_str = f_str.replace("log_ln_", "log")
            f_str = f_str.replace("arctan", "atan")
            f_str = f_str.replace("arcsin", "asin")
            f_str = f_str.replace("arccos", "acos")
            f_str = f_str.replace("^", "**")
            f_str = re.sub(r'e\*\*(\(?[^\)\+\-\*/]+?\)?)', r'exp(\1)', f_str)
            return f_str

        funcion = aplicar_reemplazos(funcion)

        allowed_names = {name: getattr(math, name) for name in dir(math) if not name.startswith("__")}
        allowed_names["x"] = 0

        def f(x):
            allowed_names["x"] = x
            return eval(funcion, {"__builtins__": None}, allowed_names)

        resultados = []
        i = 1
        ea = 100

        while i <= max_iter:
            fx0 = f(x0)
            fx1 = f(x1)

            if (fx1 - fx0) == 0:
                raise ValueError("División por cero detectada durante el cálculo.")

            x2 = x1 - fx1 * (x1 - x0) / (fx1 - fx0)

            if i == 1:
                ea = 0
            else:
                ea = abs((x2 - x1) / x2) * 100

            resultados.append((int(ejercicio), i, x0, x1, fx0, fx1, x2, round(ea, 6)))

            if ea < es and i > 1:
                break

            x0 = x1
            x1 = x2
            i += 1

        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="metodos_numericos")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM metodo_secante WHERE ejercicio = %s", (ejercicio,))
        for fila in resultados:
            cursor.execute("""
                INSERT INTO metodo_secante
                (ejercicio, iteracion, xi, xi_1, fxi, fxi_1, xi_t, ea)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, fila)

        conn.commit()
        cursor.close()
        conn.close()
 
# 📈 Gráfica estilo GeoGebra para la Secante
        try:
            # Guardamos los valores iniciales para graficar después
            x0_original = float(request.form['x0'])
            x1_original = float(request.form['x1'])

            # Calculamos x2 SOLO UNA VEZ como en GeoGebra
            f_x0 = f(x0_original)
            f_x1 = f(x1_original)
            x2_geo = x1_original - f_x1 * (x1_original - x0_original) / (f_x1 - f_x0)

            # Rango amplio y fijo para visualizar toda la forma de la función
            x_vals = np.linspace(-2000, 2000, 20000)
            x_vals_filtrados = []
            y_vals_filtrados = []

            for x in x_vals:
                try:
                    y = f(x)
                    # Solo agregamos puntos cuando el denominador no da error
                    if math.isfinite(y):
                        x_vals_filtrados.append(x)
                        y_vals_filtrados.append(y)
                    else:
                        x_vals_filtrados.append(x)
                        y_vals_filtrados.append(None)
                except Exception:
                    # En caso de división por cero o cualquier error
                    x_vals_filtrados.append(x)
                    y_vals_filtrados.append(None)


            trace_func = go.Scatter(
                x=x_vals_filtrados,
                y=y_vals_filtrados,
                mode='lines',
                name=f"f(x) = {funcion}",
                line=dict(color='blue')
            )

            # Graficar función y los puntos A, B, C
            trace_func = go.Scatter(x=x_vals_filtrados, y=y_vals_filtrados, mode='lines', name=f"f(x) = {funcion}", line=dict(color='blue'))
            trace_A = go.Scatter(x=[x1_original], y=[f(x1_original)], mode='markers',
                                name=f"A = ({x1_original:.2f}, {f(x1_original):.3f})",
                                marker=dict(color='red', size=10), text=['x₀'], textposition="top center")
            trace_B = go.Scatter(x=[x0_original], y=[f(x0_original)], mode='markers',
                                name=f"B = ({x0_original:.2f}, {f(x0_original):.3f})",
                                marker=dict(color='green', size=10), text=['x₁'], textposition="top center")
            trace_C = go.Scatter(x=[x2_geo], y=[f(x2_geo)], mode='markers',
                                name=f"C = ({x2_geo:.2f})",
                                marker=dict(color='orange', size=10), text=['x₂'], textposition="top center")
            

            layout = go.Layout(
                title='Gráfica del Método de la Secante',
                plot_bgcolor='white',
                paper_bgcolor='white',
                xaxis=dict(
                    title='x',
                    range=[-10, 10],
                    showgrid=True,
                    gridcolor='lightgray',
                    zeroline=True,
                    zerolinecolor='black',
                    zerolinewidth=2
                ),
                yaxis=dict(
                    title='f(x)',
                    range=[-10, 10],
                    showgrid=True,
                    gridcolor='lightgray',
                    zeroline=True,
                    zerolinecolor='black',
                    zerolinewidth=2
                ),
                shapes=[
                    dict(type='line', x0=0, y0=-1000, x1=0, y1=1000, line=dict(color='black', width=2)),
                    dict(type='line', x0=-1000, y0=0, x1=1000, y1=0, line=dict(color='black', width=2))
                ],
                showlegend=True,
                hovermode='closest'
            )


            fig = go.Figure(data=[trace_func, trace_A, trace_B, trace_C], layout=layout)

            os.makedirs("static/imagenes", exist_ok=True)
            html_path = f"static/imagenes/secante_{ejercicio}.html"
            pio.write_html(fig, file=html_path, auto_open=False)

        except Exception as err:
            print("❌ Error generando gráfica Secante:", err)
            html_path = ""



    except Exception as err:
        print("❌ Error generando gráfica de la secante:", err)

    return jsonify({
        "mensaje": "✅ Cálculos de la secante realizados y guardados correctamente.",
        "imagen": "/" + html_path
    })


@secante_bp.route('/resultados-secante')
def ver_resultados_secante():
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="metodos_numericos")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ejercicio, iteracion, xi, xi_1, fxi, fxi_1, xi_t, ea
            FROM metodo_secante
            ORDER BY ejercicio ASC, iteracion ASC
        """)

        filas = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(filas)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@secante_bp.route('/eliminar-secante/<int:ejercicio>', methods=['DELETE'])
def eliminar_secante(ejercicio):
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="metodos_numericos")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM metodo_secante WHERE ejercicio = %s", (ejercicio,))
        conn.commit()
        cursor.close()
        conn.close()
        return f"Registros del ejercicio #{ejercicio} eliminados correctamente."
    except Exception as e:
        return f"❌ Error: {str(e)}", 500

@secante_bp.route('/actualizar-secante', methods=['POST'])
def actualizar_secante():
    ejercicio = int(request.form['ejercicio'])

    conn = mysql.connector.connect(host="localhost", user="root", password="root", database="metodos_numericos")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM metodo_secante WHERE ejercicio = %s", (ejercicio,))
    conn.commit()
    cursor.close()
    conn.close()

    request.form = request.form.copy()
    request.form['ejercicio'] = str(ejercicio)

    return ejecutar_secante()

@secante_bp.route('/buscar_ejercicio_secante/<int:ejercicio>', methods=['GET'])
def buscar_ejercicio_secante(ejercicio):
    try:
        conn = mysql.connector.connect(
            host="localhost", user="root", password="root", database="metodos_numericos")
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT ejercicio, iteracion, xi, xi_1, fxi, fxi_1, xi_t, ea
            FROM metodo_secante
            WHERE ejercicio = %s
            ORDER BY iteracion ASC
        """, (ejercicio,))
        
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify(resultados)
    except Exception as e:
        return jsonify({"error": str(e)}), 500



