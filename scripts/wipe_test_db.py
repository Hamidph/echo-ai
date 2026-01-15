
import asyncio
import asyncpg
import sys

async def wipe_test_db():
    try:
        # Connect to default postgres database
        conn = await asyncpg.connect(user='hamid', database='postgres', host='localhost')
        
        print("Dropping database ai_visibility_test...")
        # Terminate other connections first
        await conn.execute("""
            SELECT pg_terminate_backend(pid) 
            FROM pg_stat_activity 
            WHERE datname = 'ai_visibility_test' 
            AND pid <> pg_backend_pid()
        """)
        await conn.execute('DROP DATABASE IF EXISTS ai_visibility_test')
        await conn.execute('CREATE DATABASE ai_visibility_test')
        
        print("Database recreated successfully.")
        await conn.close()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(wipe_test_db())
