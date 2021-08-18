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


# GESTOR
@bp.route('/gestor/mis_ofertas/')
@login_required_roles(['gestor', 'admin'])
def gestor_ofertas():
    
    return render_template('solarBeam/gestor/gestor_ofertas.html', len=len)


@bp.route('/gestor/mis_ofertas/<id_oferta>/predim_confirmacion', methods=['GET', 'POST'])
@login_required_roles(['gestor', 'admin'])
def gestor_oferta_info(id_oferta):
    oferta = OfertaLicitacion.query.get(id_oferta)
    if oferta:
        if not oferta.gestor == current_user.user_rol:
            abort(401)

    if request.method == 'POST':
        req_vals = request.form.to_dict()
        if req_vals['confirm'] == 'True':
            oferta.pre_dimensionamiento.status_gestor = True
            if oferta.pre_dimensionamiento.status_comprador:
                util_solarbeam.confirm_predim_ofer(oferta)
            db.session.commit()
        
        return redirect(url_for('solarbeam.gestor_ofertas'))

    return render_template('solarBeam/gestor/gestor_oferta_info.html', oferta=oferta)


@bp.route('/gestor/mis_ofertas/<id_oferta>/dim_confirmacion', methods=['GET', 'POST'])
@login_required_roles(['gestor', 'admin'])
def gestor_oferta_dim_conf(id_oferta):
    oferta = util_solarbeam.is_offer_from_gestor(id_oferta)
    if not oferta:
        return redirect(url_for('solarbeam.gestor_ofertas'))

    if request.method == 'POST':
        req_vals = request.form.to_dict()
        print(req_vals)
        
        main_error = render_template('solarBeam/gestor/gestor_oferta_dim.html', oferta=oferta, s3_error=True)
        cap_kwp = req_vals.get('capKwp')
        cap_kw = req_vals.get('capKw')

        if cap_kwp and cap_kw:
            oferta.kwp = cap_kwp
            oferta.kw = cap_kw
            if 'projEje' in request.files:
                file_object = request.files['projEje']
                file_key = f"archivos/oferta/{oferta.id}/ProyectoEjecutivo.pdf"
                error = util.upload_file_to_s3(file_object, file_key)
            
                if error:
                    return main_error
                oferta.dimensionamiento.proyecto_ejecutivo_key = file_key
            else:
                return main_error
            
            db.session.commit()

            return redirect(url_for('solarbeam.gestor_ofertas'))
            
    return render_template('solarBeam/gestor/gestor_oferta_dim.html', oferta=oferta)

# COMPRADOR
@bp.route('/comprador/registro_oferta_compra/', methods=['GET', 'POST'])
@login_required_roles(['comprador', 'admin'])
def registro_oferta_compra():
    if request.method == 'POST':
        req_vals = request.form.to_dict()
        print(req_vals)

        if not util_solarbeam.is_cp_valid(req_vals['cp']):
            req_vals.pop('csrf_token')
            req_vals['error'] = 'cp'
            return render_template('solarBeam/reg_oferta_compra.html', req_vals=req_vals, errorCP=True)
        else:
            cp = CodigoPostal.query.filter_by(codigo_postal = req_vals['cp']).first()

        oferta_aceptada = True
        if req_vals['tipoOferta'] == 'ofertaInd':
            nueva_licitacion =  LicitacionPrivada(comprador_id=current_user.user_rol.id, agrupada=False)
        elif req_vals['tipoOferta'] == 'ofertaNuevaLicPriv':
            nueva_licitacion = LicitacionPrivada(comprador_id=current_user.user_rol.id, agrupada=True)
        elif req_vals['tipoOferta'] == 'ofertaLicPub':
            nueva_licitacion = Licitacion.query.filter_by(agrupada=True, activa=True).first()
            if not nueva_licitacion:
                nueva_licitacion = LicitacionPublica(agrupada=True, activa=True)
                db.session.add(nueva_licitacion)
                db.session.flush()
        elif req_vals['tipoOferta'] == 'ofertaUnirLicPriv': 
            codigo_licit = req_vals.get('codigoLicit')
            nueva_licitacion = LicitacionPrivada.query.filter_by(agrupada=True, activa=True, codigo=codigo_licit).first()
            oferta_aceptada = None
            if not nueva_licitacion:
                req_vals.pop('csrf_token')
                req_vals['error'] = 'codigoLicit'
                return render_template('solarBeam/reg_oferta_compra.html', req_vals=req_vals, errorCodeLicit=True)
            elif nueva_licitacion.is_dimen_ofertas_complete():
                req_vals.pop('csrf_token')
                req_vals['error'] = 'codigoLicit'
                return render_template('solarBeam/reg_oferta_compra.html', req_vals=req_vals, errorCodeLicit=True, errorLicitDimen=True)
            
        if req_vals['tipoOferta'] in ['ofertaInd', 'ofertaNuevaLicPriv']:
            db.session.add(nueva_licitacion)
            db.session.flush()

        if req_vals['gestorOpc'] == 'sinGestor':
            gestor_id = util_solarbeam.get_random_gestor_id(cp.municipio)
        elif req_vals['gestorOpc'] == 'conGestor':
            gestor_id = util_solarbeam.get_gestor_id_with_code(req_vals['codigoGestor'])

            if not gestor_id:
                req_vals.pop('csrf_token')
                req_vals['error'] = 'codigoGestor'
                return render_template('solarBeam/reg_oferta_compra.html', req_vals=req_vals, errorCodeGestor=True)

        nueva_ofer_lic = OfertaLicitacion(
            licitacion_id=nueva_licitacion.id, comprador_id=current_user.user_rol.id, gestor_id=gestor_id,
            max_kw=req_vals['capMax'], min_wp=req_vals['capMin'], precio_max=req_vals['preMax'],
            nombre=req_vals['proyectoNombre'], direccion=req_vals['calle'], colonia=req_vals['colonia'],
            cp_id=cp.id, latitud=req_vals['coordLat'], longitud=req_vals['coordLon'], aceptada=oferta_aceptada,
        )
        
        db.session.add(nueva_ofer_lic)
        db.session.flush()

        util_solarbeam.populate_state_tbls(nueva_ofer_lic.id)
        db.session.commit()

        return redirect(url_for('solarbeam.comprador_ofertas'))

    return render_template('solarBeam/reg_oferta_compra.html')

@bp.route('/comprador/mis_ofertas/', methods=['GET', 'POST'])
@login_required_roles(['comprador', 'admin'])
def comprador_ofertas():
    if request.method == 'POST':
        req_vals = request.form.to_dict()
        print(req_vals)
        if req_vals['tipo'] == 'eliminar':
            oferta = util_solarbeam.is_offer_from_comprador(req_vals['idOferta'])
            if oferta:
                if oferta.status < 2:
                    db.session.delete(oferta)
                    db.session.commit()
                # return redirect(url_for('solarbeam.comprador_ofertas'))
        elif req_vals['tipo'] == 'updateGestorCode':
            oferta = OfertaLicitacion.query.get(req_vals['oferta'])
            if req_vals['gestorOpc'] == 'sinGestor':
                gestor_id = util_solarbeam.get_random_gestor_id(oferta.cp.municipio)

                if not gestor_id:
                    return render_template('solarBeam/comprador/comprador_ofertas.html', errorNoGestor=True, len=len)

            elif req_vals['gestorOpc'] == 'conGestor':
                gestor_id = util_solarbeam.get_gestor_id_with_code(req_vals['codigoGestor'])

                if not gestor_id:
                    return render_template('solarBeam/comprador/comprador_ofertas.html', errorInvGestor=True, len=len)
            
            if oferta.comprador == current_user.user_rol:
                if not oferta.gestor_id:
                    oferta.gestor_id = gestor_id
                    db.session.commit()
    
    return render_template('solarBeam/comprador/comprador_ofertas.html', len=len)

@bp.route('/comprador/mis_licitaciones/')
@login_required_roles(['comprador', 'admin'])
def comprador_lictaciones():

    return render_template('solarbeam/comprador/comprador_licitaciones.html', enumerate=enumerate)

@bp.route('/comprador/mis_licitaciones/<id_licit>', methods=['GET', 'POST'])
@login_required_roles(['comprador', 'admin'])
def comprador_ofertas_pendientes_por_licitacion(id_licit):
    licitacion = util_solarbeam.is_licit_from_comprador(id_licit)
    if not licitacion:
        return redirect(url_for('solarbeam.comprador_lictaciones'))

    if request.method == 'POST':
        req_vals = request.form.to_dict()
        req_vals = {key: value for key, value in req_vals.items() if key.startswith('oferta-')}

        for oferta_key, decision in req_vals.items():
            oferta_id = oferta_key.split('-')[-1]
            oferta = OfertaLicitacion.query.get(oferta_id)
            if util_solarbeam.is_licit_from_comprador(oferta.licitacion.id):
                bool_val = None
                if decision == 'aceptar':
                    bool_val = True
                elif decision == 'rechazar':
                    bool_val = False
                oferta.aceptada = bool_val
                db.session.commit()
        
        return redirect(url_for('solarbeam.comprador_lictaciones'))

    return render_template('solarbeam/comprador/comprador_ofertas_pendientes.html', licitacion=licitacion)

@bp.route('/comprador/mis_ofertas/<id_oferta>/predim_confirmacion', methods=['GET', 'POST'])
@login_required_roles(['comprador', 'admin'])
def comprador_oferta_info(id_oferta):
    oferta = OfertaLicitacion.query.get(id_oferta)
    if oferta:
        if not oferta.comprador == current_user.user_rol:
            abort(401)

    if request.method == 'POST':
        req_vals = request.form.to_dict()
        if req_vals['confirm'] == 'True':
            oferta.pre_dimensionamiento.status_comprador = True
            if oferta.pre_dimensionamiento.status_gestor:
                util_solarbeam.confirm_predim_ofer(oferta)
            db.session.commit()
        
        return redirect(url_for('solarbeam.comprador_ofertas'))

    return render_template('solarBeam/comprador/comprador_oferta_info.html', oferta=oferta)

@bp.route('/comprador/mis_ofertas/<id_oferta>/dim_confirmacion', methods=['GET', 'POST'])
@login_required_roles(['comprador', 'admin'])
def comprador_oferta_dim_conf(id_oferta):
    oferta = util_solarbeam.is_offer_from_comprador(id_oferta)
    if not oferta:
        return redirect(url_for('solarbeam.comprador_ofertas'))

    if request.method == 'POST':
        req_vals = request.form.to_dict()
        
        if req_vals.get('confirm') == 'yes':
            util_solarbeam.confirm_dim_ofer(oferta)

            return redirect(url_for('solarbeam.comprador_ofertas'))

    return render_template('solarBeam/comprador/comprador_oferta_dim.html', oferta=oferta)

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