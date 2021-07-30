import datetime, random
from dateutil.relativedelta import relativedelta

from app import db
from app.models import CodigoPostal, Gestor, User

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

def is_cp_valid(cp):
    return db.session.query(db.exists().where(CodigoPostal.codigo_postal == cp)).scalar()

def get_cp_id(cp):
    return CodigoPostal.query.filter_by(codigo_postal = 23090).first().id

def get_gestor_id_with_code(codigo):
    gestor = Gestor.query.filter_by(codigo=codigo).first()
    if gestor:
        return gestor.id
    else:
        return None

def get_random_gestor_id(municipio):
    gestores = Gestor.query.join(Gestor.user_role, aliased=True).join\
                (User, aliased=True).join(CodigoPostal).filter_by(municipio=municipio).all()
    if gestores:
        gestor = random.choice(gestores)
        return gestor.id
    else:
        return None