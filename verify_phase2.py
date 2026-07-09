import asyncio
import os
import sys
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

from app.services.ai import ai_assistant
from app.services.business_logic import human_mode_sessions

async def run_tests():
    phone = "923002222222"
    
    print("\n--- Test 1: Multimodal (Image) ---")
    # A sample public image URL (a simple placeholder image)
    image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/React-icon.svg/200px-React-icon.svg.png"
    res1 = await ai_assistant.generate_response("What logo is this in the image?", phone, media_url=image_url)
    print("Bot:", res1)
    
    print("\n--- Test 2: Upselling ---")
    res2 = await ai_assistant.generate_response("I want to order a spicy pizza.", phone)
    print("Bot:", res2)
    
    print("\n--- Test 3: Payments ---")
    res3 = await ai_assistant.generate_response("I am ready to checkout. Generate an easypaisa payment link for Rs. 1500.", phone)
    print("Bot:", res3)
    
    print("\n--- Test 4: Human Handoff ---")
    res4 = await ai_assistant.generate_response("I am very angry! I want to talk to a real human right now!", phone)
    print("Bot:", res4)
    print(f"Is session in human mode? {phone in human_mode_sessions}")
    
    print("\n--- Test 5: Post-Handoff Check ---")
    # Simulating the webhook logic
    if phone in human_mode_sessions:
        print(f"[{phone}] is in HUMAN MODE. AI is ignoring the message.")
    else:
        res5 = await ai_assistant.generate_response("Hello?", phone)
        print("Bot:", res5)

if __name__ == "__main__":
    asyncio.run(run_tests())
