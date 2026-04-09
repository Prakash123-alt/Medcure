import psycopg2, os
from dotenv import load_dotenv

load_dotenv("d:\\project\\AI Agent\\.env")
pg_uri = os.getenv("PG_URI")

try:
    with psycopg2.connect(pg_uri) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT u.whatsapp_number, count(c.message_id) 
                FROM users u 
                LEFT JOIN chat_history c ON u.user_id = c.user_id 
                GROUP BY u.whatsapp_number 
                ORDER BY count(c.message_id) DESC 
                LIMIT 10
            """)
            print("USER CHAT COUNTS:")
            for row in cur.fetchall():
                print(row)
except Exception as e:
    print(e)
