from flask import Blueprint, request, jsonify
import math
import mysql.connector
import plotly.graph_objs as go
import plotly.io as pio
import numpy as np
import os

puntofijo_bp = Blueprint('punto_fijo', __name__)

@puntofijo_bp.route('/punto-fijo', methods=['POST'])
def ejecutar_punto_fijo():
    try:
        funcion = request.form['funcion']
        xi = float(request.form['x0'])
        es = float(request.form['es'])
        ejercicio = request.form['ejercicio']
        max_iter = 100

        def aplicar_reemplazos(s):
            s = s.replace("raiz", "sqrt")
            s = s.replace("sen", "sin")
            s = s.replace("cos", "cos")
            s = s.replace("tan", "tan")
            s = s.replace("atan", "atan")
            s = s.replace("^", "**")
            s = s.replace("e", "exp")
            return s

        funcion = aplicar_reemplazos(funcion)

        allowed_names = {name: getattr(math, name) for name in dir(math) if not name.startswith("__")}
        allowed_names["x"] = 0

        def g(x):
            allowed_names["x"] = x
            return eval(funcion, {"__builtins__": None}, allowed_names)

        resultados = []
        i = 1
        x1 = g(xi)
        ea = 0
        resultados.append((int(ejercicio), i, xi, x1, ea))

        i += 1
        while i <= max_iter:
            xi_old = xi
            xi = x1
            x1 = g(xi)
            ea = abs((x1 - xi) / x1) * 100 if x1 != 0 else 0
            resultados.append((int(ejercicio), i, xi, x1, round(ea, 6)))
            if ea < es:
                break
            i += 1

        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="metodos_numericos")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM metodo_punto_fijo WHERE ejercicio = %s", (ejercicio,))
        for fila in resultados:
            cursor.execute("""
                INSERT INTO metodo_punto_fijo 
                (ejercicio, iteracion, xi, gxi, ea)
                VALUES (%s, %s, %s, %s, %s)
            """, fila)

        conn.commit()
        cursor.close()
        conn.close()

        try:
            x_vals = np.linspace(-5, 6, 500)  # Rango amplio como en GeoGebra
            y_vals = [g(x) for x in x_vals]

            x0 = resultados[0][2]  # xi de la primera iteración
            gx0 = resultados[0][3]  # gxi de la primera iteración


            trazo_funcion = go.Scatter(
                x=x_vals,
                y=y_vals,
                mode='lines',
                name="g(x) = " + request.form['funcion'],
                line=dict(color='blue')
            )

            punto_gx0 = go.Scatter(
                x=[x0],
                y=[gx0],
                mode='markers',
                name=f"({x0:.4f}, {gx0:.6f})",
                marker=dict(color='green', size=10)
            )

            shapes = [
                dict(type='line', x0=min(x_vals), x1=max(x_vals), y0=0, y1=0,
                    line=dict(color='black', width=1)),
                dict(type='line', x0=0, x1=0, y0=min(y_vals), y1=max(y_vals),
                    line=dict(color='black', width=1))
            ]

            fig = go.Figure(data=[trazo_funcion, punto_gx0])
            fig.update_layout(
                title=f'Método de Punto Fijo - Ejercicio {ejercicio}',
                xaxis_title='x',
                yaxis_title='y',
                plot_bgcolor='white',
                paper_bgcolor='white',
                shapes=shapes,
                showlegend=True
            )

            os.makedirs("static/imagenes", exist_ok=True)
            html_path = f"static/imagenes/punto_fijo_{ejercicio}.html"
            pio.write_html(fig, file=html_path, auto_open=False)

        except Exception as err:
            print("❌ Error generando gráfica:", err)
            html_path = ""

        return jsonify({
            "mensaje": "✅ Cálculos de punto fijo realizados y guardados correctamente.",
            "imagen": "/" + html_path
        })
    except Exception as e:
        return f"❌ Error: {str(e)}", 500

@puntofijo_bp.route('/resultados-punto-fijo')
def ver_resultados_punto_fijo():
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="metodos_numericos")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ejercicio, iteracion, xi, gxi, ea
            FROM metodo_punto_fijo
            ORDER BY ejercicio ASC, iteracion ASC
        """)
        filas = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(filas)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@puntofijo_bp.route('/eliminar-punto-fijo/<int:ejercicio>', methods=['DELETE'])
def eliminar_punto_fijo(ejercicio):
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="metodos_numericos")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM metodo_punto_fijo WHERE ejercicio = %s", (ejercicio,))
        conn.commit()
        cursor.close()
        conn.close()
        return f"Registros del ejercicio #{ejercicio} eliminados correctamente."
    except Exception as e:
        return f"❌ Error: {str(e)}", 500

@puntofijo_bp.route('/actualizar-punto-fijo', methods=['POST'])
def actualizar_punto_fijo():
    ejercicio = int(request.form['ejercicio'])

    conn = mysql.connector.connect(host="localhost", user="root", password="root", database="metodos_numericos")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM metodo_punto_fijo WHERE ejercicio = %s", (ejercicio,))
    conn.commit()
    cursor.close()
    conn.close()

    request.form = request.form.copy()
    request.form['ejercicio'] = str(ejercicio)

    return ejecutar_punto_fijo()


@puntofijo_bp.route('/buscar_ejercicio_puntofijo/<int:ejercicio>', methods=['GET'])
def buscar_ejercicio_puntofijo(ejercicio):
    try:
        conn = mysql.connector.connect(
            host="localhost", user="root", password="root", database="metodos_numericos")
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT ejercicio, iteracion, xi, gxi, ea
            FROM metodo_punto_fijo
            WHERE ejercicio = %s
            ORDER BY iteracion ASC
        """, (ejercicio,))

        resultados = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify(resultados)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
