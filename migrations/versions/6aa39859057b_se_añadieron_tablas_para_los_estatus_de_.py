"""se añadieron tablas para los estatus de cada oferta

Revision ID: 6aa39859057b
Revises: 957af7ea1138
Create Date: 2021-08-03 12:09:50.583969

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6aa39859057b'
down_revision = '957af7ea1138'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('adquisicion',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['oferta_licitacion.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('dimensionamiento',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['oferta_licitacion.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('instalacion',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['oferta_licitacion.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('pre_dimensionamiento',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('status_gestor', sa.Boolean(), nullable=False),
    sa.Column('status_comprador', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['oferta_licitacion.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('puesta_en_marcha',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['oferta_licitacion.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('puesta_en_marcha')
    op.drop_table('pre_dimensionamiento')
    op.drop_table('instalacion')
    op.drop_table('dimensionamiento')
    op.drop_table('adquisicion')
    # ### end Alembic commands ###
