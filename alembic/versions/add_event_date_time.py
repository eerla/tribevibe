"""add event date/time split and FK

Revision ID: add_event_date_time
Revises: 84fa24844985
Create Date: 2025-08-28 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'add_event_date_time'
down_revision: Union[str, Sequence[str], None] = '84fa24844985'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.drop_table('events')
    op.create_table(
        'events',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('date', sa.DateTime(timezone=False), nullable=False),
        sa.Column('time', sa.String(), nullable=False),
        sa.Column('location', sa.String(), nullable=False),
        sa.Column('organizer_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )
    op.create_index(op.f('ix_events_id'), 'events', ['id'], unique=False)

def downgrade() -> None:
    op.drop_table('events')
    op.create_table(
        'events',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('organizer_id', sa.Integer(), nullable=False),
    )
    op.create_index(op.f('ix_events_id'), 'events', ['id'], unique=False)
