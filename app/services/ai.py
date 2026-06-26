from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage
from app.core.config import settings
from app.services.business_logic import business_tools

class AIAssistant:
    def __init__(self):
        # Initialize Gemini via Langchain
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash",
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.7,
        )
        
        self.system_prompt = """
        You are a helpful, friendly, and professional AI assistant for a Pakistani business.
        You understand English, Urdu, and Roman Urdu seamlessly.
        Your responses should be human-like, natural, and adapt to the user's language.
        If a user speaks in Roman Urdu, you can reply in Roman Urdu or English depending on context.
        Keep your responses concise and tailored for WhatsApp messaging (use emojis appropriately).
        
        You have access to tools to check order statuses and book appointments. Use them when requested!
        """
        
        # Memory saver for tracking conversation state
        self.memory = MemorySaver()
        
        # Create the agent
        self.agent = create_react_agent(
            self.llm, 
            tools=business_tools, 
            checkpointer=self.memory,
            prompt=self.system_prompt
        )

    async def generate_response(self, user_message: str, phone_number: str, media_url: str = None) -> str:
        """
        Process the user's message and generate an AI response using memory and tools.
        Supports optional media (images/audio) via URL.
        """
        try:
            # Prepare the message content
            content = []
            
            # If media is provided, fetch and encode it
            if media_url:
                from app.services.media_handler import fetch_media_as_base64
                media_data = await fetch_media_as_base64(media_url)
                if media_data:
                    content.append({
                        "type": "image_url", # Langchain uses image_url for base64 media data natively
                        "image_url": {"url": f"data:{media_data['mime_type']};base64,{media_data['data']}"}
                    })
            
            # Always append the text content
            if user_message:
                content.append({"type": "text", "text": user_message})
            elif not content:
                # Fallback if both are empty
                content.append({"type": "text", "text": "Hello"})
            
            # Invoke the agent with the user input and the phone number as the thread_id
            config = {"configurable": {"thread_id": phone_number}}
            result = await self.agent.ainvoke(
                {"messages": [("user", content)]},
                config=config
            )
            # The last message in the state is the AI's response
            return result["messages"][-1].content
        except Exception as e:
            print(f"AI Generation Error: {e}")
            return "Sorry, I am having trouble processing your request right now. Please try again later."

ai_assistant = AIAssistant()

