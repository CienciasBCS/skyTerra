"""empty message

Revision ID: e00bb8bd2960
Revises: 0edd56c2c099
Create Date: 2021-07-28 10:43:49.683722

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e00bb8bd2960'
down_revision = '0edd56c2c099'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('oferta_licitacion',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('licitacion_id', sa.Integer(), nullable=False),
    sa.Column('comprador_id', sa.Integer(), nullable=False),
    sa.Column('gestor_id', sa.Integer(), nullable=True),
    sa.Column('min_kw', sa.Numeric(precision=4, scale=2), nullable=False),
    sa.Column('max_kw', sa.Numeric(precision=4, scale=2), nullable=False),
    sa.Column('min_wp', sa.Numeric(precision=4, scale=2), nullable=False),
    sa.Column('max_wp', sa.Numeric(precision=4, scale=2), nullable=False),
    sa.Column('precio_max', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.ForeignKeyConstraint(['comprador_id'], ['comprador.id'], ),
    sa.ForeignKeyConstraint(['gestor_id'], ['gestor.id'], ),
    sa.ForeignKeyConstraint(['licitacion_id'], ['licitacion.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('oferta_licitacion')
    # ### end Alembic commands ###