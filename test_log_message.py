import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
PG_URI = os.getenv("PG_URI", "postgresql://postgres:0xSploit%401234@34.57.252.40:5432/medical_agent")

from medical_ai_agent.api import log_message, get_or_create_user, get_session_id

try:
    user_id, _, _, _ = get_or_create_user("web_user")
    session_id = get_session_id(user_id)
    print("User ID:", user_id)
    print("Session ID:", session_id)
    
    print("Attempting to log a message...")
    log_message(user_id, session_id, "assistant", "TEST MESSAGE FROM SCRIPT")
    print("✅ log_message executed successfully.")
    
    # Verify in DB
    conn = psycopg2.connect(PG_URI)
    cursor = conn.cursor()
    cursor.execute("SELECT role, content FROM chat_history WHERE user_id = %s", (user_id,))
    print("History in DB:", cursor.fetchall())
except Exception as e:
    import traceback
    print("❌ EXCEPTION OCCURRED:")
    traceback.print_exc()
