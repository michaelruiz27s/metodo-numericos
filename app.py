from flask import Flask, send_file, send_from_directory
from Biseccion import biseccion_bp
from Falsa_Posicion import falsa_bp
from Punto_Fijo import puntofijo_bp
from Newton_Raphson import newton_bp
from Secante import secante_bp   # <-- ✅ Agregamos Secante
from Newton_Raphson_SENL import newton_sistemas_bp  # ✅ <<<< Nuevo Blueprint para Newton-Raphson Sistemas

app = Flask(__name__)

# Rutas estáticas
@app.route('/')
def index():
    return send_file("index.html")

@app.route('/style.css')
def estilo():
    return send_from_directory('.', 'style.css')

@app.route('/Funciones.js')
def funciones():
    return send_from_directory('.', 'Funciones.js')

# Registrar blueprints
app.register_blueprint(biseccion_bp)
app.register_blueprint(falsa_bp)
app.register_blueprint(puntofijo_bp)
app.register_blueprint(newton_bp)
app.register_blueprint(secante_bp)   # <-- ✅ Registramos el Blueprint de Secante
app.register_blueprint(newton_sistemas_bp)   # ✅ <<<< Aquí registras también el nuevo NR-SENL



if __name__ == '__main__':
    app.run(debug=True)

