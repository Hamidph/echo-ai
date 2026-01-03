"""add iteration status index

Revision ID: 004_add_iteration_status_index
Revises: d2d9f1e0f3ab
Create Date: 2026-01-02

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '004_add_iteration_status_index'
down_revision = 'd2d9f1e0f3ab'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add index on iterations.status for filtering by status."""
    op.create_index(
        'ix_iterations_status',
        'iterations',
        ['status'],
        unique=False
    )


def downgrade() -> None:
    """Remove index on iterations.status."""
    op.drop_index('ix_iterations_status', table_name='iterations')
