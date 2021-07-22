from operator import methodcaller
from flask import render_template, request

from app.solarbeam import bp
from .scripts import util_solarbeam, generacion, ahorros
from app import util

@bp.route('/solarbeam/app/', methods=['GET', 'POST'])
def solarbeam_app():
    util.get_conn_sb_tar()
    estados = util.get_json_s3('cfe-tarifas', 'estados_municipios.json')
    if request.method == 'POST':
        req_vals = request.form.to_dict()
        print(req_vals)
        lat, lon = float(req_vals['coordLat']), float(req_vals['coordLon'])
        consumo_df = util_solarbeam.get_consumo_df(req_vals)
        tot_kwh = consumo_df[['kwh-base', 'kwh-inter', 'kwh-punta']].sum().sum()
        a, cap = generacion.main(lat, lon, 2010, tot_kwh)
        df, df2, rinv, rinv_noinf, ahorro_key, ahorro_anual, nueva_fact = ahorros.main(
            a, consumo_df, cap, req_vals['estado'], req_vals['municipio'], req_vals['servicio'])



        # print(costos_actuales)
    return render_template('solarBeam/home.html', estados=estados)