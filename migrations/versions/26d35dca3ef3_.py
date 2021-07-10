"""empty message

Revision ID: 26d35dca3ef3
Revises: b9fabb2969e4
Create Date: 2021-07-09 18:36:30.729516

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '26d35dca3ef3'
down_revision = 'b9fabb2969e4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('licitacion',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('kwh', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('oferta_proveedor', sa.Column('licitacion_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'oferta_proveedor', 'licitacion', ['licitacion_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'oferta_proveedor', type_='foreignkey')
    op.drop_column('oferta_proveedor', 'licitacion_id')
    op.drop_table('licitacion')
    # ### end Alembic commands ###
