"""empty message

Revision ID: 63bfa63f34e4
Revises: 1b6ae3c3a858
Create Date: 2021-08-18 15:48:24.145884

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '63bfa63f34e4'
down_revision = '1b6ae3c3a858'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_pending',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('rol_solicitado', sa.String(length=30), nullable=False),
    sa.Column('aceptado', sa.Boolean(), nullable=True),
    sa.Column('fecha_peticion', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_pending_fecha_peticion'), 'user_pending', ['fecha_peticion'], unique=False)
    op.create_table('admin',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['user_role.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('admin')
    op.drop_index(op.f('ix_user_pending_fecha_peticion'), table_name='user_pending')
    op.drop_table('user_pending')
    # ### end Alembic commands ###
