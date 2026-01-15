
import asyncio
import asyncpg
import sys

async def create_test_db():
    try:
        # Connect to default postgres database
        conn = await asyncpg.connect(user='hamid', database='postgres', host='localhost')
        
        # Check if database exists
        exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname = 'ai_visibility_test'")
        
        if not exists:
            print("Creating database ai_visibility_test...")
            await conn.execute('CREATE DATABASE ai_visibility_test')
            print("Database created successfully.")
        else:
            print("Database ai_visibility_test already exists.")
            
        await conn.close()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(create_test_db())
