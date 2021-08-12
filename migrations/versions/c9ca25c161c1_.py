"""empty message

Revision ID: c9ca25c161c1
Revises: a0982a032af1
Create Date: 2021-08-12 12:12:34.499860

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c9ca25c161c1'
down_revision = 'a0982a032af1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('licitacion_privada_ibfk_4', 'licitacion_privada', type_='foreignkey')
    op.create_foreign_key(None, 'licitacion_privada', 'licitacion', ['id'], ['id'])
    op.add_column('oferta_licitacion', sa.Column('activa', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('oferta_licitacion', 'activa')
    op.drop_constraint(None, 'licitacion_privada', type_='foreignkey')
    op.create_foreign_key('licitacion_privada_ibfk_4', 'licitacion_privada', 'licitacion', ['id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###