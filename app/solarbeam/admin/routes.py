from flask import render_template, request, url_for
from sqlalchemy import or_
from werkzeug.utils import redirect

from app.decorators import login_required_roles
from app.models import UserPending, Gestor, Integrador
from app import db
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