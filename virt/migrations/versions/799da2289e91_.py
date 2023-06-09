"""empty message

Revision ID: 799da2289e91
Revises: a98559228e0e
Create Date: 2022-09-25 20:09:20.997782

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '799da2289e91'
down_revision = 'a98559228e0e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('profile_pic', sa.String(length=10000000), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'profile_pic')
    # ### end Alembic commands ###
