import pprint

from flask import render_template, request, url_for, redirect
from sqlalchemy import or_

from app.decorators import login_required_roles
from app.models import Licitacion, OfertaLicitacion, OfertaProveedor, UserPending, Gestor, Integrador
from app import db
from . import modelo
from . import bp

@bp.route('/usuarios_por_confirmar/')
@login_required_roles(['admin'])
def pending_users():
    pending_users = UserPending.query.filter(
        or_(UserPending.aceptado == False, UserPending.aceptado == None)
        ).all() 
    return  render_template('solarbeam/admin/usuarios_por_confirmar.html', pending_users=pending_users)


@bp.route('/usuarios_por_confirmar/<id_user>', methods=['GET', 'POST'])
@login_required_roles(['admin'])
def confirm_user(id_user):
    pending_user = UserPending.query.get(id_user)

    if request.method == 'POST':
        req_vals = request.form.to_dict()
        if req_vals['tipo_rol'] == 'gestor':
            rol = Gestor(user_id=pending_user.user.id)
        elif req_vals['tipo_rol'] == 'integrador':
            rol = Integrador(user_id=pending_user.user.id)
        pending_user.aceptado = True
        pending_user.user.tiene_rol = True

        db.session.add(rol)
        db.session.commit()

        return redirect(url_for('solarbeam_admin.pending_users'))

    return render_template('solarbeam/admin/confirmar_rol_usuario.html', pending_user=pending_user)

@bp.route('/licitaciones/', methods=['GET', 'POST'])
@login_required_roles(['admin'])
def licitaciones():
    licitaciones = Licitacion.query.filter_by(activa=True, oferta_venta_asignada=False).all()
    return render_template('solarbeam/admin/licitaciones.html', licitaciones=licitaciones)


@bp.route('/licitaciones/<id_licit>', methods=['GET', 'POST'])
@login_required_roles(['admin'])
def asignacion_ofertas(id_licit):
    licitacion = Licitacion.query.get(id_licit)
    if licitacion.oferta_venta_asignada:
        return redirect(url_for('solarbeam_admin.licitaciones'))

    if request.method == 'POST':
        req_vals = request.form.to_dict()
        if req_vals.get('confirm') == 'true':
            input_modelo = {}
            for oferta_compra in licitacion.ofertas:
                input_modelo[oferta_compra.id] = {}
                for oferta_prov in oferta_compra.ofertas_proveedores:
                    input_modelo[oferta_compra.id][oferta_prov.id] = float(oferta_prov.precio)
            
            print(input_modelo)
            output = modelo.main(input_modelo)
            for decision in output:
                oferta_comp = OfertaLicitacion.query.get(decision['oferta_compra'])
                oferta_vta = OfertaProveedor.query.get(decision['oferta_venta'])
                oferta_comp.status = 3
                oferta_vta.asignada = decision['variable']
            licitacion.oferta_venta_asignada = True
            db.session.commit()
        return redirect(url_for('solarbeam_admin.licitaciones'))
    return render_template('solarbeam/admin/licitacion_modelo.html', licitacion=licitacion)