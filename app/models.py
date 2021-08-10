from datetime import datetime

import boto3
from sqlalchemy.ext.hybrid import hybrid_property
from flask_login import UserMixin
from flask import current_app

from app import db, login, util


class ConsumoInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    consumo_json = db.Column(db.JSON, nullable=False)
    ahorro_json = db.Column(db.JSON, nullable=False)
    info_solar_json = db.Column(db.JSON, nullable=False)
    rinv_inf_json = db.Column(db.JSON, nullable=False)
    rinv_noinf_json = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)

class CodigoPostal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo_postal = db.Column(db.Integer, unique=True, nullable=False)
    estado = db.Column(db.String(100), nullable=False)
    municipio = db.Column(db.String(100), nullable=False)
    ciudad = db.Column(db.String(100))
    usuarios = db.relationship('User', backref='cp')
    ofertas = db.relationship('OfertaLicitacion', backref='cp')

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cog_user_id = db.Column(db.String(50), unique=True)
    nombre = db.Column(db.String(100))
    apellidos = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    telefono = db.Column(db.String(10))
    nombre_comercial = db.Column(db.String(100), nullable=False)
    razon_social = db.Column(db.String(100), nullable=False)
    rfc = db.Column(db.String(13), nullable=False)
    nombre_rep_legal = db.Column(db.String(100), nullable=False)
    ape_paterno_rep_legal = db.Column(db.String(100), nullable=False)
    ape_materno_rep_legal = db.Column(db.String(100), nullable=False)
    calle = db.Column(db.String(100), nullable=False)
    colonia = db.Column(db.String(100), nullable=False)
    cp_id = db.Column(db.Integer, db.ForeignKey('codigo_postal.id', ondelete="CASCADE"))
    acta_constitutiva_key = db.Column(db.String(100), nullable=False)
    doc_req1_key = db.Column(db.String(100), nullable=False)
    doc_req2_key = db.Column(db.String(100), nullable=False)
    doc_req3_key = db.Column(db.String(100), nullable=False)
    tiene_rol = db.Column(db.Boolean, nullable=False, default=False)
    user_rol = db.relationship('UserRole', backref='user', uselist=False, cascade="all,delete")
    # rol_id = db.Column(db.Integer, db.ForeignKey('rol.id'))


    def __repr__(self):
        return f'<User {self.cog_user_id}>'  

class UserRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), unique=True)
    tipo = db.Column(db.String(25))
    comprador = db.relationship('Comprador', backref='user_role', uselist=False, cascade="all,delete")
    gestor = db.relationship('Gestor', backref='user_role', uselist=False, cascade="all,delete")
    integrador = db.relationship('Integrador', backref='user_role', uselist=False, cascade="all,delete")

    __mapper_args__ = {
        'polymorphic_identity':'user_role',
        'polymorphic_on': tipo
    }

class Comprador(UserRole):
    id = db.Column(db.Integer, db.ForeignKey('user_role.id', ondelete="CASCADE"), primary_key=True)
    atr = db.Column(db.String(10))
    ofertas = db.relationship('OfertaLicitacion', backref='comprador')


    __mapper_args__ = {
        'polymorphic_identity':'comprador',
    }

class Gestor(UserRole):
    id = db.Column(db.Integer, db.ForeignKey('user_role.id', ondelete="CASCADE"), primary_key=True)
    ofertas = db.relationship('OfertaLicitacion', backref='gestor')
    codigo = db.Column(db.String(6), index=True, default=util.get_random_code, unique=True)

    __mapper_args__ = {
        'polymorphic_identity':'gestor',
    }    

class Integrador(UserRole):
    id = db.Column(db.Integer, db.ForeignKey('user_role.id', ondelete="CASCADE"), primary_key=True)
    ofertas = db.relationship('OfertaProveedor', backref='integrador')
    ofertas_grupo = db.relationship('OfertaGrupo', backref='integrador')

    __mapper_args__ = {
        'polymorphic_identity':'integrador',
    }    

class Marca(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(75), nullable=False)
    productos = db.relationship('Producto', backref='marca')

    def __repr__(self):
        return f'<Marca: {self.nombre}>'    

class Producto(db.Model):
    __tablename__ = 'producto'
    id = db.Column(db.Integer, primary_key=True)
    marca_id = db.Column(db.Integer, db.ForeignKey('marca.id'))
    type = db.Column(db.String(50))
    paneles = db.relationship('Panel', backref='producto')
    inversores = db.relationship('Inversor', backref='producto')

    __mapper_args__ = {
        'polymorphic_identity':'producto',
        'polymorphic_on': type
    }

class Panel(Producto):
    __tablename__ = 'panel'
    id = db.Column(db.Integer, db.ForeignKey('producto.id'), primary_key=True)
    modelo = db.Column(db.String(100),  nullable=False)
    ficha_tecnica_key = db.Column(db.String(50), nullable=False)
    wp = db.Column(db.Integer, nullable=False)
    vmp = db.Column(db.Numeric(4, 2), nullable=False)
    imp = db.Column(db.Numeric(4, 2), nullable=False)
    efc = db.Column(db.Numeric(4, 2), nullable=False)

    def __repr__(self):
        return f'<Panel: {self.marca.nombre} - wp: {self.wp}>'  

    __mapper_args__ = {
        'polymorphic_identity':'panel',
    }

class Inversor(Producto):
    id = db.Column(db.Integer, db.ForeignKey('producto.id'), primary_key=True)
    modelo = db.Column(db.String(100),  nullable=False)
    ficha_tecnica_key = db.Column(db.String(50), nullable=False)
    min_wp = db.Column(db.Integer, nullable=False)
    max_wp = db.Column(db.Integer, nullable=False)
    kw_ac = db.Column(db.Integer, nullable=False)
    max_vdc = db.Column(db.Numeric(4, 2), nullable=False)
    max_isc = db.Column(db.Numeric(4, 2), nullable=False)
    max_imc = db.Column(db.Numeric(4, 2), nullable=False)
    min_mppt = db.Column(db.Numeric(4, 2), nullable=False)
    max_mppt = db.Column(db.Numeric(4, 2), nullable=False)
    num_mppt = db.Column(db.Integer, nullable=False)
    strings = db.Column(db.Integer, nullable=False)
    efc = db.Column(db.Numeric(4, 2), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity':'inversor',
    }

class Licitacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agrupada = db.Column(db.Boolean, nullable=False, default=False)
    kwp_inst = db.Column(db.Numeric(4, 2))
    kw = db.Column(db.Numeric(4, 2))
    cant = db.Column(db.Numeric(4, 2))
    activa = db.Column(db.Boolean, nullable=False, default=True)
    ofertas = db.relationship('OfertaLicitacion', backref='licitacion', cascade="all,delete")

    def __repr__(self):
        return f'<Licitación: {self.nombre} - kwh: {self.kw}>'  

class OfertaLicitacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    licitacion_id = db.Column(db.Integer, db.ForeignKey('licitacion.id', ondelete="CASCADE"), nullable=False)
    comprador_id = db.Column(db.Integer, db.ForeignKey('comprador.id', ondelete="CASCADE" ), nullable=False)
    gestor_id = db.Column(db.Integer, db.ForeignKey('gestor.id'))
    nombre = db.Column(db.String(100), nullable=False)
    min_wp = db.Column(db.Numeric(8, 2),  nullable=False)
    max_kw = db.Column(db.Numeric(8, 2),  nullable=False)
    kwp = db.Column(db.Numeric(8,2))
    kw = db.Column(db.Numeric(8,2))
    precio_max = db.Column(db.Numeric(12, 2),  nullable=False)        
    direccion = db.Column(db.String(100), nullable=False)
    colonia = db.Column(db.String(100), nullable=False)
    cp_id = db.Column(db.Integer, db.ForeignKey('codigo_postal.id', ondelete="CASCADE"))
    latitud = db.Column(db.Numeric(7, 4),  nullable=False)
    longitud = db.Column(db.Numeric(7, 4),  nullable=False)
    status = db.Column(db.Integer,  nullable=False, default=0)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    pre_dimensionamiento = db.relationship('PreDimensionamiento', uselist=False, backref='oferta')
    dimensionamiento = db.relationship('Dimensionamiento', uselist=False, backref='oferta')
    adquisicion = db.relationship('Adquisicion', uselist=False, backref='oferta')
    instalacion = db.relationship('Instalacion', uselist=False, backref='oferta')
    puesta_en_marcha = db.relationship('PuestaEnMarcha', uselist=False, backref='oferta')

class PreDimensionamiento(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('oferta_licitacion.id'), primary_key=True)
    status_gestor = db.Column(db.Boolean, nullable=False, default=False)
    status_comprador = db.Column(db.Boolean, nullable=False, default=False)

class Dimensionamiento(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('oferta_licitacion.id'), primary_key=True)
    proyecto_ejecutivo_key = db.Column(db.String(50))
    status_comprador = db.Column(db.Boolean, nullable=False, default=False)

    @hybrid_property
    def create_presigned_url(self):
        """Generate a presigned URL to share an S3 object
            return: Presigned URL as string. If error, returns None.
        """
        s3 = boto3.client('s3')
        bucket_name = current_app.config['BUCKET']
        expiration = 3600
 
        # Generate a presigned URL for the S3 object
        try:
            response = s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": self.proyecto_ejecutivo_key},
                ExpiresIn=expiration,
            )
        except Exception as e:
            return None
    
        # The response contains the presigned URL
        return response
    
class Adquisicion(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('oferta_licitacion.id'), primary_key=True)

class Instalacion(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('oferta_licitacion.id'), primary_key=True)

class PuestaEnMarcha(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('oferta_licitacion.id'), primary_key=True)    

class OfertaProveedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    licitacion_id = db.Column(db.Integer, db.ForeignKey('licitacion.id'), nullable=False)
    num_max = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(8, 2),  nullable=False)
    integrador_id = db.Column(db.Integer, db.ForeignKey('integrador.id'), nullable=False)

    def __repr__(self):
        return f'<Oferta: {self.producto.type} Para: {self.licitacion.user.nombre}>'  

class OfertaCondicionada(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    oferta_1 = db.Column(db.Integer, db.ForeignKey('oferta_proveedor.id'), nullable=False)
    oferta_2 = db.Column(db.Integer, db.ForeignKey('oferta_proveedor.id'), nullable=False)

class OfertaGrupo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    integrador_id = db.Column(db.Integer, db.ForeignKey('integrador.id'), nullable=False)

class OfertaExcluyente(db.Model):
    grupo_id = db.Column(db.Integer, db.ForeignKey('oferta_grupo.id'), primary_key=True)
    oferta = db.Column(db.Integer, db.ForeignKey('oferta_proveedor.id'), primary_key=True)
    

@login.user_loader
def load_user(cog_user_id):
    return User.query.get(cog_user_id)