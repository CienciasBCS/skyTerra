from operator import methodcaller
from flask import render_template, request

from app.solarbeam import bp
from .scripts import util_solarbeam, generacion, ahorros
from app import util

@bp.route('/solarbeam/app/', methods=['GET', 'POST'])
def solarbeam_app():
    estados = util.get_json_s3('cfe-tarifas', 'estados_municipios.json')
    if request.method == 'POST':
        req_vals = request.form.to_dict(flat=False)
        print(req_vals)
        # lat, lon = float(req_vals['coordLat'][0]), float(req_vals['coordLon'][0])
        costos_actuales = util_solarbeam.get_costos_actuales_anuales(req_vals)
        # tot_kwh = sum(costos_actuales)
        # a, cap = generacion.main(lat, lon, 2010, tot_kwh)
        # print(a['Month'])
        # df, df2, rinv, rinv_noinf, ahorro_key, ahorro_anual, nueva_fact = ahorros.main(
        #     a, df, cap, request.form['tarifa_dropdown'])



        print(costos_actuales)
    return render_template('solarBeam/home.html', estados=estados)