"""Initial schema with experiments, batch_runs, and iterations

Revision ID: 001
Revises:
Create Date: 2025-12-30 21:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create experiments table
    op.create_table(
        'experiments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=False, comment='The prompt to run N times for visibility analysis'),
        sa.Column('target_brand', sa.String(length=255), nullable=False, comment='Primary brand to track visibility for'),
        sa.Column('competitor_brands', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='List of competitor brands for Share of Voice analysis'),
        sa.Column('domain_whitelist', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Allowed domains for hallucination detection'),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=False, comment='Experiment configuration (iterations, temperature, etc.)'),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True, comment='Error message if experiment failed'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_experiments_created_at', 'experiments', ['created_at'])
    op.create_index('ix_experiments_status', 'experiments', ['status'])
    op.create_index('ix_experiments_status_created', 'experiments', ['status', 'created_at'])
    op.create_index('ix_experiments_target_brand', 'experiments', ['target_brand'])

    # Create batch_runs table
    op.create_table(
        'batch_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('experiment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False, comment='LLM provider (openai, anthropic, perplexity)'),
        sa.Column('model', sa.String(length=100), nullable=False, comment='Specific model used (e.g., gpt-4o, sonar)'),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_ms', sa.Float(), nullable=True, comment='Total execution time in milliseconds'),
        sa.Column('metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Computed analytics: visibility_rate, consistency_score, etc.'),
        sa.Column('total_iterations', sa.Integer(), nullable=False),
        sa.Column('successful_iterations', sa.Integer(), nullable=False),
        sa.Column('failed_iterations', sa.Integer(), nullable=False),
        sa.Column('total_tokens', sa.Integer(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['experiment_id'], ['experiments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_batch_runs_experiment_id', 'batch_runs', ['experiment_id'])
    op.create_index('ix_batch_runs_experiment_provider', 'batch_runs', ['experiment_id', 'provider'])
    op.create_index('ix_batch_runs_provider', 'batch_runs', ['provider'])
    op.create_index('ix_batch_runs_status', 'batch_runs', ['status'])

    # Create iterations table
    op.create_table(
        'iterations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('batch_run_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('iteration_index', sa.Integer(), nullable=False, comment='Zero-based index within the batch'),
        sa.Column('raw_response', sa.Text(), nullable=True, comment='Complete LLM response text for variance analysis'),
        sa.Column('latency_ms', sa.Float(), nullable=True, comment='Response latency in milliseconds'),
        sa.Column('is_success', sa.Boolean(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, comment='Iteration status: success, failed, rate_limited, timeout'),
        sa.Column('extracted_brands', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Brands mentioned in this response'),
        sa.Column('citations', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Source URLs from Perplexity responses'),
        sa.Column('prompt_tokens', sa.Integer(), nullable=True),
        sa.Column('completion_tokens', sa.Integer(), nullable=True),
        sa.Column('total_tokens', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['batch_run_id'], ['batch_runs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_iterations_batch_run_id', 'iterations', ['batch_run_id'])
    op.create_index('ix_iterations_batch_index', 'iterations', ['batch_run_id', 'iteration_index'])
    op.create_index('ix_iterations_batch_success', 'iterations', ['batch_run_id', 'is_success'])
    op.create_index('ix_iterations_is_success', 'iterations', ['is_success'])


def downgrade() -> None:
    op.drop_index('ix_iterations_is_success', table_name='iterations')
    op.drop_index('ix_iterations_batch_success', table_name='iterations')
    op.drop_index('ix_iterations_batch_index', table_name='iterations')
    op.drop_index('ix_iterations_batch_run_id', table_name='iterations')
    op.drop_table('iterations')

    op.drop_index('ix_batch_runs_status', table_name='batch_runs')
    op.drop_index('ix_batch_runs_provider', table_name='batch_runs')
    op.drop_index('ix_batch_runs_experiment_provider', table_name='batch_runs')
    op.drop_index('ix_batch_runs_experiment_id', table_name='batch_runs')
    op.drop_table('batch_runs')

    op.drop_index('ix_experiments_target_brand', table_name='experiments')
    op.drop_index('ix_experiments_status_created', table_name='experiments')
    op.drop_index('ix_experiments_status', table_name='experiments')
    op.drop_index('ix_experiments_created_at', table_name='experiments')
    op.drop_table('experiments')
