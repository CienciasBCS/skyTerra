"""empty message

Revision ID: 5f5f8b9caffc
Revises: 9f7e358f0aaf
Create Date: 2021-07-12 09:04:10.171195

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5f5f8b9caffc'
down_revision = '9f7e358f0aaf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('marca',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=75), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('rol',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=25), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('producto',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('marca_id', sa.Integer(), nullable=True),
    sa.Column('type', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['marca_id'], ['marca.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('cog_user_id', sa.String(length=50), nullable=True),
    sa.Column('nombre', sa.String(length=100), nullable=True),
    sa.Column('apellidos', sa.String(length=100), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('telefono', sa.String(length=10), nullable=True),
    sa.Column('username', sa.String(length=100), nullable=True),
    sa.Column('rol_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['rol_id'], ['rol.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('cog_user_id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('telefono'),
    sa.UniqueConstraint('username')
    )
    op.create_table('inversor',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('modelo', sa.String(length=100), nullable=False),
    sa.Column('ficha_tecnica_key', sa.String(length=50), nullable=False),
    sa.Column('min_wp', sa.Integer(), nullable=False),
    sa.Column('max_wp', sa.Integer(), nullable=False),
    sa.Column('kw_ac', sa.Integer(), nullable=False),
    sa.Column('max_vdc', sa.Numeric(precision=4, scale=2), nullable=False),
    sa.Column('max_isc', sa.Numeric(precision=4, scale=2), nullable=False),
    sa.Column('max_imc', sa.Numeric(precision=4, scale=2), nullable=False),
    sa.Column('min_mppt', sa.Numeric(precision=4, scale=2), nullable=False),
    sa.Column('max_mppt', sa.Numeric(precision=4, scale=2), nullable=False),
    sa.Column('num_mppt', sa.Integer(), nullable=False),
    sa.Column('strings', sa.Integer(), nullable=False),
    sa.Column('efc', sa.Numeric(precision=4, scale=2), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['producto.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('licitacion',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('kwh', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('oferta_grupo',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('panel',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('modelo', sa.String(length=100), nullable=False),
    sa.Column('ficha_tecnica_key', sa.String(length=50), nullable=False),
    sa.Column('wp', sa.Integer(), nullable=False),
    sa.Column('vmp', sa.Numeric(precision=4, scale=2), nullable=False),
    sa.Column('imp', sa.Numeric(precision=4, scale=2), nullable=False),
    sa.Column('efc', sa.Numeric(precision=4, scale=2), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['producto.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('oferta_proveedor',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('producto_id', sa.Integer(), nullable=False),
    sa.Column('licitacion_id', sa.Integer(), nullable=False),
    sa.Column('num_max', sa.Integer(), nullable=False),
    sa.Column('precio_unitario', sa.Numeric(precision=8, scale=2), nullable=False),
    sa.ForeignKeyConstraint(['licitacion_id'], ['licitacion.id'], ),
    sa.ForeignKeyConstraint(['producto_id'], ['producto.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('oferta_condicionada',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('oferta_1', sa.Integer(), nullable=False),
    sa.Column('oferta_2', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['oferta_1'], ['oferta_proveedor.id'], ),
    sa.ForeignKeyConstraint(['oferta_2'], ['oferta_proveedor.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('oferta_excluyente',
    sa.Column('grupo_id', sa.Integer(), nullable=False),
    sa.Column('oferta', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['grupo_id'], ['oferta_grupo.id'], ),
    sa.ForeignKeyConstraint(['oferta'], ['oferta_proveedor.id'], ),
    sa.PrimaryKeyConstraint('grupo_id', 'oferta')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('oferta_excluyente')
    op.drop_table('oferta_condicionada')
    op.drop_table('oferta_proveedor')
    op.drop_table('panel')
    op.drop_table('oferta_grupo')
    op.drop_table('licitacion')
    op.drop_table('inversor')
    op.drop_table('user')
    op.drop_table('producto')
    op.drop_table('rol')
    op.drop_table('marca')
    # ### end Alembic commands ###
