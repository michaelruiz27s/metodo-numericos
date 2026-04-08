from flask import Blueprint, request, jsonify
import math
import mysql.connector
import numpy as np

newton_sistemas_bp = Blueprint('newton_sistemas', __name__)

@newton_sistemas_bp.route('/newton-sistemas', methods=['POST'])
def ejecutar_newton_sistemas():
    try:
        funciones_input = request.form.getlist('vector_funciones')
        jacobiano_input = request.form.getlist('jacobiano')
        x_inicial = float(request.form['x_inicial'])  # ✅ captura x inicial
        y_inicial = float(request.form['y_inicial'])  # ✅ captura y inicial
        x = np.array([x_inicial, y_inicial], dtype=float)  # ✅ arma el vector [x, y]
        es = float(request.form['es'])
        ejercicio = int(request.form['ejercicio'])
        max_iter = 100

        def aplicar_reemplazos(expr):
            expr = expr.replace("raiz", "sqrt")
            expr = expr.replace("sen", "sin")
            expr = expr.replace("cos", "cos")
            expr = expr.replace("tan", "tan")
            expr = expr.replace("^", "**")
            return expr

        funciones = [aplicar_reemplazos(f) for f in funciones_input]
        jacobiano = [aplicar_reemplazos(j) for j in jacobiano_input]

        n = 2 

        allowed_names = {name: getattr(math, name) for name in dir(math) if not name.startswith("__")}

        def evaluar_funciones(x):
            resultado = []
            for f in funciones:
                contexto = allowed_names.copy() 
                contexto.update({"x": x[0], "y": x[1]})
                try:
                    resultado.append(eval(f, {"__builtins__": None}, contexto))
                except Exception as e:
                    raise ValueError(f"Error evaluando función '{f}' con x={x[0]}, y={x[1]}: {str(e)}")
            return np.array(resultado)



        def evaluar_jacobiano(x):
            resultado = []
            for fila in range(n):
                fila_jacobiana = []
                for col in range(n):
                    expr = jacobiano[fila * n + col]
                    allowed_names["x"] = x[0]
                    allowed_names["y"] = x[1]
                    fila_jacobiana.append(eval(expr, {"__builtins__": None}, allowed_names))
                resultado.append(fila_jacobiana)
            return np.array(resultado)

        resultados = []
        i = 1

        while i <= max_iter:
            try:
                F = evaluar_funciones(x)
                J = evaluar_jacobiano(x)

                if np.linalg.det(J) == 0:
                    return "❌ Error: Jacobiano singular, no se puede invertir.", 400

                J_inv = np.linalg.inv(J)
                delta = np.dot(J_inv, F)
                x_nueva = x - delta

                if i == 1:
                    e1, e2 = 0, 0
                else:
                    e1 = abs((x_nueva[0] - x[0]) / x_nueva[0]) * 100 if x_nueva[0] != 0 else 0
                    e2 = abs((x_nueva[1] - x[1]) / x_nueva[1]) * 100 if x_nueva[1] != 0 else 0

                fila = (
                    ejercicio, i,
                    x[0], x[1],
                    F[0], F[1],
                    J[0, 0], J[0, 1], J[1, 0], J[1, 1],
                    J_inv[0, 0], J_inv[0, 1], J_inv[1, 0], J_inv[1, 1],
                    x_nueva[0], x_nueva[1],
                    e1, e2
                )
                resultados.append(fila)

                if i > 1 and max(e1, e2) < es:
                    break

                x = x_nueva
                i += 1

            except ValueError as e:
             return f"❌ Error de dominio durante la iteración {i}: {str(e)}", 400



        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="metodos_numericos")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM metodo_newton_sistemas WHERE ejercicio = %s", (ejercicio,))
        for fila in resultados:
            cursor.execute("""
                INSERT INTO metodo_newton_sistemas 
                (ejercicio, iteracion, x, y, fx, fy, 
                 j11, j12, j21, j22, 
                 inv_j11, inv_j12, inv_j21, inv_j22, 
                 delta_x, delta_y, e1, e2)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, fila)

        conn.commit()
        cursor.close()
        conn.close()

        return "✅ Cálculos Newton Sistemas guardados correctamente."

    except Exception as e:
        return f"❌ Error: {str(e)}", 500

@newton_sistemas_bp.route('/resultados-newton-sistemas')
def resultados_newton_sistemas():
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="metodos_numericos")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ejercicio, iteracion, x, y, fx, fy,
                   j11, j12, j21, j22,
                   inv_j11, inv_j12, inv_j21, inv_j22,
                   delta_x, delta_y, e1, e2
            FROM metodo_newton_sistemas
            ORDER BY ejercicio ASC, iteracion ASC
        """)
        filas = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(filas)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@newton_sistemas_bp.route('/eliminar-newton-sistemas/<int:ejercicio>', methods=['DELETE'])
def eliminar_newton_sistemas(ejercicio):
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="metodos_numericos")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM metodo_newton_sistemas WHERE ejercicio = %s", (ejercicio,))
        conn.commit()
        cursor.close()
        conn.close()
        return f"✅ Registros del ejercicio #{ejercicio} eliminados correctamente."
    except Exception as e:
        return f"❌ Error: {str(e)}", 500

@newton_sistemas_bp.route('/actualizar-newton-sistemas', methods=['POST'])
def actualizar_newton_sistemas():
    try:
        funciones_input = request.form.getlist('vector_funciones')
        jacobiano_input = request.form.getlist('jacobiano')
        x_inicial = float(request.form['x_inicial'])
        y_inicial = float(request.form['y_inicial'])
        x = np.array([x_inicial, y_inicial], dtype=float)
        es = float(request.form['es'])
        ejercicio = int(request.form['ejercicio'])
        max_iter = 100

        def aplicar_reemplazos(expr):
            expr = expr.replace("raiz", "sqrt").replace("sen", "sin").replace("cos", "cos")
            expr = expr.replace("tan", "tan").replace("^", "**")
            return expr

        funciones = [aplicar_reemplazos(f) for f in funciones_input]
        jacobiano = [aplicar_reemplazos(j) for j in jacobiano_input]

        allowed_names = {name: getattr(math, name) for name in dir(math) if not name.startswith("__")}

        def evaluar_funciones(x):
            resultado = []
            for f in funciones:
                allowed_names.update({"x": x[0], "y": x[1]})
                resultado.append(eval(f, {"__builtins__": None}, allowed_names))
            return np.array(resultado)

        def evaluar_jacobiano(x):
            resultado = []
            for fila in range(2):
                fila_jacobiana = []
                for col in range(2):
                    expr = jacobiano[fila * 2 + col]
                    allowed_names.update({"x": x[0], "y": x[1]})
                    fila_jacobiana.append(eval(expr, {"__builtins__": None}, allowed_names))
                resultado.append(fila_jacobiana)
            return np.array(resultado)

        resultados = []
        i = 1

        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="metodos_numericos")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM metodo_newton_sistemas WHERE ejercicio = %s", (ejercicio,))
        conn.commit()

        while i <= max_iter:
            F = evaluar_funciones(x)
            J = evaluar_jacobiano(x)

            if np.linalg.det(J) == 0:
                return "❌ Error: Jacobiano singular, no se puede invertir.", 400

            J_inv = np.linalg.inv(J)
            delta = np.dot(J_inv, F)
            x_nueva = x - delta

            if i == 1:
                e1, e2 = 0, 0
            else:
                e1 = abs((x_nueva[0] - x[0]) / x_nueva[0]) * 100 if x_nueva[0] != 0 else 0
                e2 = abs((x_nueva[1] - x[1]) / x_nueva[1]) * 100 if x_nueva[1] != 0 else 0

            fila = (
                ejercicio, i,
                x[0], x[1],
                F[0], F[1],
                J[0, 0], J[0, 1], J[1, 0], J[1, 1],
                J_inv[0, 0], J_inv[0, 1], J_inv[1, 0], J_inv[1, 1],
                delta[0], delta[1],
                e1, e2
            )
            cursor.execute("""
                INSERT INTO metodo_newton_sistemas 
                (ejercicio, iteracion, x, y, fx, fy,
                 j11, j12, j21, j22,
                 inv_j11, inv_j12, inv_j21, inv_j22,
                 delta_x, delta_y, e1, e2)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, fila)

            conn.commit()

            if i > 1 and max(e1, e2) < es:
                break

            x = x_nueva
            i += 1

        cursor.close()
        conn.close()

        return "✅ Actualización Newton Sistemas exitosa."

    except Exception as e:
        return f"❌ Error al actualizar: {str(e)}", 500
