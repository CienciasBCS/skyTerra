"""empty message

Revision ID: bba6e7c3d57e
Revises: c014ac38478e
Create Date: 2021-08-20 15:16:00.953075

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bba6e7c3d57e'
down_revision = 'c014ac38478e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('oferta_proveedor', sa.Column('asignada', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('oferta_proveedor', 'asignada')
    # ### end Alembic commands ###
