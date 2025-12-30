"""Add user and API key tables for authentication

Revision ID: 002
Revises: 001
Create Date: 2025-12-30 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False, comment='User email address (unique identifier)'),
        sa.Column('hashed_password', sa.String(length=255), nullable=False, comment='Bcrypt hashed password'),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, comment='Whether the user account is active'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, comment='Whether the user email has been verified'),
        sa.Column('role', sa.String(length=20), nullable=False, comment='User role (admin, user, viewer)'),
        sa.Column('pricing_tier', sa.String(length=20), nullable=False, comment='Current pricing tier'),
        sa.Column('monthly_iteration_quota', sa.Integer(), nullable=False, comment='Monthly iteration quota based on pricing tier'),
        sa.Column('iterations_used_this_month', sa.Integer(), nullable=False, comment='Iterations used in current billing period'),
        sa.Column('quota_reset_date', sa.DateTime(timezone=True), nullable=True, comment='When the monthly quota resets'),
        sa.Column('stripe_customer_id', sa.String(length=255), nullable=True, comment='Stripe customer ID for billing'),
        sa.Column('stripe_subscription_id', sa.String(length=255), nullable=True, comment='Stripe subscription ID'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('stripe_customer_id')
    )
    op.create_index('ix_users_created_at', 'users', ['created_at'])
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_pricing_tier', 'users', ['pricing_tier'])

    # Create API keys table
    op.create_table(
        'api_keys',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('key', sa.String(length=255), nullable=False, comment='Hashed API key (bcrypt)'),
        sa.Column('prefix', sa.String(length=10), nullable=False, comment="First 8 characters of key for display (e.g., 'sk_live_')"),
        sa.Column('name', sa.String(length=255), nullable=False, comment='User-provided name for the API key'),
        sa.Column('is_active', sa.Boolean(), nullable=False, comment='Whether the API key is active'),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True, comment='Last time this API key was used'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True, comment='When this API key expires (optional)'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True, comment='When this API key was revoked'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )
    op.create_index('ix_api_keys_created_at', 'api_keys', ['created_at'])
    op.create_index('ix_api_keys_key', 'api_keys', ['key'])
    op.create_index('ix_api_keys_user_active', 'api_keys', ['user_id', 'is_active'])
    op.create_index('ix_api_keys_user_id', 'api_keys', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_api_keys_user_id', table_name='api_keys')
    op.drop_index('ix_api_keys_user_active', table_name='api_keys')
    op.drop_index('ix_api_keys_key', table_name='api_keys')
    op.drop_index('ix_api_keys_created_at', table_name='api_keys')
    op.drop_table('api_keys')

    op.drop_index('ix_users_pricing_tier', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_created_at', table_name='users')
    op.drop_table('users')
