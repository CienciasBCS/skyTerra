"""empty message

Revision ID: 23a72385e6f8
Revises: e4ba0e45feef
Create Date: 2021-08-05 12:10:05.349817

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '23a72385e6f8'
down_revision = 'e4ba0e45feef'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('consumo_info', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_consumo_info_created_at'), 'consumo_info', ['created_at'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_consumo_info_created_at'), table_name='consumo_info')
    op.drop_column('consumo_info', 'created_at')
    # ### end Alembic commands ###