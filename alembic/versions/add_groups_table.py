"""add groups table

Revision ID: add_groups_table
Revises: c1e20e7b4b81
Create Date: 2025-09-05 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'add_groups_table'
down_revision: Union[str, Sequence[str], None] = 'c1e20e7b4b81'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'groups',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('owner_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('avatar_url', sa.String(), nullable=True),
    )
    op.create_index(op.f('ix_groups_id'), 'groups', ['id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_groups_id'), table_name='groups')
    op.drop_table('groups')
