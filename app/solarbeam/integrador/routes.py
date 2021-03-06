from flask import render_template, request, redirect, url_for
from flask_login import current_user


from app.decorators import login_required_roles
from app.models import OfertaLicitacion, Adquisicion, OfertaProveedor
from app.solarbeam.scripts import util_solarbeam
from app import db
from . import bp

@bp.route('/proyectos_disponibles')
@login_required_roles(['integrador', 'admin'])
def integrador_proyectos_disponibles():
    # ofertas_disponibles = OfertaLicitacion.query.join(Adquisicion).filter(OfertaLicitacion.status == 2, Adquisicion.oferta_prov_id==None).all()

    return render_template('solarBeam/integrador/integrador_proyectos.html', len=len)

@bp.route('/proyectos_disponibles/<id_oferta>', methods=['GET', 'POST'])
@login_required_roles(['integrador', 'admin'])
def integrador_oferta_info(id_oferta):
    oferta = OfertaLicitacion.query.get(id_oferta)
    if oferta:
        if not ( oferta.status == 2 and oferta.adquisicion.integrador_id == None  ):
            return redirect(url_for('solarbeam_integrador.integrador_proyectos_disponibles'))
    else:
        return redirect(url_for('solarbeam_integrador.integrador_proyectos_disponibles'))

    if request.method == 'POST':
        req_vals = request.form.to_dict()
        oferta_prov = OfertaProveedor(oferta_id=oferta.id, integrador_id=current_user.user_rol.id, precio=req_vals['precioOferta'])
        db.session.add(oferta_prov)
        db.session.commit()
        return redirect(url_for('solarbeam_integrador.integrador_proyectos_disponibles'))

    return render_template('solarBeam/integrador/integrador_proyecto_info.html', oferta=oferta)

@bp.route('/mis_ofertas/', methods=['GET', 'POST'])
@login_required_roles(['integrador', 'admin'])
def integrador_ofertas():
    licitaciones = current_user.user_rol.get_licitaciones_con_ofertas()

    if request.method == 'POST':
        req_vals = request.form.to_dict()
        if req_vals['tipo'] == 'eliminar':
            oferta = util_solarbeam.is_offer_prov_from_proveedor(req_vals['idOferta'])
            if oferta and not oferta.asignada:
                db.session.delete(oferta)
                db.session.commit()

    return render_template('solarBeam/integrador/integrador_ofertas.html', licitaciones=licitaciones)

@bp.route('/proyecto/<id_oferta>/instalacion_confirmacion', methods=['GET', 'POST'])
@login_required_roles(['integrador', 'admin'])
def integrador_oferta_instalacion_conf(id_oferta):
    oferta = util_solarbeam.is_offer_asignada_a_integrador(id_oferta)
    if not oferta or oferta.status != 3:
        return redirect(url_for('solarbeam_integrador.integrador_proyectos_disponibles'))

    if request.method == 'POST':
        req_vals = request.form.to_dict()
        print(req_vals)

        if req_vals.get('instalacion') == 'True':
            oferta.instalacion.confirmacion_integrador = True
            db.session.commit()

            util_solarbeam.confirm_inst_offer(oferta)

            return redirect(url_for('solarbeam_integrador.integrador_proyectos_disponibles'))

    return render_template('solarbeam/integrador/integrador_oferta_inst.html', oferta=oferta)