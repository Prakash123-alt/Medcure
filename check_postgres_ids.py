import asyncio
from medical_ai_agent.database import init_db_pool, get_db_connection, close_db_pool

async def check_ids():
    await init_db_pool()
    async with get_db_connection() as conn:
        r = await conn.fetch("SELECT id FROM aiims_guidelines ORDER BY id LIMIT 5")
        print("FIRST 5 IDs:")
        for row in r:
            print(row['id'])
            
        r2 = await conn.fetch("SELECT id FROM aiims_guidelines ORDER BY id OFFSET 200 LIMIT 5")
        print("\nOFFSET 200 IDs:")
        for row in r2:
            print(row['id'])
            
    await close_db_pool()

if __name__ == "__main__":
    asyncio.run(check_ids())
