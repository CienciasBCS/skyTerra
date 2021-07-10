"""empty message

Revision ID: 72f82be3ddda
Revises: adbf922d0ee7
Create Date: 2021-07-09 17:25:34.918685

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '72f82be3ddda'
down_revision = 'adbf922d0ee7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('producto', sa.Column('type', sa.String(length=50), nullable=True))
    op.drop_column('producto', 'tipo')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('producto', sa.Column('tipo', mysql.VARCHAR(length=50), nullable=True))
    op.drop_column('producto', 'type')
    # ### end Alembic commands ###
