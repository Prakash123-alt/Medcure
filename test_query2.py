import psycopg2
import os
from dotenv import load_dotenv

load_dotenv("d:\\project\\AI Agent\\.env")
pg_uri = os.getenv('PG_URI')

with psycopg2.connect(pg_uri) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT content FROM chat_history WHERE role='assistant' ORDER BY created_at DESC LIMIT 1")
        row = cur.fetchone()
        if row:
            txt = row[0]
            print('LENGTH:', len(txt))
            print('LAST 150 CHARS:')
            print(txt[-150:])
            print('\nALL BUTTON STRINGS FOUND:')
            import re
            print(re.findall(r'\[BUTTON:.*?\]', txt))
