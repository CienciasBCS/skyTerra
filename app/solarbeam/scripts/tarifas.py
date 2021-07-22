import json, datetime

from app import util

factor_carga = {
    'apbt': 0.50, 'apmt': 0.50, 'rabt': 0.5, 'ramt': 0.5, 'pdbt': 0.58, 
    'gdbt': 0.49, 'gdmth': 0.57, 'gdmto': 0.55, 'dist': 0.74, 'dit': 0.71
}

def get_days_of_month(mes):
    days = {
        1: 31, 2:28, 3:31, 4:30, 5:31, 6:30,
        7: 31, 8: 31, 9:30, 10:31, 11:30, 12:31
    }
    return days[mes]

def meses(mes):
    mes_dict = {
        1: 0, 2: 31, 3: 59, 4: 90, 5: 120, 6: 151,
        7: 181, 8: 212, 9: 243, 10: 273, 11: 304, 12: 334,
    }
    return mes_dict[mes]

def get_tar_info(estado, municipio, mes, tarifa, tipo):
    conn = util.get_conn_sb_tar()
    query = f"""
    SELECT mes, division, costos FROM {tarifa}
    WHERE mes = '{mes}' AND estado = '{estado}' AND municipio = '{municipio}'
    AND tipo = '{tipo}'
    """
    print(query)
    results = conn.execute(query).fetchall()
    conn.close()
    return {result[1]: json.loads(result[2]) for result in results}

def calc_tarifa_gdmth(fecha, estado, municipio, tipo, kwh_list, dem_list):
    mes = datetime.datetime.strptime(fecha, '%Y-%m-%d').month
    tar_info = get_tar_info(estado, municipio, fecha, 'gdmth', tipo)
    
    costos_variables = []
    for division, costos_info in tar_info.items():
        costo_fijo = float(costos_info['fijo'])
        costo_dist = float(costos_info['distribucion'])
        costo_cap = float(costos_info['capacidad'])
        
        costos_variables.append(kwh_list[0] * costos_info['base'])
        costos_variables.append(kwh_list[1] * costos_info['intermedia'])
        if len(kwh_list) > 2:
            costos_variables.append(kwh_list[2] * costos_info['punta'])

    costo_var_total = sum(costos_variables)
    number_of_days = get_days_of_month(mes)
    dem_calculada = (sum(kwh_list) / (24 * number_of_days * factor_carga['gdmth']))
    
    if len(dem_list) == 3:
        cargo_cap = min(dem_list[2], dem_calculada)
    else:
        cargo_cap = dem_calculada
    cargo_dist = min(max(dem_list), dem_calculada)
    costo_capdist_total = (cargo_cap *  costo_cap) + (cargo_dist * costo_dist)
    return costo_fijo + costo_capdist_total + costo_var_total