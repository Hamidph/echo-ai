
import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.experiment import Iteration, BatchRun, Experiment, ExperimentStatus, BatchRunStatus
from backend.app.models.user import User
from backend.app.tasks.maintenance import cleanup_old_pii_data
from backend.app.core.config import get_settings

# Access settings to create robust test
settings = get_settings()

@pytest.mark.asyncio
async def test_data_retention_policy(client, db_session: AsyncSession, test_user: User):
    """
    Verify that the cleanup task removes PII from old records but keeps new ones.
    """
    # 1. Setup Data
    # We need an experiment and batch run to link iterations to
    experiment = Experiment(
        user_id=test_user.id,
        prompt="Test Prompt",
        target_brand="Test Brand",
        status=ExperimentStatus.COMPLETED
    )
    db_session.add(experiment)
    await db_session.flush()
    
    batch_run = BatchRun(
        experiment_id=experiment.id,
        provider="openai",
        model="gpt-4o",
        status=BatchRunStatus.COMPLETED
    )
    db_session.add(batch_run)
    await db_session.flush()
    
    # Create OLD iteration (should be cleaned)
    # 31 days ago (assuming default 30 days retention)
    old_date = datetime.now(timezone.utc) - timedelta(days=31)
    
    old_iteration = Iteration(
        batch_run_id=batch_run.id,
        iteration_index=1,
        raw_response="SENSITIVE OLD DATA",
        created_at=old_date
    )
    db_session.add(old_iteration)
    
    # Create NEW iteration (should be kept)
    # 1 day ago
    new_date = datetime.now(timezone.utc) - timedelta(days=1)
    
    new_iteration = Iteration(
        batch_run_id=batch_run.id,
        iteration_index=2,
        raw_response="SENSITIVE NEW DATA",
        created_at=new_date
    )
    db_session.add(new_iteration)
    
    await db_session.commit()
    
    # Refresh to confirm creation
    await db_session.refresh(old_iteration)
    await db_session.refresh(new_iteration)
    
    # Manually override created_at because Postgres might use server time on insert defaults
    # Although we passed it in constructor, SQLAlchemy should respect it.
    # But let's force update via SQL to be absolutely sure we beat auto-timestamps
    await db_session.execute(
        update(Iteration)
        .where(Iteration.id == old_iteration.id)
        .values(created_at=old_date)
    )
    await db_session.execute(
        update(Iteration)
        .where(Iteration.id == new_iteration.id)
        .values(created_at=new_date)
    )
    await db_session.commit()
    
    assert old_iteration.raw_response == "SENSITIVE OLD DATA"
    assert new_iteration.raw_response == "SENSITIVE NEW DATA"
    
    # 2. Run Cleanup Task
    # We call the async function directly (bypassing Celery)
    msg = await cleanup_old_pii_data()
    print(f"\n[DEBUG] Cleanup result: {msg}")
    
    # 3. Verify Results
    await db_session.refresh(old_iteration)
    await db_session.refresh(new_iteration)
    
    # Old response should be None
    assert old_iteration.raw_response is None
    
    # New response should be intact
    assert new_iteration.raw_response == "SENSITIVE NEW DATA"
