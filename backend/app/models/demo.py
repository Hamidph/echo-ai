from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, DateTime, String, Integer
from sqlalchemy.dialects.postgresql import UUID
from backend.app.core.database import Base

class DemoUsage(Base):
    """
    Track usage of the public demo endpoint.
    """
    __tablename__ = "demo_usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    target_brand = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    ip_address = Column(String, nullable=True)
    prompt = Column(String, nullable=True)
