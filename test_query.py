import psycopg2
import os
from dotenv import load_dotenv

load_dotenv("d:\\project\\AI Agent\\.env")
pg_uri = os.getenv('PG_URI', 'postgresql://postgres:0xSploit%401234@34.57.252.40:5432/medical_agent')

with psycopg2.connect(pg_uri) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT content FROM chat_history WHERE role='assistant' ORDER BY created_at DESC LIMIT 1")
        row = cur.fetchone()
        if row:
            print("--- FULL ASSISTANT MESSAGE ---")
            print(row[0])
            print("------------------------------")
