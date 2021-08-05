"""empty message

Revision ID: 3ddc45fe922b
Revises: 23a72385e6f8
Create Date: 2021-08-05 15:43:56.365255

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3ddc45fe922b'
down_revision = '23a72385e6f8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('consumo_info', sa.Column('rinv_inf_json', sa.JSON(), nullable=False))
    op.add_column('consumo_info', sa.Column('rinv_noinf_json', sa.JSON(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('consumo_info', 'rinv_noinf_json')
    op.drop_column('consumo_info', 'rinv_inf_json')
    # ### end Alembic commands ###
