
def get_costos_actuales_anuales(req_dict):
    costos_actuales = []
    for bim, costo in req_dict.items():
        if bim.startswith('bim'):
            costos_actuales.append(float(costo[0]))
    return costos_actuales