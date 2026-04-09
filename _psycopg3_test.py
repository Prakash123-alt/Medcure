"""Simple psycopg3 async connection test"""
import asyncio, sys, os, warnings
warnings.filterwarnings("ignore")

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from dotenv import load_dotenv
load_dotenv()

async def main():
    import psycopg
    pg_uri = os.environ["PG_URI"]
    print(f"Connecting with psycopg3 to: {pg_uri[:40]}...")
    try:
        conn = await asyncio.wait_for(
            psycopg.AsyncConnection.connect(pg_uri, autocommit=True),
            timeout=10
        )
        row = await conn.execute("SELECT 1")
        result = await row.fetchone()
        print(f"Query result: {result}")
        await conn.close()
        print("PASS: psycopg3 async connection OK")
    except asyncio.TimeoutError:
        print("FAIL: Connection timed out after 10s")
    except Exception as e:
        print(f"FAIL: {e}")

asyncio.run(main())
