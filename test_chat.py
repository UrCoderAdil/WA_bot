import asyncio
import os
import sys
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

# Load env before importing app modules
load_dotenv()

from app.services.ai import ai_assistant

async def main():
    print("==================================================")
    print("🤖 WhatsApp AI Assistant - Local Terminal Testing 🤖")
    print("==================================================")
    print("Type your message below (type 'exit' to quit):")
    print()
    
    mock_phone_number = "923001234567"
    
    while True:
        user_input = input(f"[{mock_phone_number}] You: ")
        if user_input.lower() in ['exit', 'quit', 'q']:
            print("Exiting...")
            break
            
        print("AI is typing...")
        
        # Call the AI directly
        ai_response = await ai_assistant.generate_response(user_input, mock_phone_number)
        
        print(f"🤖 Bot: {ai_response}")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())
