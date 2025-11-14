from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

# ==============================
# Páginas
# ==============================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/formulario')
def formulario():
    return render_template('formulario.html')


# ==============================
# Ruta que recibe el JSON del front
# ==============================
@app.route('/guardar_datos', methods=['POST'])
def guardar_datos():
    try:
        data = request.get_json(force=True)
        print("📦 Datos recibidos:", data)  # para depuración

        # ===== Validación mínima =====
        if not data or not isinstance(data, dict):
            return jsonify({"error": "No se recibieron datos válidos"}), 400

        # ===== Simulación de cálculos financieros =====
        patrimonio = data.get("patrimonio", {})
        gastos = data.get("gastos", {})

        # Convertir valores a float (si vienen vacíos o texto, usar 0)
        def to_float(v):
            try:
                return float(v)
            except (TypeError, ValueError):
                return 0.0

        ingreso_total = (
            to_float(patrimonio.get("sueldo_titular")) +
            to_float(patrimonio.get("ingreso_promedio")) +
            to_float(patrimonio.get("alquileres")) +
            to_float(patrimonio.get("dividendos")) +
            to_float(patrimonio.get("ahorro_familiar"))
        )

        gasto_total = (
            to_float(gastos.get("alquiler")) +
            to_float(gastos.get("alimentacion")) +
            to_float(gastos.get("servicios")) +
            to_float(gastos.get("transporte")) +
            to_float(gastos.get("otros")) +
            to_float(gastos.get("estilos")) +
            to_float(gastos.get("viajes")) +
            to_float(gastos.get("seguro")) +
            to_float(gastos.get("cambios"))
        )

        ahorro_neto = ingreso_total - gasto_total

        # ===== Crear respuesta simulada =====
        respuesta = {
            "ingresos_totales": round(ingreso_total, 2),
            "gastos_totales": round(gasto_total, 2),
            "ahorro_neto": round(ahorro_neto, 2),
            "graficos_html": f"""
                <div style='margin-top:20px'>
                    <h4>Visualización rápida:</h4>
                    <p>Ingresos: S/. {round(ingreso_total,2)}</p>
                    <p>Gastos: S/. {round(gasto_total,2)}</p>
                    <p>Ahorro Neto: S/. {round(ahorro_neto,2)}</p>
                </div>
            """
        }

        return jsonify(respuesta)

    except Exception as e:
        print("❌ Error al procesar datos:", e)
        return jsonify({"error": str(e)}), 500


# ==============================
# Ruta futura: generar PDF
# ==============================
@app.route('/generar_pdf', methods=['POST'])
def generar_pdf():
    data = request.get_json(force=True)
    # Aquí más adelante implementaremos la lógica de PDF
    return jsonify({"status": "success", "message": "PDF generado (simulado)"})


# ==============================
# Ejecución
# ==============================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
