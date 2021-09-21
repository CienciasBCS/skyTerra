from datetime import datetime
import json, time

from flask import render_template, request, abort, url_for, session
from flask_login import current_user
from werkzeug.utils import redirect

from app.solarbeam import bp
from app.decorators import login_required_no_rol, login_required_roles
from app.models import Comprador, Licitacion, OfertaLicitacion,\
                        UserPending, ConsumoInfo, CodigoPostal, LicitacionPublica, LicitacionPrivada
from .scripts import util_solarbeam, generacion, ahorros
from . import solarbeam_graphs
from app import util, db

@bp.route('/', methods=['GET', 'POST'])
def solarbeam_app():
    estados = util.get_json_s3('tarifas-cfe', 'estados_municipios.json')
    if request.method == 'POST':
        # resp = make_response(redirect(url_for('solarbeam.consumption_dashboard')))

        req_vals = request.form.to_dict()
        lat, lon = float(req_vals['coordLat']), float(req_vals['coordLon'])
        consumo_df = util_solarbeam.get_consumo_df(req_vals)
        tot_kwh = consumo_df[['kwh-base', 'kwh-inter', 'kwh-punta']].sum().sum()
        start = time.time()
        a, cap = generacion.main(lat, lon, 2010, tot_kwh)
        end = time.time()
        print(f"TIEMPO PARA GENERACION: {end - start}")
        start = time.time()
        df, df2, rinv_inf, rinv_noinf = ahorros.main(
            a, consumo_df, cap, req_vals['estado'], req_vals['municipio'], req_vals['servicio'])
        end = time.time()
        print(f"TIEMPO PARA AHORROS: {end-start}")

        if 'consumo_id' in session:
            consumo_info = ConsumoInfo.query.get(session['consumo_id'])
            consumo_info.consumo_json = json.loads(df.to_json())
            consumo_info.ahorro_json = json.loads(df2.to_json())
            consumo_info.info_solar_json = json.loads(a[['ind', 'generacion_graph']].to_json())
            consumo_info.rinv_inf_json = rinv_inf
            consumo_info.rinv_noinf_json = rinv_noinf
            consumo_info.created_at = datetime.utcnow()
            db.session.commit()
        else:
            consumo_info = ConsumoInfo(
                consumo_json = json.loads(df.to_json()), 
                ahorro_json = json.loads(df2.to_json()),
                info_solar_json=json.loads(a[['ind', 'generacion_graph']].to_json()),
                rinv_inf_json = rinv_inf, rinv_noinf_json=rinv_noinf
            )

            db.session.add(consumo_info)
            db.session.commit()
            session['consumo_id'] = consumo_info.id

        return redirect(url_for('solarbeam.consumption_dashboard'))

    return render_template('solarBeam/home.html', estados=estados)

@bp.route('/set_session/<consumo_id>')
def set_session(consumo_id):
    session['consumo_id'] = int(consumo_id)
    return 'yep'

@bp.route('/consumo_personal')
def consumption_dashboard():
    consumo_id = session['consumo_id']
    consumo_info = ConsumoInfo.query.get(consumo_id)

    graphs, capacidad, costos = solarbeam_graphs.get_consumo_graphs(
        consumo_info.consumo_json, consumo_info.ahorro_json, consumo_info.info_solar_json, 
        consumo_info.rinv_inf_json, consumo_info.rinv_noinf_json
    )
    return render_template('solarbeam/consumo_personal.html', graphs=graphs, capacidad=capacidad, costos=costos)

@bp.route('/confirmacion_usuario/', methods=['GET', 'POST'])
@login_required_no_rol()
def confirmar_usuario():
    if current_user.user_pending:
        abort(401)

    if request.method == 'POST':
        req_vals = request.form.to_dict()
        
        if not util_solarbeam.is_cp_valid(req_vals['cp']): # Unica validación en el servidor!!
            req_vals.pop('csrf_token')
            req_vals['error'] = 'cp'
            return render_template('solarBeam/confirm_user.html', cp_error=True, req_vals=req_vals)

        for file in request.files:
            file_object = request.files[file]
            file_key = f"archivos/usuario/{current_user.id}/{file}.pdf"

            error = util.upload_file_to_s3(file_object, file_key)

        if req_vals['rolUser'] == 'comprador':
            rol = Comprador(user_id=current_user.id)
            has_rol = True
            flask_url = 'solarbeam.comprador_ofertas'
        else: # gestor e integrador
            rol = UserPending(id=current_user.id, rol_solicitado=req_vals['rolUser'])
            has_rol = False
            flask_url = 'solarbeam.solarbeam_app'
        db.session.add(rol)


        current_user.nombre = req_vals['nombreUser']
        current_user.apellidos = req_vals['apellUser']
        current_user.telefono = req_vals['telUser']
        current_user.nombre_comercial = req_vals['nombreCom']
        current_user.razon_social = req_vals['razSoc']
        current_user.rfc = req_vals['rfc']
        current_user.nombre_rep_legal = req_vals['nomLegal']
        current_user.ape_paterno_rep_legal = req_vals['apePatLegal']
        current_user.ape_materno_rep_legal = req_vals['apeMatLegal']
        current_user.calle = req_vals['calle']
        current_user.colonia = req_vals['colonia']
        current_user.cp_id = util_solarbeam.get_cp_id(req_vals['cp'])  
        current_user.acta_constitutiva_key = f"archivos/usuario/{current_user.id}/actaConstitutiva.pdf"
        current_user.doc_req1_key = f"archivos/usuario/{current_user.id}/docReq1.pdf"
        current_user.doc_req2_key = f"archivos/usuario/{current_user.id}/docReq2.pdf"
        current_user.doc_req3_key = f"archivos/usuario/{current_user.id}/docReq3.pdf"
        current_user.tiene_rol = has_rol

        db.session.commit()

        return redirect(url_for(flask_url))

    return render_template('solarBeam/confirm_user.html')

# INTEGRADOR

@bp.route('/proyectos_disponibles/agregar_oferta')
def agregar_oferta():


    return render_template('solarBeam/integrador_agregar_oferta.html')


@bp.route('/proyectos_disponibles/instalacion')
def instalacion():


    return render_template('solarBeam/instalacion.html')


@bp.route('/proyectos_disponibles/marcha')
def marrcha():


    return render_template('solarBeam/marcha.html')    