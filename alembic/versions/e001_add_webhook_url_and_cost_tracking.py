"""Add webhook_url to users and estimated_cost_usd to batch_runs

Revision ID: e001_add_webhook_url_and_cost_tracking
Revises: c006fbeda77e
Create Date: 2026-03-09 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e001_add_webhook_url_and_cost_tracking"
down_revision: Union[str, None] = "c006fbeda77e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add webhook_url to users table
    op.add_column(
        "users",
        sa.Column(
            "webhook_url",
            sa.String(500),
            nullable=True,
            comment="Webhook URL to notify on experiment completion",
        ),
    )

    # Add estimated_cost_usd to batch_runs table
    op.add_column(
        "batch_runs",
        sa.Column(
            "estimated_cost_usd",
            sa.Float(),
            nullable=True,
            comment="Estimated API cost in USD based on token usage",
        ),
    )


def downgrade() -> None:
    op.drop_column("batch_runs", "estimated_cost_usd")
    op.drop_column("users", "webhook_url")
