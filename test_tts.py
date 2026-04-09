import asyncio
from medical_ai_agent.voice import generate_sarvam_tts
import logging

logging.basicConfig(level=logging.INFO)

async def test():
    text = "Arey beta, I heard you were feeling a bit frustrated or tired. Take care, okay? It's so hot outside, please keep sipping on water or maybe some nice Nimbu Pani to stay refreshed. Now, listen carefully beta, if you notice sudden severe chest pain, a fast or irregular heartbeat, severe dizziness or fainting, new rashes or blistering skin, new tendon pain especially in your ankle, or any sudden difficulty breathing, please seek urgent medical help immediately. You were wondering about your Ciprofloxacin and Albuterol. Beta, it's good you're mindful. Combining your Albuterol with Ciprofloxacin can increase the risk of an irregular heart rhythm. Please keep an eye out for any heart palpitations, chest discomfort, or dizziness. Also, Ciprofloxacin carries a small risk of tendon problems like pain or swelling, and very rarely, severe skin reactions. It is important to continue your Ciprofloxacin exactly as prescribed for your UTI. According to AIIMS guidelines, the standard treatment protocol for urinary tract infection with Ciprofloxacin is 500 mg twice daily (BD) for 5 days. Please complete the entire course of antibiotics, even if you start feeling better, to make sure the infection is fully gone. Lekin beta, iski dose ke liye apne doctor se zaroor poochein. Always remember to discuss any concerns or new symptoms with your own doctor. They know your health best, beta."
    out = await generate_sarvam_tts(text, 'en-IN', 'test_voice.ogg')
    print(f'Finished: {out}')

asyncio.run(test())
