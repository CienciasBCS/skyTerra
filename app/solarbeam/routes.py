import re
from flask import render_template, request
from flask.helpers import url_for
from flask_login import current_user
from werkzeug.utils import redirect

from app.solarbeam import bp
from app.decorators import login_required_no_rol, login_required_roles
from app.models import Comprador, Integrador, Gestor, Licitacion, OfertaLicitacion
from .scripts import util_solarbeam, generacion, ahorros
from app import util, db

@bp.route('/solarbeam/app/', methods=['GET', 'POST'])
def solarbeam_app():
    util.get_conn_sb_tar()
    estados = util.get_json_s3('tarifas-cfe', 'estados_municipios.json')
    if request.method == 'POST':
        req_vals = request.form.to_dict()
        print(req_vals)
        lat, lon = float(req_vals['coordLat']), float(req_vals['coordLon'])
        consumo_df = util_solarbeam.get_consumo_df(req_vals)
        tot_kwh = consumo_df[['kwh-base', 'kwh-inter', 'kwh-punta']].sum().sum()
        a, cap = generacion.main(lat, lon, 2010, tot_kwh)
        df, df2, rinv, rinv_noinf, ahorro_key, ahorro_anual, nueva_fact = ahorros.main(
            a, consumo_df, cap, req_vals['estado'], req_vals['municipio'], req_vals['servicio'])


    return render_template('solarBeam/home.html', estados=estados)

@bp.route('/solarbeam/app/confirmacion_usuario/', methods=['GET', 'POST'])
@login_required_no_rol()
def confirmar_usuario():
    if request.method == 'POST':
        req_vals = request.form.to_dict()
        print(req_vals)
        print(request.files)
        for file in request.files:
            file_object = request.files[file]
            file_key = f"archivos/{current_user.id}/{file}.pdf"

            error = util.upload_file_to_s3(file_object, file_key)

        if req_vals['rolUser'] == 'comprador':
            rol = Comprador(user_id=current_user.id)
        elif req_vals['rolUser'] == 'integrador':
            rol = Integrador(user_id=current_user.id)
        elif req_vals['rolUser'] == 'gestor':
            rol = Gestor(user_id=current_user.id)
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
        current_user.codigo_postal = req_vals['cp']
        current_user.acta_constitutiva_key = f"archivos/{current_user.id}/actaConstitutiva.pdf"
        current_user.doc_req1_key = f"archivos/{current_user.id}/docReq1.pdf"
        current_user.doc_req2_key = f"archivos/{current_user.id}/docReq2.pdf"
        current_user.doc_req3_key = f"archivos/{current_user.id}/docReq3.pdf"
        current_user.tiene_rol = True

        db.session.commit()

        return redirect(url_for('solarbeam.confirmar_usuario'))

    return render_template('solarBeam/confirm_user.html')


# COMPRADOR
@bp.route('/solarbeam/app/mis_ofertas/')
def comprador_ofertas():


    return render_template('solarBeam/comprador_ofertas.html', len=len)


@bp.route('/solarbeam/app/registro_oferta_compra/', methods=['GET', 'POST'])
@login_required_roles(['comprador', 'admin'])
def registro_oferta_compra():
    if request.method == 'POST':
        req_vals = request.form.to_dict()
        print(req_vals)
        if req_vals['tipoOferta'] == 'ofertaInd':
            nueva_licitacion = Licitacion(agrupada=False, activa=True)
            db.session.add(nueva_licitacion)
            db.session.flush()

            nueva_ofer_lic = OfertaLicitacion(
                licitacion_id=nueva_licitacion.id, comprador_id=current_user.user_rol.comprador.id,
                max_kw=req_vals['capMax'], min_wp=req_vals['capMin'], precio_max=req_vals['preMax'],
                nombre=req_vals['proyectoNombre'], direccion=req_vals['calle'], colonia=req_vals['colonia'],
                codigo_postal=req_vals['cp'], latitud=req_vals['coordLat'], longitud=req_vals['coordLon'],
                status=0
            )
            db.session.add(nueva_ofer_lic)
            db.session.commit()

            return redirect(url_for('solarbeam.comprador_ofertas'))

        if req_vals['coordLat'] and req_vals['coordLon']:
            return render_template('solarBeam/reg_oferta_compra.html', success=True)
        else:
            return render_template('solarBeam/reg_oferta_compra.html', errorCoords=True)

    return render_template('solarBeam/reg_oferta_compra.html')




# INTEGRADOR
@bp.route('/solarbeam/app/proyectos_disponibles/')
def proyectos_disponibles():


    return render_template('solarBeam/integrador_oferta_compra.html')


@bp.route('/solarbeam/app/proyectos_disponibles/agregar_oferta')
def agregar_oferta():


    return render_template('solarBeam/integrador_agregar_oferta.html')


@bp.route('/solarbeam/app/proyectos_disponibles/instalacion')
def instalacion():


    return render_template('solarBeam/instalacion.html')


@bp.route('/solarbeam/app/proyectos_disponibles/marcha')
def marrcha():


    return render_template('solarBeam/marcha.html')    