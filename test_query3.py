import psycopg2
import os
from dotenv import load_dotenv

load_dotenv("d:\\project\\AI Agent\\.env")
pg_uri = os.getenv('PG_URI')

try:
    with psycopg2.connect(pg_uri) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT u.whatsapp_number, c.session_id, COUNT(c.message_id)
                FROM chat_history c
                JOIN users u ON c.user_id = u.user_id
                GROUP BY u.whatsapp_number, c.session_id
                ORDER BY COUNT(c.message_id) DESC
                LIMIT 5
            """)
            print("--- TOP SESSIONS ---")
            for row in cur.fetchall():
                print(row)
except Exception as e:
    print(f"Error: {e}")
