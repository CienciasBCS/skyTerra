from flask import render_template, request, redirect, url_for, abort
from flask_login import current_user

from app.decorators import login_required_roles
from app.models import OfertaLicitacion
from app.solarbeam.scripts import util_solarbeam
from app import db, util
from . import bp


@bp.route('/mis_ofertas/')
@login_required_roles(['gestor', 'admin'])
def gestor_ofertas():
    
    return render_template('solarBeam/gestor/gestor_ofertas.html', len=len)


@bp.route('/mis_ofertas/<id_oferta>/predim_confirmacion', methods=['GET', 'POST'])
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


@bp.route('/mis_ofertas/<id_oferta>/dim_confirmacion', methods=['GET', 'POST'])
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
