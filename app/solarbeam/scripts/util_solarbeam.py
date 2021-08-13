import datetime, random
from dateutil.relativedelta import relativedelta

from flask import abort
from flask_login import current_user
from app import db
from app.models import CodigoPostal, Gestor, User, OfertaLicitacion, Licitacion, \
                    PreDimensionamiento, Dimensionamiento, Adquisicion, Instalacion, PuestaEnMarcha
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
    return CodigoPostal.query.filter_by(codigo_postal = cp).first().id

def is_telCel_valid(cel):
    return not db.session.query(db.exists().where(User.telefono == cel)).scalar()

def populate_state_tbls(oferta_id):
    for tbl in [PreDimensionamiento, Dimensionamiento, Adquisicion, Instalacion, PuestaEnMarcha]:
        tbl_obj = tbl(id=oferta_id)
        db.session.add(tbl_obj)

def get_gestor_id_with_code(codigo):
    gestor = Gestor.query.filter_by(codigo=codigo).first()
    if gestor:
        return gestor.id
    return None

def get_random_gestor_id(municipio):
    gestores = Gestor.query.join(User, aliased=True).join(CodigoPostal).filter_by(municipio=municipio).all()
    if gestores:
        gestor = random.choice(gestores)
        return gestor.id
    return None

def is_licit_from_comprador(id_licit):
    licitacion = Licitacion.query.get(id_licit)
    if licitacion:
        if licitacion.creador != current_user.user_rol:
            abort(401)
        return licitacion
    return False

def is_offer_from_gestor(id_oferta):
    oferta = OfertaLicitacion.query.get(id_oferta)
    if oferta:
        if oferta.gestor != current_user.user_rol:
            abort(401)
        return oferta
    return False

def is_offer_from_comprador(id_oferta):
    oferta = OfertaLicitacion.query.get(id_oferta)
    if oferta:
        if not oferta.comprador == current_user.user_rol:
            abort(401)
        else:
            return oferta
    else:
        return False

def confirm_predim_ofer(oferta):
    if oferta.pre_dimensionamiento.is_complete:
        oferta.status = 1

    db.session.commit()

def confirm_dim_ofer(oferta):
    oferta.dimensionamiento.status_comprador = True
    if oferta.licitacion.is_dimen_ofertas_complete():
        for dim_oferta in oferta.licitacion.ofertas:
            if oferta.aceptada:
                dim_oferta.status = 2
    db.session.commit()