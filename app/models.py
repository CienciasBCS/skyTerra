from datetime import datetime
from enum import unique
import re

import boto3
from sqlalchemy.ext.hybrid import hybrid_property
from flask_login import UserMixin
from flask import current_app
from app import ma

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
    tiene_rol = db.Column(db.Boolean)
    user_rol = db.relationship('UserRole', backref='user', uselist=False, cascade="all,delete")
    user_pending = db.relationship('UserPending', backref='user', uselist=False, cascade="all,delete")
    # rol_id = db.Column(db.Integer, db.ForeignKey('rol.id'))

    # @hybrid_property
    def create_presigned_url(self, file):
        """Generate a presigned URL to share an S3 object
            return: Presigned URL as string. If error, returns None.
        """
        s3 = boto3.client('s3')
        bucket_name = current_app.config['BUCKET']
        expiration = 3600
        key_files = {
            'acta_const': self.acta_constitutiva_key, 'doc1': self.doc_req1_key,
            'doc2': self.doc_req2_key, 'doc3': self.doc_req3_key
        }

 
        try:
            response = s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": key_files[file]},
                ExpiresIn=expiration,
            )
        except Exception as e:
            return None
    
        # The response contains the presigned URL
        return response

    def __repr__(self):
        return f'<User {self.cog_user_id}>' 

class UserPending(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    rol_solicitado = db.Column(db.String(30), nullable=False)
    aceptado = db.Column(db.Boolean)
    fecha_peticion = db.Column(db.DateTime, index=True, default=datetime.utcnow)

class UserRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), unique=True)
    tipo = db.Column(db.String(25))

    __mapper_args__ = {
        'polymorphic_identity':'user_role',
        'polymorphic_on': tipo
    }

class Admin(UserRole):
    id = db.Column(db.Integer, db.ForeignKey('user_role.id', ondelete="CASCADE"), primary_key=True)
    __mapper_args__ = {
        'polymorphic_identity':'admin',
    }

    def get_pending_users(self):
        return len(UserPending.query.filter(UserPending.aceptado == None).all())

class Comprador(UserRole):
    id = db.Column(db.Integer, db.ForeignKey('user_role.id', ondelete="CASCADE"), primary_key=True)
    atr = db.Column(db.String(10))
    ofertas = db.relationship('OfertaLicitacion', backref='comprador')
    licitaciones_privadas = db.relationship('LicitacionPrivada', backref='creador')

    __mapper_args__ = {
        'polymorphic_identity':'comprador',
    }

    def has_licit_priv_agrupadas(self):
        return bool(LicitacionPrivada.query.filter_by(agrupada=True, comprador_id=self.id).all())

    def get_licit_priv_agrupadas(self):
        return LicitacionPrivada.query.filter_by(agrupada=True, comprador_id=self.id).all()

    def get_total_number_of_pending_offers(self):
        return len(
            OfertaLicitacion.query.join(LicitacionPrivada)\
                .filter(OfertaLicitacion.aceptada==None,
                        LicitacionPrivada.comprador_id==self.id).all()
        )

    def get_ofertas_by_status(self, status_id):
        return OfertaLicitacion.query.filter_by(status=status_id, aceptada=True, comprador_id=self.id).all()
    
    def get_ofertas_activas(self):
        return OfertaLicitacion.query.join(Licitacion).filter(Licitacion.activa == True, OfertaLicitacion.comprador_id == self.id).all()

class Gestor(UserRole):
    id = db.Column(db.Integer, db.ForeignKey('user_role.id', ondelete="CASCADE"), primary_key=True)
    ofertas = db.relationship('OfertaLicitacion', backref='gestor')
    codigo = db.Column(db.String(6), index=True, default=util.get_random_code, unique=True)

    __mapper_args__ = {
        'polymorphic_identity':'gestor',
    }

    def get_ofertas_by_status(self, status_id):
        return OfertaLicitacion.query.filter_by(status=status_id, aceptada=True, gestor_id=self.id).all()
    
    def get_ofertas_activas(self):
        return OfertaLicitacion.query.join(Licitacion).filter(Licitacion.activa == True, OfertaLicitacion.gestor_id == self.id).all()

class Integrador(UserRole):
    id = db.Column(db.Integer, db.ForeignKey('user_role.id', ondelete="CASCADE"), primary_key=True)
    ofertas = db.relationship('OfertaProveedor', backref='integrador')

    def get_licitaciones_con_ofertas(self):
        return Licitacion.query.join(OfertaLicitacion).join(OfertaProveedor).filter(
            OfertaProveedor.integrador_id == self.id, Licitacion.activa == True,
            OfertaLicitacion.aceptada == True
        ).all()

    def get_ofertas_disponibles(self):
        return OfertaLicitacion.query.join(Adquisicion).\
            filter(OfertaLicitacion.status == 2, Adquisicion.oferta_prov_id == None).all()

    def get_ofertas_en_instalacion(self):
        return OfertaLicitacion.query.join(Adquisicion).join(OfertaProveedor).\
            filter(OfertaLicitacion.status == 3, OfertaProveedor.integrador_id == self.id).all()

    __mapper_args__ = {
        'polymorphic_identity':'integrador',
    }    

class Licitacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agrupada = db.Column(db.Boolean, nullable=False, default=False)
    kwp_inst = db.Column(db.Numeric(4, 2))
    kw = db.Column(db.Numeric(4, 2))
    cant = db.Column(db.Numeric(4, 2))
    activa = db.Column(db.Boolean, nullable=False, default=True)
    tipo = db.Column(db.String(25))
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    ofertas = db.relationship('OfertaLicitacion', backref='licitacion', cascade="all,delete")
    oferta_venta_asignada = db.Column(db.Boolean, nullable=False, default=False)

    __mapper_args__ = {
        'polymorphic_identity':'licitacion',
        'polymorphic_on': tipo
    }
    
    def is_predim_ofertas_complete(self):
        return all([oferta.pre_dimensionamiento.is_complete for oferta in self.ofertas if oferta.aceptada])

    def is_dimen_ofertas_complete(self):
        return all([oferta.dimensionamiento.is_complete for oferta in self.ofertas if oferta.aceptada])

    def get_total_kw_ofertas(self):
        return sum([oferta.kw for oferta in self.ofertas if oferta.kw])

    def get_total_kwp_ofertas(self):
        return sum([oferta.kwp for oferta in self.ofertas if oferta.kwp])
    
    def get_total_number_of_ofertas_compra(self):
        return len(self.ofertas)

    def get_total_number_of_ofertas_prov(self):
        total_ofertas_prov = 0
        for oferta in self.ofertas:
            total_ofertas_prov += len(oferta.ofertas_proveedores)
        return total_ofertas_prov
    
    def __repr__(self):
        return f'<kwh: {self.kw}>'  

class LicitacionPrivada(Licitacion):
    id = db.Column(db.Integer, db.ForeignKey('licitacion.id'), primary_key=True)
    comprador_id = db.Column(db.Integer, db.ForeignKey('comprador.id'), nullable=False)
    codigo = db.Column(db.String(6), index=True, default=util.get_random_code, unique=True)

    __mapper_args__ = {
        'polymorphic_identity':'licitacion_privada',
        'with_polymorphic': '*'
    }

    def get_number_of_pending_offers(self):
        return len(
            OfertaLicitacion.query.join(LicitacionPrivada)\
                .filter(OfertaLicitacion.aceptada==None, LicitacionPrivada.id==self.id).all()
        )

    def get_pending_offers(self):
        return OfertaLicitacion.query.join(LicitacionPrivada)\
                .filter(OfertaLicitacion.aceptada==None, LicitacionPrivada.id==self.id).all()
        

    def __repr__(self):
        return f'<Código: {self.codigo}>'  

class LicitacionPublica(Licitacion):
    id = db.Column(db.Integer, db.ForeignKey('licitacion.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'licitacion_publica',
    }

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
    aceptada = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    pre_dimensionamiento = db.relationship('PreDimensionamiento', uselist=False, backref='oferta', cascade="all, delete-orphan")
    dimensionamiento = db.relationship('Dimensionamiento', uselist=False, backref='oferta', cascade="all, delete-orphan")
    adquisicion = db.relationship('Adquisicion', uselist=False, backref='oferta', cascade="all, delete-orphan")
    instalacion = db.relationship('Instalacion', uselist=False, backref='oferta', cascade="all, delete-orphan")
    puesta_en_marcha = db.relationship('PuestaEnMarcha', uselist=False, backref='oferta', cascade="all, delete-orphan")
    ofertas_proveedores = db.relationship('OfertaProveedor', uselist=True, backref='oferta_compra')

    def get_comprador_ofertas_by_status(self, status_id):
        return self.query.join(Licitacion).filter(Licitacion.status == status_id, 
                Comprador.id==self.comprador_id, self.aceptada == True).all()

    def is_oferta_instalada(self):
        return all([self.instalacion.confirmacion_comprador, self.instalacion.confirmacion_integrador, 
                self.instalacion.confirmacion_gestor])

    def __repr__(self):
        return f'<kwh: {self.nombre}>'                  

class PreDimensionamiento(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('oferta_licitacion.id'), primary_key=True)
    status_gestor = db.Column(db.Boolean, nullable=False, default=False)
    status_comprador = db.Column(db.Boolean, nullable=False, default=False)

    @property
    def is_complete(self):
        return self.status_gestor and self.status_comprador

class Dimensionamiento(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('oferta_licitacion.id'), primary_key=True)
    proyecto_ejecutivo_key = db.Column(db.String(50))
    status_comprador = db.Column(db.Boolean, nullable=False, default=False)

    @property
    def is_complete(self):
        return bool(self.proyecto_ejecutivo_key) and self.status_comprador

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
    oferta_prov_id = db.Column(db.Integer, db.ForeignKey('oferta_proveedor.id'), unique=True)

    oferta_proveedor = db.relationship('OfertaProveedor', uselist=False, backref='adquisicion')
    # integrador_id = db.Column(db.Integer, db.ForeignKey('integrador.id'))

class Instalacion(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('oferta_licitacion.id'), primary_key=True)
    confirmacion_integrador = db.Column(db.Boolean, default=False, nullable=False)
    confirmacion_comprador = db.Column(db.Boolean, default=False, nullable=False)
    confirmacion_gestor = db.Column(db.Boolean, default=False, nullable=False)
    
class PuestaEnMarcha(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('oferta_licitacion.id'), primary_key=True)    
    finished_at = db.Column(db.DateTime, index=True)

class OfertaProveedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    oferta_id = db.Column(db.Integer, db.ForeignKey('oferta_licitacion.id'), nullable=False)
    integrador_id = db.Column(db.Integer, db.ForeignKey('integrador.id'), nullable=False)
    precio = db.Column(db.Numeric(8, 2),  nullable=False)
    asignada = db.Column(db.Boolean)

    def __repr__(self):
        return f'<Precio: {self.precio} Para: {self.oferta_compra.nombre}>'  

# class OfertaCondicionada(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     oferta_1 = db.Column(db.Integer, db.ForeignKey('oferta_proveedor.id'), nullable=False)
#     oferta_2 = db.Column(db.Integer, db.ForeignKey('oferta_proveedor.id'), nullable=False)

# class OfertaGrupo(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     integrador_id = db.Column(db.Integer, db.ForeignKey('integrador.id'), nullable=False)

# class OfertaExcluyente(db.Model):
#     grupo_id = db.Column(db.Integer, db.ForeignKey('oferta_grupo.id'), primary_key=True)
#     oferta = db.Column(db.Integer, db.ForeignKey('oferta_proveedor.id'), primary_key=True)
    

# --------- SCHEMAS ---------
class CodigoPostalSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CodigoPostal

class PreDimensionamientoSchema(ma.SQLAlchemyAutoSchema):
    is_complete = ma.Boolean()
    class Meta:
        model = PreDimensionamiento

class DimensionamientoSchema(ma.SQLAlchemyAutoSchema):
    is_complete = ma.Boolean()
    class Meta:
        model = Dimensionamiento        

class OfertaLicitacionSchema(ma.SQLAlchemyAutoSchema):
    precio_max = ma.Decimal(as_string=True)
    max_kw = ma.Decimal(as_string=True)
    min_wp = ma.Decimal(as_string=True)
    kw = ma.Decimal(as_string=True)
    kwp = ma.Decimal(as_string=True)
    latitud = ma.Decimal(as_string=True)
    longitud = ma.Decimal(as_string=True)
    cp = ma.Nested(CodigoPostalSchema(only=('estado', 'municipio')))

    class Meta:
        model = OfertaLicitacion

class LicitacionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Licitacion

    
    codigo = ma.Nested(CodigoPostalSchema(only=('estado', 'municipio')), many=True)
    ofertas = ma.Nested(OfertaLicitacionSchema(), many=True)

class OfertaProveedorSchema(ma.SQLAlchemyAutoSchema):
    precio = ma.Decimal(as_string=True)

    class Meta:
        model = OfertaProveedor

    oferta_compra = ma.Nested(OfertaLicitacionSchema())

@login.user_loader
def load_user(cog_user_id):
    return User.query.get(cog_user_id)