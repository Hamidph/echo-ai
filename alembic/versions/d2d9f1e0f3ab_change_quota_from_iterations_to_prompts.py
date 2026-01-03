"""Change quota from iterations to prompts

Revision ID: d2d9f1e0f3ab
Revises: 003
Create Date: 2026-01-01 02:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd2d9f1e0f3ab'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename columns from iterations to prompts
    op.alter_column('users', 'monthly_iteration_quota',
                    new_column_name='monthly_prompt_quota',
                    existing_type=sa.Integer(),
                    existing_nullable=False,
                    existing_server_default='100')

    op.alter_column('users', 'iterations_used_this_month',
                    new_column_name='prompts_used_this_month',
                    existing_type=sa.Integer(),
                    existing_nullable=False,
                    existing_server_default='0')


def downgrade() -> None:
    # Revert column names
    op.alter_column('users', 'monthly_prompt_quota',
                    new_column_name='monthly_iteration_quota',
                    existing_type=sa.Integer(),
                    existing_nullable=False)

    op.alter_column('users', 'prompts_used_this_month',
                    new_column_name='iterations_used_this_month',
                    existing_type=sa.Integer(),
                    existing_nullable=False)
