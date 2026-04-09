import os
import uvicorn
from pyngrok import ngrok
from medical_ai_agent.config import config

def start_webhook_server():
    port = config.PORT
    
    print(f"Starting ngrok tunnel to expose local port {port}...")
    try:
        # Set authtoken from config and open a ngrok tunnel to the dev server
        if config.NGROK_AUTHTOKEN:
            ngrok.set_auth_token(config.NGROK_AUTHTOKEN)
        else:
            print("⚠️ NGROK_AUTHTOKEN not found in environment. Proceeding with default (may fail).")
            
        public_url = ngrok.connect(port).public_url
        
        print("\n" + "=" * 60)
        print("🚀 Sister Nani Webhook is LIVE!")
        print(f"🔗 Public Base URL: {public_url}")
        print(f"📲 PASTE THIS IN TWILIO WEBHOOK URL: {public_url}/webhook/whatsapp")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"❌ Failed to start ngrok: {e}")
        print("Please ensure you have ngrok authenticated if required (ngrok config add-authtoken <token>)")
        print(f"⚡ Continuing without ngrok — server will be available at http://127.0.0.1:{port}")
        
    # Start the FastAPI server
    uvicorn.run("medical_ai_agent.api:app", host="0.0.0.0", port=port, reload=False)

if __name__ == "__main__":
    start_webhook_server()
