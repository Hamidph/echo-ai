"""add performance indexes

Revision ID: 005_add_performance_indexes
Revises: d2d9f1e0f3ab
Create Date: 2026-01-15 10:00:00.000000

This migration adds critical database indexes to improve query performance
for the most common queries in the application:

1. Experiment listing (user's experiments filtered by status, sorted by date)
2. Dashboard aggregations (batch run metrics by provider)
3. Iteration analysis (brand extraction queries)
4. User quota queries (billing tier lookups)
5. Scheduled experiments (Celery Beat scheduler)

All indexes are created with CONCURRENTLY to avoid blocking production traffic.
"""
from alembic import op


# revision identifiers, used by Alembic
revision = '005_add_performance_indexes'
down_revision = 'd2d9f1e0f3ab'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add performance-critical indexes."""

    # Index 1: Experiment listing (most common query)
    # Supports: SELECT * FROM experiments WHERE user_id = ? AND status = ? ORDER BY created_at DESC
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_experiments_user_status_created
        ON experiments(user_id, status, created_at DESC)
    """)

    # Index 2: Dashboard aggregations (experiment metrics by provider)
    # Supports: SELECT metrics FROM batch_runs WHERE experiment_id = ? AND provider = ?
    # INCLUDE clause adds metrics columns to index (covering index, no table lookup needed)
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_batch_runs_experiment_provider_status
        ON batch_runs(experiment_id, provider, status)
        INCLUDE (metrics, total_tokens, completed_at)
    """)

    # Index 3: Iteration analysis (brand extraction queries)
    # Supports: SELECT * FROM iterations WHERE batch_run_id = ? AND is_success = true
    # Partial index (WHERE clause) reduces index size and improves performance
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_iterations_batch_success_brands
        ON iterations(batch_run_id, is_success)
        WHERE extracted_brands IS NOT NULL
    """)

    # Index 4: User quota queries (billing tier lookups)
    # Supports: SELECT * FROM users WHERE pricing_tier = ? AND quota_reset_date < NOW()
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_tier_quota_reset
        ON users(pricing_tier, quota_reset_date)
    """)

    # Index 5: Scheduled experiments (Celery Beat scheduler)
    # Supports: SELECT * FROM experiments WHERE is_recurring = true AND next_run_at < NOW()
    # Partial index optimizes recurring experiment queries
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_experiments_next_run_recurring
        ON experiments(next_run_at)
        WHERE is_recurring = true AND status != 'cancelled'
    """)

    # Index 6: User email lookup (login queries)
    # Email is already unique, but explicit index improves login performance
    # This is actually redundant (unique constraint creates index), but explicit for clarity
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email_active
        ON users(email)
        WHERE is_active = true
    """)


def downgrade() -> None:
    """Remove performance indexes."""

    # Drop indexes in reverse order
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_users_email_active")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_experiments_next_run_recurring")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_users_tier_quota_reset")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_iterations_batch_success_brands")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_batch_runs_experiment_provider_status")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_experiments_user_status_created")
