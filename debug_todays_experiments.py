import asyncio
import os
from datetime import datetime, timezone
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# Setup simple async engine
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://appuser:apppassword@localhost:5432/ai_visibility")
# Adjust for local railway connection if needed or assume running in environment with access
# Since I'm on the user's machine, I might need the actual DB URL. 
# I will try to read .env first, but usually run_command in this env might rely on `railway run` or similar if the DB is remote.
# For now, I'll assume I can access the DB if I use the correct credentials. 
# But wait, the user is on Mac, the DB is on Railway. I cannot connect directly via localhost unless I proxy.
# BETTER APPROACH: Use `railway run python script.py` to run it in the context of the infra? 
# Or just read the .env and hope it's exposed?
# The user's active document is `.env`. I can see it.

async def check_experiments():
    # Load env vars manually if needed, but let's assume valid DATABASE_URL is available or passed
    # I'll rely on `railway run` to inject vars.
    
    # Just in case `railway run` isn't used, I will check the user's .env content first? 
    # No, I will write this script to rely on os.environ and run it via `railway run`.
    
    engine = create_async_engine(os.environ["DATABASE_URL"])
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        today = datetime.now(timezone.utc).date()
        print(f"Checking experiments for date (UTC): {today}")
        
        # Query all experiments updated or completed today
        stmt = text("""
            SELECT id, status, completed_at, target_brand 
            FROM experiments 
            WHERE DATE(completed_at) = :today OR DATE(created_at) = :today
        """)
        
        result = await session.execute(stmt, {"today": today})
        experiments = result.fetchall()
        
        print(f"Found {len(experiments)} experiments interacting today:")
        for exp in experiments:
            print(f"- ID: {exp.id}, Status: {exp.status}, Completed At: {exp.completed_at}")

        if not experiments:
            print("No experiments found for today.")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_experiments())
