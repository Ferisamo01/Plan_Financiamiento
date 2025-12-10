from flask import Flask, render_template, request, jsonify
import requests
from variables import tasas, edad
import os
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)

# ==============================
# Páginas
# ==============================


def obtener_token():
    url = "https://login.salesforce.com/services/oauth2/token"

    client_id = os.getenv("SALESFORCE_CLIENT_ID")
    client_secret = os.getenv("SALESFORCE_CLIENT_SECRET")

    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }

    response = requests.post(url, data=data)
    return response.json()

print("Hola", obtener_token())

@app.post("/salesforce/cliente")
def consultar_cliente_salesforce():
    #url = 
    #token =
    
    try:
        data = request.get_json()

        dni = data.get("numero_id")
        print("DNI:",dni)
        if not dni:
            return jsonify({"error": "Falta DNI"}), 400

        print("Buscando cliente con DNI:", dni)

        return jsonify({"found": False}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/formulario')
def formulario():
    return render_template('formulario.html')


@app.route('/resultados')
def resultados():
    return render_template('resultados.html')

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
        otras_propiedades = data.get("otras_propiedades", {})
        lista_hijos = data.get("hijos", [])
        lista_inversiones = data.get("inversiones", [])
        lista_propiedades = data.get("propiedades", [])
        lista_participaciones = data.get("participaciones", [])
        perfil_riesgo = data.get("perfil_riesgo", "")
        #tasa = tasas(perfil_riesgo)
        gastos = data.get("gastos", {})
        titular = data.get("titular", {})
        
        tasa =  to_float(data.get("pensiones", {}).get("porcentaje_pension"))
        inflacion = to_float(data.get("pensiones",{}).get("inflacion_porcentual"))
        print("Perfil de riesgo:", perfil_riesgo, tasa)

        #activos_liquidos = data.get("activos_liquidos", {})
        #activos_no_liquidos = data.get("activos_no_liquidos", {})
        #pensiones = data.get("pensiones", {})
        #ingresos_futuros = data.get("ingresos_futuros", {})
        #ingresos_adicionales = data.get("ingresos_adicionales", {})
        #ingresos_extraordinarios = data.get("ingresos_extraordinarios", {})
        #herencias = data.get("herencias", {})
        

        

        # Convertir valores a float (si vienen vacíos o texto, usar 0)
        def to_float(v):
            try:
                return float(v)
            except (TypeError, ValueError):
                return 0.0
            
        def to_bool(v):
            return str(v).lower() == "true"
            
        educacion_hijos = sum(to_float(hijo.get("costo_total")) for hijo in lista_hijos)

        ahorros = to_float(patrimonio.get("ahorros_corrientes"))

        inversiones_on = sum(
            to_float(inv.get("valor"))
            for inv in lista_inversiones
            if not to_bool(inv.get("extranjera"))
        )

        inversiones_off = sum(
            to_float(inv.get("valor"))
            for inv in lista_inversiones
            if to_bool(inv.get("extranjera"))
        )

        propiedades_on = sum(
            to_float(prop.get("valor"))
            for prop in lista_propiedades
            if not to_bool(prop.get("extranjera"))
        )

        propiedades_off = sum(
            to_float(prop.get("valor"))
            for prop in lista_propiedades
            if to_bool(prop.get("extranjera"))
        )

        otras_propiedades_valor = (
            to_float(otras_propiedades.get("otros_inmuebles")) +
            to_float(otras_propiedades.get("inmuebles_inversion")) 
        )

        activos_liquidos = ahorros + inversiones_on + inversiones_off
        activos_no_liquidos = propiedades_on + propiedades_off + otras_propiedades_valor

        anhos_aporte = to_float(titular.get("edad_jubilacion")) - edad(titular.get("fecha_nacimiento"))
        pensiones = (
            to_float(data.get("pensiones", {}).get("valor_fondo")) * ((1 + tasa) ** anhos_aporte)
        ) + (
            to_float(patrimonio.get("sueldo_titular", 0)) * 0.10 * (((1 + tasa) ** anhos_aporte - 1) / tasa)
        )


        ingreso_futuros = (
            to_float(patrimonio.get("sueldo_titular")) +
            to_float(patrimonio.get("utilidades_bonos"))
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

        ahorro_neto = ingreso_futuros - gasto_total

        # ===== Crear respuesta simulada =====
        respuesta = {
            "ingresos_totales": round(ingreso_futuros, 2),
            "gastos_totales": round(gasto_total, 2),
            "ahorro_neto": round(ahorro_neto, 2),
            "activos_liquidos": round(activos_liquidos, 2),
            "activos_no_liquidos": round(activos_no_liquidos, 2),
            "pensiones": round(pensiones, 2),
            "graficos_html": f"""
                <div style='margin-top:20px'>
                    <h4>Visualización rápida:</h4>
                    <p>Ingresos: S/. {round(ingreso_futuros,2)}</p>
                    <p>Gastos: S/. {round(gasto_total,2)}</p>
                    <p>Ahorro Neto: S/. {round(ahorro_neto,2)}</p>
                    <p>Activos Líquidos: S/. {round(activos_liquidos,2)}</p>
                    <p>Activos No Líquidos: S/. {round(activos_no_liquidos,2)}</p>
                    <p>AFP + Futuros aportes: S/. {round(pensiones,2)}</p>
                </div>
            """
        }
        print("✅ Cálculos realizados:", respuesta)

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
