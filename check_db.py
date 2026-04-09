import psycopg2
import os

PG_URI = "postgresql://postgres:0xSploit%401234@34.57.252.40:5432/medical_agent"
try:
    conn = psycopg2.connect(PG_URI)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, onboarding_step FROM users WHERE whatsapp_number='web_user'")
    user = cursor.fetchone()
    print("User:", user)

    if user:
        cursor.execute("SELECT role, content FROM chat_history WHERE user_id = %s ORDER BY created_at ASC", (user[0],))
        rows = cursor.fetchall()
        print(f"Chat History ({len(rows)} messages):")
        for r in rows:
            print(f"  {r[0]}: {r[1][:100]}...")
except Exception as e:
    print("Error:", e)
