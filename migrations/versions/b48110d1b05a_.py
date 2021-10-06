"""empty message

Revision ID: b48110d1b05a
Revises: ff89f9856d51
Create Date: 2021-09-20 14:22:24.553092

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b48110d1b05a'
down_revision = 'ff89f9856d51'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'adquisicion', ['oferta_prov_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'adquisicion', type_='unique')
    # ### end Alembic commands ###