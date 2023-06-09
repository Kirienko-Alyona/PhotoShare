"""photo_m2m_tag fix

Revision ID: 48b3cfa769ee
Revises: 73c08b795382
Create Date: 2023-05-13 15:35:27.011458

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '48b3cfa769ee'
down_revision = '73c08b795382'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('photo_m2m_tag', sa.Column('photo_id', sa.Integer(), nullable=False))
    op.add_column('photo_m2m_tag', sa.Column('tag_id', sa.Integer(), nullable=False))
    op.drop_constraint('photo_m2m_tag_tag_fkey', 'photo_m2m_tag', type_='foreignkey')
    op.drop_constraint('photo_m2m_tag_photo_fkey', 'photo_m2m_tag', type_='foreignkey')
    op.drop_constraint('photo_m2m_tag_pkey', 'photo_m2m_tag', type_='primary')
    op.create_foreign_key(None, 'photo_m2m_tag', 'tags', ['tag_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'photo_m2m_tag', 'photos', ['photo_id'], ['id'], ondelete='CASCADE')
    op.create_primary_key('photo_m2m_tag_tag_pkey', 'photo_m2m_tag', ['photo_id', 'tag_id'])
    op.drop_column('photo_m2m_tag', 'tag')
    op.drop_column('photo_m2m_tag', 'id')
    op.drop_column('photo_m2m_tag', 'photo')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('photo_m2m_tag', sa.Column('photo', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('photo_m2m_tag', sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False))
    op.add_column('photo_m2m_tag', sa.Column('tag', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'photo_m2m_tag', type_='foreignkey')
    op.drop_constraint(None, 'photo_m2m_tag', type_='foreignkey')
    op.drop_constraint(None, 'photo_m2m_tag', type_='primary')
    op.create_foreign_key('photo_m2m_tag_photo_fkey', 'photo_m2m_tag', 'photos', ['photo'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('photo_m2m_tag_tag_fkey', 'photo_m2m_tag', 'tags', ['tag'], ['id'], ondelete='CASCADE')
    op.create_primary_key('photo_m2m_tag_tag_pkey', 'photo_m2m_tag', ['id'])
    op.drop_column('photo_m2m_tag', 'tag_id')
    op.drop_column('photo_m2m_tag', 'photo_id')
    # ### end Alembic commands ###
