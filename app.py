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

#print("Hola", obtener_token())

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

        def to_float(v):
            try:
                return float(v)
            except (TypeError, ValueError):
                return 0.0
            
        def to_bool(v):
            return str(v).lower() == "true"
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
        lista_creditos =  data.get("creditos", [])
        seguro_vida = data.get("seguro_vida") or {}

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

            
        educacion_hijos = sum(to_float(hijo.get("costo_total")) for hijo in lista_hijos)


        ahorros = to_float(patrimonio.get("ahorros_corrientes"))
        
        #Participaciones
        participaciones = sum(to_float(participacion.get("valor")) for participacion in lista_participaciones)

        #Inversiones
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

        inversiones_fija = sum(
            to_float(inv.get("valor")) * (to_float(inv.get("dist_fija")) / 100)
            for inv in lista_inversiones
        )

        inversiones_variable = sum(
            to_float(inv.get("valor")) * (to_float(inv.get("dist_variable")) / 100)
            for inv in lista_inversiones
        )

        inversiones_alternativos = sum(
            to_float(inv.get("valor")) * (to_float(inv.get("dist_alternativos")) / 100)
            for inv in lista_inversiones
        )

        inversiones_cash = sum(
            to_float(inv.get("valor")) * (to_float(inv.get("dist_cash")) / 100)
            for inv in lista_inversiones
        )



        #Propiedades
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

        ingresos_conyuge = 0.0

        #Conyuge
        if to_bool(titular.get("estado_civil") == "Casado"):
            conyuge = data.get("conyuge", {})
            ingresos_conyuge = to_float(conyuge.get("sueldo_titular_conyugue")) + to_float(conyuge.get("utilidades_titular_conyugue"))

        activos_liquidos = ahorros + inversiones_on + inversiones_off
        activos_no_liquidos = propiedades_on + propiedades_off + otras_propiedades_valor + participaciones

        anhos_aporte = 0.00
        
        if titular.get("situacion_laboral") != "Jubilado":
            anhos_aporte = to_float(titular.get("edad_jubilacion")) - edad(titular.get("fecha_nacimiento"))
        else:
            anhos_aporte = 0.00

        pensiones = (
            to_float(data.get("pensiones", {}).get("valor_fondo")) * ((1 + tasa) ** anhos_aporte)
        ) + (
            to_float(patrimonio.get("sueldo_titular", 0)) * 0.10 * (((1 + tasa) ** anhos_aporte - 1) / tasa)
        )


        ingreso_futuros = (
            to_float(patrimonio.get("sueldo_titular")) +
            to_float(patrimonio.get("utilidades_bonos")) +
            ingresos_conyuge
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

        ingresos_adicionales = (
            to_float(patrimonio.get("dividendos")) +
            to_float(patrimonio.get("otros_ingresos")) +
            to_float(patrimonio.get("ahorro_familiar"))
        
        )
        
        #Gastos
        
        deudas = sum(to_float(credito.get("saldo_actual")) for credito in lista_creditos)
        
        gastos_basicos = (
            to_float(gastos.get("alquiler")) +
            to_float(gastos.get("alimentacion")) +
            to_float(gastos.get("servicios")) +
            to_float(gastos.get("transporte")) + 
            to_float(gastos.get("seguro") )
        )

        gasto_seguro_vida = (
            to_float(seguro_vida.get("pago"))
        )

        gastos_estilo_vida = (
            to_float(gastos.get("estilos"))
        )

        gastos_viajes = (
            to_float(gastos.get("viajes"))
        )

        gastos_educacion_hijos = (
            educacion_hijos
        )

        gastos_extraordinarios = (
            to_float(gastos.get("otros"))
        )

        #ahorro_neto = ingreso_futuros - gasto_total

        # ===== Crear respuesta simulada =====
        respuesta = {

            #ingresos
           
            "activos_liquidos": round(activos_liquidos, 2),
            "ahorros": round(ahorros, 2),
            "inversiones_on": round(inversiones_on, 2),
            "inversiones_off": round(inversiones_off, 2),


            "activos_no_liquidos": round(activos_no_liquidos, 2),
            "propiedades_on": round(propiedades_on, 2),
            "propiedades_off": round(propiedades_off, 2),
            "otros" : round(otras_propiedades_valor, 2),
            "participaciones": round(participaciones, 2),

            "pensiones": round(pensiones, 2),


            "ingresos_futuros": round(ingreso_futuros, 2),
            "sueldo_titular": round(to_float(patrimonio.get("sueldo_titular")), 2),
            "utilidades_bonos": round(to_float(patrimonio.get("utilidades_bonos")), 2),
            "ingresos_conyuge": round(ingresos_conyuge, 2),

            "ingresos_adicionales": round(ingresos_adicionales, 2),

            #gastos

            "deudas": round(deudas, 2),
            "gastos_basicos": round(gastos_basicos, 2),
            "gasto_seguro_vida": round(gasto_seguro_vida, 2),
            "gastos_estilo_vida": round(gastos_estilo_vida, 2),
            "gastos_viajes": round(gastos_viajes, 2),
            "gastos_educacion_hijos": round(gastos_educacion_hijos, 2),
            "gastos_extraordinarios": round(gastos_extraordinarios, 2),

        }

        
        #print("✅ Cálculos realizados:", respuesta)

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
