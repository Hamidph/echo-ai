import asyncio
import os
from uuid import UUID
from sqlalchemy import select
from backend.app.core.database import async_session_factory
from backend.app.models.experiment import Experiment

async def check_experiments():
    async with async_session_factory() as session:
        stmt = select(Experiment).order_by(Experiment.created_at.desc()).limit(10)
        result = await session.execute(stmt)
        experiments = result.scalars().all()
        
        print("\nLatest Experiments:")
        print("-" * 60)
        for exp in experiments:
            print(f"ID: {exp.id} | Status: {exp.status:10} | Brand: {exp.target_brand}")
        print("-" * 60)

if __name__ == "__main__":
    asyncio.run(check_experiments())
