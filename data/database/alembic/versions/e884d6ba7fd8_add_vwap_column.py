"""add vwap column

Revision ID: e884d6ba7fd8
Revises: edc25726b16e
Create Date: 2022-04-24 14:51:41.578474

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e884d6ba7fd8'
down_revision = 'edc25726b16e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ticker_prices', sa.Column('vwap', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('ticker_prices', 'vwap')
    # ### end Alembic commands ###
