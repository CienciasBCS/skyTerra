"""empty message

Revision ID: 05eaaf4c36cc
Revises: 26d35dca3ef3
Create Date: 2021-07-09 18:52:58.642826

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '05eaaf4c36cc'
down_revision = '26d35dca3ef3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('oferta_grupo',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
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
    op.drop_table('oferta_grupo')
    # ### end Alembic commands ###
