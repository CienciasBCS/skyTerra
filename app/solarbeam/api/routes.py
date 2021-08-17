import pprint

from flask import json, jsonify, request
from flask_login import current_user

from app.decorators import login_required_roles
from app.models import Licitacion, LicitacionSchema, OfertaLicitacion, OfertaLicitacionSchema, OfertaProveedor, OfertaProveedorSchema
from . import bp

@bp.route('/licitacion_info')
@login_required_roles(['gestor', 'comprador', 'admin'])    
def api_test():
    id_lic = request.args.get('licitacionId')
    licitacion = Licitacion.query.get(id_lic)
    licitacion_info = LicitacionSchema().dump(licitacion)
    # output = licitacion_schema.dump(oferta.licitacion)
    # for key, value in output.items():

    pprint.pprint(licitacion_info)
    return jsonify(licitacion_info)

@bp.route('/oferta_info')
@login_required_roles(['gestor', 'comprador', 'admin'])    
def oferta_info():
    id_ofe = request.args.get('ofertaId')
    oferta = OfertaLicitacion.query.get(id_ofe)
    oferta_info = OfertaLicitacionSchema().dump(oferta)
    # output = licitacion_schema.dump(oferta.licitacion)
    # for key, value in output.items():

    pprint.pprint(oferta_info)
    return jsonify(oferta_info)

@bp.route('/integrador/ofertas_prov')
@login_required_roles(['integrador', 'admin'])
def ofertas_info_por_licit():
    id_licit = request.args.get('licitId')
    ofertas = OfertaProveedor.query.join(OfertaLicitacion).join(Licitacion)\
        .filter(OfertaProveedor.integrador_id==current_user.user_rol.id, Licitacion.id==id_licit).all()
        # OfertaProveedor.query.join(OfertaLicitacion).join(Licitacion).filter(OfertaProveedor.integrador_id==11, Licitacion.id==35).all()
    print(ofertas)
    oferta_output = OfertaProveedorSchema(many=True).dump(ofertas)
    
    pprint.pprint(oferta_output)
    return jsonify(oferta_output)