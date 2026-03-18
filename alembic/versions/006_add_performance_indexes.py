"""Add performance indexes for common query patterns.

Revision ID: 006_add_performance_indexes
Revises: e001_add_webhook_url_and_cost_tracking
Create Date: 2026-03-09 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "006_add_performance_indexes"
down_revision: Union[str, None] = "e001_add_webhook_url_and_cost_tracking"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Experiment listing: user_id + status + created_at (dashboard queries)
    op.create_index(
        "idx_experiments_user_status_created",
        "experiments",
        ["user_id", "status", "created_at"],
        if_not_exists=True,
    )

    # 2. Batch run aggregations: experiment_id + provider + status
    op.create_index(
        "idx_batch_runs_experiment_provider_status",
        "batch_runs",
        ["experiment_id", "provider", "status"],
        if_not_exists=True,
    )

    # 3. Iteration success lookups (partial index for successful iterations)
    op.create_index(
        "idx_iterations_batch_success",
        "iterations",
        ["batch_run_id", "is_success"],
        if_not_exists=True,
    )

    # 4. User tier and quota lookups
    op.create_index(
        "idx_users_tier_quota_reset",
        "users",
        ["pricing_tier", "quota_reset_date"],
        if_not_exists=True,
    )

    # 5. Recurring experiment scheduling
    op.create_index(
        "idx_experiments_next_run_recurring",
        "experiments",
        ["next_run_at", "is_recurring"],
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_index("idx_experiments_next_run_recurring", table_name="experiments")
    op.drop_index("idx_users_tier_quota_reset", table_name="users")
    op.drop_index("idx_iterations_batch_success", table_name="iterations")
    op.drop_index("idx_batch_runs_experiment_provider_status", table_name="batch_runs")
    op.drop_index("idx_experiments_user_status_created", table_name="experiments")
