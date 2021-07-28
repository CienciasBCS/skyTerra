"""empty message

Revision ID: 9cc3100537ea
Revises: e00bb8bd2960
Create Date: 2021-07-28 11:53:46.773243

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '9cc3100537ea'
down_revision = 'e00bb8bd2960'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('oferta_licitacion', sa.Column('nombre', sa.String(length=100), nullable=False))
    op.add_column('oferta_licitacion', sa.Column('tipo', sa.Integer(), nullable=False))
    op.add_column('oferta_licitacion', sa.Column('direccion', sa.String(length=100), nullable=False))
    op.add_column('oferta_licitacion', sa.Column('colonia', sa.String(length=100), nullable=False))
    op.add_column('oferta_licitacion', sa.Column('codigo_postal', sa.Integer(), nullable=False))
    op.add_column('oferta_licitacion', sa.Column('latitud', sa.Numeric(precision=7, scale=4), nullable=False))
    op.add_column('oferta_licitacion', sa.Column('longitud', sa.Numeric(precision=7, scale=4), nullable=False))
    op.add_column('oferta_licitacion', sa.Column('status', sa.Integer(), nullable=False))
    op.drop_column('oferta_licitacion', 'min_kw')
    op.drop_column('oferta_licitacion', 'max_wp')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('oferta_licitacion', sa.Column('max_wp', mysql.DECIMAL(precision=4, scale=2), nullable=False))
    op.add_column('oferta_licitacion', sa.Column('min_kw', mysql.DECIMAL(precision=4, scale=2), nullable=False))
    op.drop_column('oferta_licitacion', 'status')
    op.drop_column('oferta_licitacion', 'longitud')
    op.drop_column('oferta_licitacion', 'latitud')
    op.drop_column('oferta_licitacion', 'codigo_postal')
    op.drop_column('oferta_licitacion', 'colonia')
    op.drop_column('oferta_licitacion', 'direccion')
    op.drop_column('oferta_licitacion', 'tipo')
    op.drop_column('oferta_licitacion', 'nombre')
    # ### end Alembic commands ###