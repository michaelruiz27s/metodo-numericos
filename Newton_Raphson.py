from flask import Blueprint, request, jsonify
import math
import re
import mysql.connector

newton_bp = Blueprint('newton_raphson', __name__)

@newton_bp.route('/newton-raphson', methods=['POST'])
def ejecutar_newton_raphson():
    try:
        funcion = request.form['funcion']
        derivada = request.form['derivada']
        x0 = float(request.form['x0'])
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
            return s

        funcion = aplicar_reemplazos(funcion)
        derivada = aplicar_reemplazos(derivada)

        allowed_names = {name: getattr(math, name) for name in dir(math) if not name.startswith("__")}
        allowed_names["x"] = 0

        def f(x):
            allowed_names["x"] = x
            return eval(funcion, {"__builtins__": None}, allowed_names)

        def df(x):
            allowed_names["x"] = x
            return eval(derivada, {"__builtins__": None}, allowed_names)

        resultados = []
        i = 1
        xi = x0
        ea = 0
        fxi = f(xi)
        dfxi = df(xi)
        xi1 = xi - fxi / dfxi
        resultados.append((int(ejercicio), i, xi, fxi, dfxi, xi1, ea))

        i += 1
        while i <= max_iter:
            xi = xi1
            fxi = f(xi)
            dfxi = df(xi)

            if dfxi == 0:
                raise ZeroDivisionError(f"Derivada es cero en x = {xi}")

            xi1 = xi - fxi / dfxi
            ea = abs((xi1 - xi) / xi1) * 100 if xi1 != 0 else 0
            resultados.append((int(ejercicio), i, xi, fxi, dfxi, xi1, round(ea, 6)))

            if ea < es:
                break
            i += 1

        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="metodos_numericos")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM metodo_newton_raphson WHERE ejercicio = %s", (ejercicio,))
        for fila in resultados:
            cursor.execute("""
                INSERT INTO metodo_newton_raphson 
                (ejercicio, iteracion, xi, fxi, dfxi, xi1, ea)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, fila)

        conn.commit()
        cursor.close()
        conn.close()

        return "✅ Cálculos de Newton-Raphson realizados y guardados correctamente."

    except Exception as e:
        return f"❌ Error: {str(e)}", 500


@newton_bp.route('/resultados-newton-raphson')
def ver_resultados_newton_raphson():
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="metodos_numericos")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ejercicio, iteracion, xi, fxi, dfxi, xi1, ea
            FROM metodo_newton_raphson
            ORDER BY ejercicio ASC, iteracion ASC
        """)
        filas = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(filas)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@newton_bp.route('/eliminar-newton-raphson/<int:ejercicio>', methods=['DELETE'])
def eliminar_newton_raphson(ejercicio):
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="metodos_numericos")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM metodo_newton_raphson WHERE ejercicio = %s", (ejercicio,))
        conn.commit()
        cursor.close()
        conn.close()
        return f"✅ Registros del ejercicio #{ejercicio} eliminados correctamente."
    except Exception as e:
        return f"❌ Error: {str(e)}", 500


@newton_bp.route('/actualizar-newton-raphson', methods=['POST'])
def actualizar_newton_raphson():
    ejercicio = int(request.form['ejercicio'])

    conn = mysql.connector.connect(host="localhost", user="root", password="root", database="metodos_numericos")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM metodo_newton_raphson WHERE ejercicio = %s", (ejercicio,))
    conn.commit()
    cursor.close()
    conn.close()

    request.form = request.form.copy()
    request.form['ejercicio'] = str(ejercicio)

    return ejecutar_newton_raphson()
