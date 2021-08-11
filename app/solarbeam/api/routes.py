import pprint
from decimal import Decimal

from flask import jsonify, request

from app.decorators import login_required_roles
from app.models import Licitacion, LicitacionSchema, OfertaLicitacion, OfertaLicitacionSchema
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