"""empty message

Revision ID: 0fa42b1ea1ab
Revises: 3aadbe040ab3
Create Date: 2021-04-28 15:47:04.268039

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0fa42b1ea1ab'
down_revision = '3aadbe040ab3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('genres', sa.ARRAY(sa.String()), nullable=True))
    op.add_column('Venue', sa.Column('looking_for_talent', sa.Boolean(), nullable=True))
    op.add_column('Venue', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    op.add_column('Venue', sa.Column('website_link', sa.String(length=200), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'website_link')
    op.drop_column('Venue', 'seeking_description')
    op.drop_column('Venue', 'looking_for_talent')
    op.drop_column('Venue', 'genres')
    # ### end Alembic commands ###
