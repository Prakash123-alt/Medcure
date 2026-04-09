import psycopg2

PG_URI = "postgresql://postgres:0xSploit%401234@34.57.252.40:5432/medical_agent"
try:
    conn = psycopg2.connect(PG_URI)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE whatsapp_number='web_user'")
    user = cursor.fetchone()
    if user:
        user_id = user[0]
        cursor.execute("DELETE FROM chat_history WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM prescriptions WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM semantic_memory WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        conn.commit()
        print(f"✅ Successfully reset web_user (ID: {user_id})")
    else:
        print("✅ web_user not found. Clean state.")
except Exception as e:
    print("Error:", e)
