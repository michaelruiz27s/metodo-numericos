from flask import Blueprint, request, jsonify
import math
import re
import mysql.connector
import plotly.graph_objs as go
import plotly.io as pio
import numpy as np
import os



falsa_bp = Blueprint('falsa_posicion', __name__)

@falsa_bp.route('/falsa-posicion', methods=['POST'])
def ejecutar_falsa_posicion():
    try:
        funcion = request.form['funcion']
        xa = float(request.form['xa'])
        xb = float(request.form['xb'])
        xa_original = xa
        xb_original = xb
        es = float(request.form['es'])
        ejercicio = request.form['ejercicio']
        max_iter = 100

        def aplicar_reemplazos(s):
            s = s.replace("raiz", "sqrt")
            s = s.replace("ln", "log_ln_")
            s = s.replace("log(", "log10(")
            s = s.replace("log_ln_", "log")
            s = s.replace("sen", "sin")
            s = s.replace("cos", "cos")
            s = s.replace("tan", "tan")
            s = s.replace("atan", "atan")
            s = s.replace("arctan", "atan")
            s = s.replace("arcsin", "asin")
            s = s.replace("arccos", "acos")
            s = s.replace("^", "**")
            s = re.sub(r'e\*\*(\(?[^\)\+\-\*/]+?\)?)', r'exp(\1)', s)
            return s

        funcion = aplicar_reemplazos(funcion)

        allowed_names = {name: getattr(math, name) for name in dir(math) if not name.startswith("__")}
        allowed_names["x"] = 0

        def f(x):
            allowed_names["x"] = x
            return eval(funcion, {"__builtins__": None}, allowed_names)

        resultados = []
        Xr_anterior = 0
        i = 1

        while True:
            fXa = f(xa)
            fXb = f(xb)

            if abs(fXa - fXb) < 1e-12:
                raise ValueError("División por cero detectada durante el cálculo de Xr.")

            xr = xb - (fXb * (xa - xb)) / (fXa - fXb)
            fXr = f(xr)

            ea = 0 if i == 1 else abs((xr - Xr_anterior) / xr) * 100
            resultados.append((int(ejercicio), i, xa, xb, fXa, fXb, xr, fXr, round(ea, 4)))

            if ea < es and i > 1:
                break
            if i >= max_iter:
                break

            Xr_anterior = xr
            if fXa * fXr < 0:
                xb = xr
            else:
                xa = xr
            i += 1

        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="metodos_numericos")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM metodo_falsa_posicion WHERE ejercicio = %s", (ejercicio,))
        for fila in resultados:
            cursor.execute("""
                INSERT INTO metodo_falsa_posicion 
                (ejercicio, iteracion, xa, xb, fxa, fxb, xr, fxr, ea)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, fila)

        conn.commit()
        cursor.close()
        conn.close()
        # 📈 Gráfica estilo GeoGebra para Falsa Posición
        try:
            x_vals = np.linspace(xa_original - 10, xb_original + 10, 500)
            y_vals = [f(x) for x in x_vals]

            xr = xb_original - (f(xb_original) * (xa_original - xb_original)) / (f(xa_original) - f(xb_original))

            trace_func = go.Scatter(x=x_vals, y=y_vals, mode='lines', name=f"f(x) = {funcion}", line=dict(color='blue'))
            trace_A = go.Scatter(x=[xa_original], y=[f(xa_original)], mode='markers',
                              name=f"A = ({xa_original:.2f}, {f(xa_original):.3f})", text=['A'], marker=dict(color='red', size=10), textposition="top center")
            trace_B = go.Scatter(x=[xb_original], y=[f(xb_original)], mode='markers',
                               name=f"B = ({xb_original:.2f}, {f(xb_original):.3f})", marker=dict(color='green', size=10), textposition="top center")
            trace_C = go.Scatter(x=[xr], y=[f(xr)], mode='markers',
                                 name=f"C = ({xr:.2f}, {f(xr):.3f})", text=['C'], marker=dict(color='orange', size=10), textposition="top center")

            layout = go.Layout(
                title='Gráfica del Método de Falsa Posición',
                plot_bgcolor='white',       # Fondo blanco
                paper_bgcolor='white',      # Fondo blanco alrededor
                xaxis=dict(
                    title='x',
                    range=[-55, 125],
                    showgrid=True,
                    gridcolor='lightgray',   # Cuadrícula gris clara
                    zeroline=True,
                    zerolinecolor='black',
                    zerolinewidth=2
                ),
                yaxis=dict(
                    title='f(x)',
                    range=[-66, 81],
                    showgrid=True,
                    gridcolor='lightgray',
                    zeroline=True,
                    zerolinecolor='black',
                    zerolinewidth=2
                ),
                shapes=[
                    # Línea vertical en x = 0
                    dict(type='line', x0=0, y0=-1000, x1=0, y1=1000,
                        line=dict(color='black', width=2)),
                    # Línea horizontal en y = 0
                    dict(type='line', x0=-1000, y0=0, x1=1000, y1=0,
                        line=dict(color='black', width=2))
                ],
                showlegend=True,
                hovermode='closest'
            )

            fig = go.Figure(data=[trace_func, trace_A, trace_B, trace_C], layout=layout)

            os.makedirs("static/imagenes", exist_ok=True)
            html_path = f"static/imagenes/falsa_posicion_{ejercicio}.html"
            pio.write_html(fig, file=html_path, auto_open=False)

        except Exception as err:
            print("❌ Error generando gráfica Falsa Posición:", err)
            html_path = ""

        return jsonify({
            "mensaje": "✅ Cálculos de falsa posición realizados y guardados correctamente.",
            "imagen": "/" + html_path
        })

    except Exception as e:
        return f"❌ Error: {str(e)}", 500




@falsa_bp.route('/resultados-falsa-posicion')
def ver_resultados_falsa_posicion():
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="metodos_numericos")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ejercicio, iteracion, xa, xb, fxa, fxb, xr, fxr, ea
            FROM metodo_falsa_posicion
            ORDER BY ejercicio ASC, iteracion ASC
        """)
        filas = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(filas)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@falsa_bp.route('/eliminar-falsa-posicion/<int:ejercicio>', methods=['DELETE'])
def eliminar_falsa_posicion(ejercicio):
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="metodos_numericos")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM metodo_falsa_posicion WHERE ejercicio = %s", (ejercicio,))
        conn.commit()
        cursor.close()
        conn.close()
        return f"Registros del ejercicio #{ejercicio} eliminados correctamente."
    except Exception as e:
        return f"❌ Error: {str(e)}", 500

@falsa_bp.route('/actualizar-falsa-posicion', methods=['POST'])
def actualizar_falsa_posicion():
    ejercicio = int(request.form['ejercicio'])

    conn = mysql.connector.connect(host="localhost", user="root", password="root", database="metodos_numericos")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM metodo_falsa_posicion WHERE ejercicio = %s", (ejercicio,))
    conn.commit()
    cursor.close()
    conn.close()

    request.form = request.form.copy()
    request.form['ejercicio'] = str(ejercicio)

    return ejecutar_falsa_posicion()
    
@falsa_bp.route('/buscar_ejercicio_falsa/<int:ejercicio>', methods=['GET'])
def buscar_ejercicio_falsa(ejercicio):
    try:
        conn = mysql.connector.connect(
            host="localhost", user="root", password="root", database="metodos_numericos")
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT ejercicio, iteracion, xa, xb, fxa, fxb, xr, fxr, ea
            FROM metodo_falsa_posicion
            WHERE ejercicio = %s
            ORDER BY iteracion ASC
        """, (ejercicio,))
        
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify(resultados)
    except Exception as e:
        return jsonify({"error": str(e)}), 500



