
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update

from backend.app.core.config import get_settings
from backend.app.core.database import get_session_factory
from backend.app.models.experiment import Iteration
from backend.app.core.config import get_settings
from backend.app.core.database import get_session_factory
from backend.app.models.experiment import Iteration

logger = logging.getLogger(__name__)
settings = get_settings()

async def cleanup_old_pii_data() -> str:
    """
    Remove raw PII data from old iterations based on retention policy.
    
    This task nullifies the `raw_response` field for records older than
    `data_retention_days` setting.
    """
    retention_days = settings.data_retention_days
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
    
    logger.info(f"Starting PII data cleanup. Cutoff date: {cutoff_date} (Retention: {retention_days} days)")
    
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            # Update query to nullify raw_response for old records
            stmt = (
                update(Iteration)
                .where(Iteration.created_at < cutoff_date)
                .where(Iteration.raw_response.is_not(None))
                .values(raw_response=None)
            )
            
            result = await session.execute(stmt)
            await session.commit()
            
            rows_affected = result.rowcount
            msg = f"Cleaned up {rows_affected} iteration records older than {cutoff_date}"
            logger.info(msg)
            return msg
            
        except Exception as e:
            logger.error(f"Error during PII cleanup: {e}")
            await session.rollback()
            raise e
