"""add_brand_profile_to_users

Revision ID: c006fbeda77e
Revises: cc4f512527a5
Create Date: 2026-01-09 21:15:43.300018

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c006fbeda77e'
down_revision: Union[str, Sequence[str], None] = 'cc4f512527a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add brand profile fields to users table
    op.add_column('users', sa.Column('brand_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('brand_description', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('brand_website', sa.String(), nullable=True))
    op.add_column('users', sa.Column('brand_competitors', sa.JSON(), nullable=True))
    op.add_column('users', sa.Column('brand_industry', sa.String(), nullable=True))
    op.add_column('users', sa.Column('brand_target_keywords', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove brand profile fields from users table
    op.drop_column('users', 'brand_target_keywords')
    op.drop_column('users', 'brand_industry')
    op.drop_column('users', 'brand_competitors')
    op.drop_column('users', 'brand_website')
    op.drop_column('users', 'brand_description')
    op.drop_column('users', 'brand_name')
