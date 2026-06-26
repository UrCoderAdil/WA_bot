import asyncio
import os
import sys
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

from app.services.ai import ai_assistant

async def run_tests():
    phone = "923001111111"
    
    print("\n--- Test 1: Memory (Setting name) ---")
    res1 = await ai_assistant.generate_response("Hi, my name is Adil.", phone)
    print("Bot:", res1)
    
    print("\n--- Test 2: Memory (Recalling name) ---")
    res2 = await ai_assistant.generate_response("What is my name?", phone)
    print("Bot:", res2)
    
    print("\n--- Test 3: Tools (Check Order) ---")
    res3 = await ai_assistant.generate_response("Can you check my order 1234?", phone)
    print("Bot:", res3)
    
    print("\n--- Test 4: Tools (Book Appointment) ---")
    res4 = await ai_assistant.generate_response("I want to book an appointment for tomorrow at 5pm.", phone)
    print("Bot:", res4)

if __name__ == "__main__":
    asyncio.run(run_tests())
