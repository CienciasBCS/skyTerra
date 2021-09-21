from flask import render_template, request, redirect, url_for, abort
from flask_login import current_user

from app.decorators import login_required_roles
from app.models import OfertaLicitacion, CodigoPostal, LicitacionPrivada, Licitacion, LicitacionPublica
from app.solarbeam.scripts import util_solarbeam
from app import db
from . import bp

@bp.route('/registro_oferta_compra/', methods=['GET', 'POST'])
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

        return redirect(url_for('solarbeam_comprador.comprador_ofertas'))

    return render_template('solarBeam/reg_oferta_compra.html')

@bp.route('/mis_ofertas/', methods=['GET', 'POST'])
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

@bp.route('/mis_licitaciones/')
@login_required_roles(['comprador', 'admin'])
def comprador_lictaciones():

    return render_template('solarbeam/comprador/comprador_licitaciones.html', enumerate=enumerate)

@bp.route('/mis_licitaciones/<id_licit>', methods=['GET', 'POST'])
@login_required_roles(['comprador', 'admin'])
def comprador_ofertas_pendientes_por_licitacion(id_licit):
    licitacion = util_solarbeam.is_licit_from_comprador(id_licit)
    if not licitacion:
        return redirect(url_for('solarbeam_comprador.comprador_lictaciones'))

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
        
        return redirect(url_for('solarbeam_comprador.comprador_lictaciones'))

    return render_template('solarbeam/comprador/comprador_ofertas_pendientes.html', licitacion=licitacion)

@bp.route('/mis_ofertas/<id_oferta>/predim_confirmacion', methods=['GET', 'POST'])
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
        
        return redirect(url_for('solarbeam_comprador.comprador_ofertas'))

    return render_template('solarBeam/comprador/comprador_oferta_info.html', oferta=oferta)

@bp.route('/mis_ofertas/<id_oferta>/dim_confirmacion', methods=['GET', 'POST'])
@login_required_roles(['comprador', 'admin'])
def comprador_oferta_dim_conf(id_oferta):
    oferta = util_solarbeam.is_offer_from_comprador(id_oferta)
    if not oferta:
        return redirect(url_for('solarbeam_comprador.comprador_ofertas'))

    if request.method == 'POST':
        req_vals = request.form.to_dict()
        
        if req_vals.get('confirm') == 'yes':
            util_solarbeam.confirm_dim_ofer(oferta)

            return redirect(url_for('solarbeam_comprador.comprador_ofertas'))

    return render_template('solarBeam/comprador/comprador_oferta_dim.html', oferta=oferta)

@bp.route('/mis_ofertas/<id_oferta>/instalacion_confirmacion', methods=['GET', 'POST'])
@login_required_roles(['comprador', 'admin'])
def comprador_oferta_instalacion_conf(id_oferta):
    oferta = util_solarbeam.is_offer_from_comprador(id_oferta)
    if not oferta or oferta.status != 3:
        return redirect(url_for('solarbeam_comprador.comprador_ofertas'))

    if request.method == 'POST':
        req_vals = request.form.to_dict()
        print(req_vals)

        if req_vals.get('instalacion') == 'True':
            oferta.instalacion.confirmacion_comprador = True
            db.session.commit()

            util_solarbeam.confirm_inst_offer(oferta)

            return redirect(url_for('solarbeam_comprador.comprador_ofertas'))

    return render_template('solarBeam/comprador/comprador_oferta_inst.html', id_oferta=id_oferta, oferta=oferta)