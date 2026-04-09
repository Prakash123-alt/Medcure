"""Quick Gemini API + DeepSeek connectivity test."""
import os, requests, asyncio, warnings
warnings.filterwarnings("ignore")
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

print(f"Google key: {GOOGLE_API_KEY[:20]}... (len={len(GOOGLE_API_KEY)})")
print(f"DeepSeek key: {DEEPSEEK_API_KEY[:20]}... (len={len(DEEPSEEK_API_KEY)})")
print()

# ── Test 1: Gemini via REST ──────────────────────────────────────────────
print("=== Gemini API Test ===")
MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-preview-05-20",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
]
gemini_ok = False
for model in MODELS:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GOOGLE_API_KEY}"
    try:
        resp = requests.post(url, json={"contents": [{"parts": [{"text": "Reply with only the word PONG"}]}]}, timeout=15)
        if resp.status_code == 200:
            d = resp.json()
            reply = d["candidates"][0]["content"]["parts"][0]["text"].strip()
            print(f"  OK  [{model}]: {reply[:80]}")
            gemini_ok = True
            break
        else:
            err = resp.json().get("error", {})
            code = err.get("code", resp.status_code)
            msg = err.get("message", "?")[:120]
            print(f"  FAIL [{model}] {code}: {msg}")
    except Exception as e:
        print(f"  ERROR [{model}]: {e}")

if not gemini_ok:
    print("  ❌ No working Gemini model found with current GOOGLE_API_KEY")

print()

# ── Test 2: Gemini via LangChain (ChatGoogleGenerativeAI) ────────────────
print("=== LangChain Gemini Test ===")
async def test_langchain_gemini():
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import HumanMessage
        # Use the working model found above
        model_name = "gemini-2.5-flash"
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0,
            google_api_key=GOOGLE_API_KEY,
        )
        r = await asyncio.wait_for(llm.ainvoke([HumanMessage(content="Reply PONG")]), timeout=20)
        print(f"  OK  [{model_name}]: {str(r.content)[:80]}")
        return True
    except asyncio.TimeoutError:
        print("  TIMEOUT — LangChain Gemini took > 20s")
    except Exception as e:
        print(f"  FAIL: {type(e).__name__}: {str(e)[:200]}")
    return False

asyncio.run(test_langchain_gemini())
print()

# ── Test 3: DeepSeek via OpenRouter ─────────────────────────────────────
print("=== DeepSeek / OpenRouter Test ===")
OPEN_ROUTER = os.getenv("OPEN_ROUTER", "")
if OPEN_ROUTER:
    try:
        headers = {
            "Authorization": f"Bearer {OPEN_ROUTER}",
            "HTTP-Referer": "https://github.com/sister-nani",
            "X-Title": "Sister Nani",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "deepseek/deepseek-chat",
            "messages": [{"role": "user", "content": "Reply with only the word PONG"}],
            "max_tokens": 10,
        }
        resp = requests.post("https://openrouter.ai/api/v1/chat/completions",
                             json=payload, headers=headers, timeout=20)
        if resp.status_code == 200:
            reply = resp.json()["choices"][0]["message"]["content"].strip()
            print(f"  OK  [openrouter/deepseek-chat]: {reply[:80]}")
        else:
            print(f"  FAIL {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        print(f"  ERROR: {e}")
else:
    print("  SKIPPED — OPEN_ROUTER not set")

print()

# ── Test 4: DeepSeek direct API ─────────────────────────────────────────
print("=== DeepSeek Direct API Test ===")
if DEEPSEEK_API_KEY:
    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": "Reply with only the word PONG"}],
            "max_tokens": 10,
        }
        resp = requests.post("https://api.deepseek.com/v1/chat/completions",
                             json=payload, headers=headers, timeout=20)
        if resp.status_code == 200:
            reply = resp.json()["choices"][0]["message"]["content"].strip()
            print(f"  OK  [deepseek-chat]: {reply[:80]}")
        else:
            print(f"  FAIL {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        print(f"  ERROR: {e}")
else:
    print("  SKIPPED — DEEPSEEK_API_KEY not set")
