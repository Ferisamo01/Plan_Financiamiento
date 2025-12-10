from datetime import datetime
def tasas(perfil):

    mapeo_tasas = {
        "Conservador": 0.04,
        "Moderado": 0.045,
        "Dinámico": 0.06,
        "400": 0.085,
        "500": 0.07,
        "100": 0.04,
        "200": 0.045,
        "300": 0.06,
        "100 SA": 0.04,
        "200 SA": 0.045,
        "300 SA": 0.05,
        "400 SA": 0.055,
        "500 SA": 0.06
    }

    return mapeo_tasas.get(perfil, 0.05)

def edad(fecha_nacimiento):
    print("Fecha de nacimiento recibida:", fecha_nacimiento, type(fecha_nacimiento))

    if not fecha_nacimiento:
        return 0

    try:
        fecha_nac = datetime.strptime(fecha_nacimiento, "%Y-%m-%d")
        hoy = datetime.today()
        edad_calculada = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
        return edad_calculada
    except ValueError:
        return 0