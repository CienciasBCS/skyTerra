"""empty message

Revision ID: 0edd56c2c099
Revises: 875be989a8df
Create Date: 2021-07-28 10:07:21.704482

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0edd56c2c099'
down_revision = '875be989a8df'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('licitacion', sa.Column('nombre', sa.String(length=75), nullable=False))
    op.add_column('licitacion', sa.Column('descripcion', sa.String(length=200), nullable=False))
    op.add_column('licitacion', sa.Column('agrupada', sa.Boolean(), nullable=False))
    op.add_column('licitacion', sa.Column('kwp_inst', sa.Numeric(precision=4, scale=2), nullable=False))
    op.add_column('licitacion', sa.Column('kw', sa.Numeric(precision=4, scale=2), nullable=False))
    op.add_column('licitacion', sa.Column('cant', sa.Numeric(precision=4, scale=2), nullable=False))
    op.add_column('licitacion', sa.Column('activa', sa.Boolean(), nullable=False))
    op.drop_column('licitacion', 'kwh')
    op.add_column('oferta_licitacion', sa.Column('gestor_id', sa.Integer(), nullable=True))
    op.alter_column('oferta_licitacion', 'licitacion_id',
               existing_type=mysql.INTEGER(),
               nullable=False)
    op.alter_column('oferta_licitacion', 'comprador_id',
               existing_type=mysql.INTEGER(),
               nullable=False)
    op.drop_constraint('oferta_licitacion_ibfk_1', 'oferta_licitacion', type_='foreignkey')
    op.create_foreign_key(None, 'oferta_licitacion', 'comprador', ['comprador_id'], ['id'])
    op.create_foreign_key(None, 'oferta_licitacion', 'gestor', ['gestor_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'oferta_licitacion', type_='foreignkey')
    op.drop_constraint(None, 'oferta_licitacion', type_='foreignkey')
    op.create_foreign_key('oferta_licitacion_ibfk_1', 'oferta_licitacion', 'user', ['comprador_id'], ['id'])
    op.alter_column('oferta_licitacion', 'comprador_id',
               existing_type=mysql.INTEGER(),
               nullable=True)
    op.alter_column('oferta_licitacion', 'licitacion_id',
               existing_type=mysql.INTEGER(),
               nullable=True)
    op.drop_column('oferta_licitacion', 'gestor_id')
    op.add_column('licitacion', sa.Column('kwh', mysql.INTEGER(), autoincrement=False, nullable=False))
    op.drop_column('licitacion', 'activa')
    op.drop_column('licitacion', 'cant')
    op.drop_column('licitacion', 'kw')
    op.drop_column('licitacion', 'kwp_inst')
    op.drop_column('licitacion', 'agrupada')
    op.drop_column('licitacion', 'descripcion')
    op.drop_column('licitacion', 'nombre')
    # ### end Alembic commands ###