import datetime
from dateutil.relativedelta import relativedelta

import pandas as pd

def get_costos_actuales_anuales(req_dict):
    costos_actuales = []
    for bim, costo in req_dict.items():
        if bim.startswith('bim'):
            costos_actuales.append(float(costo[0]))
    return costos_actuales

def get_consumo_df(req_dict):
    fecha_inicio_str = '-'.join(req_dict['fecha'].split('-')[:-1])
    fecha_inicio = datetime.datetime.strptime(fecha_inicio_str, '%Y-%m')
    df_data = {}
    for carac, value in req_dict.items():
        if carac.startswith(('dem', 'kwh')):
            incremento_mes = int(carac.split('-')[-1])
            fecha = fecha_inicio + relativedelta(months=incremento_mes)
            mes = fecha.month
            nombre_carac = '-'.join(carac.split('-')[:-1])
            if nombre_carac not in df_data:
                df_data[nombre_carac] = {}
                df_data['fecha'] = {}
            
            df_data[nombre_carac][mes] =  int(value)
            df_data['fecha'][mes] = fecha.strftime('%Y-%m-%d')
    consumo = pd.DataFrame(df_data).reset_index()   
    consumo.rename(columns={'index': 'mes'}, inplace=True)

    return consumo