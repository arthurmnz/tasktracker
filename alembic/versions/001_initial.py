"""initial

Revision ID: 001_initial
Revises: 
Create Date: 2026-03-17 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg

revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'recurrence_rules',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', pg.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('interval', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('days_of_week', sa.JSON(), nullable=True),
        sa.Column('day_of_month', sa.Integer(), nullable=True),
        sa.Column('month_of_year', sa.Integer(), nullable=True),
        sa.Column('cron_expression', sa.String(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('max_occurrences', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'tasks',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', pg.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('priority', sa.String(), nullable=False),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('is_recurring', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('recurrence_rule_id', pg.UUID(as_uuid=True), nullable=True),
        sa.Column('parent_task_id', pg.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )


def downgrade():
    op.drop_table('tasks')
    op.drop_table('recurrence_rules')
    op.drop_table('users')
