from contextvars import ContextVar
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage
from app.core.config import settings
from app.services.business_logic import business_tools

# Operational instructions that always apply, regardless of tenant. Tenant-specific
# persona/business info (from the DB) is appended on top of this at request time.
BASE_INSTRUCTIONS = """
You are a helpful, friendly, and professional AI assistant for a Pakistani business.
You understand English, Urdu, and Roman Urdu seamlessly.
Your responses should be human-like, natural, and adapt to the user's language.
If a user speaks in Roman Urdu, you can reply in Roman Urdu or English depending on context.
Keep your responses concise and tailored for WhatsApp messaging (use emojis appropriately).

You have access to tools. Use them when relevant:
- check_order_status: look up an order's delivery status.
- book_appointment: book a clinic/hospital appointment.
- generate_payment_link: create an EasyPaisa/JazzCash/card checkout link.
- get_upsell_recommendations: suggest complementary items.
- search_knowledge_base: look up business info (menu, products, policies, FAQs)
  BEFORE answering factual questions — never invent business details.
- lookup_customer: fetch the customer's saved profile/preferences.
- update_customer_profile: save details you learn (their name, preferred language,
  allergies, favorite order) so you remember them next time.
- escalate_to_human: hand off to a human agent.

When a customer tells you their name or a lasting preference, call update_customer_profile
so it is remembered in future conversations.

Each user message is prefixed with the customer's phone number in the form
"[customer_phone: <number>]". Always pass that exact number to tools that require
a phone_number (book_appointment, escalate_to_human). Do not ask the user for it.
""".strip()

# Per-request tenant persona. Set via a ContextVar so a single shared agent can serve
# many tenants concurrently without rebuilding it per request. ContextVars are isolated
# per asyncio task, so concurrent requests don't clobber each other.
_tenant_prompt: ContextVar[str] = ContextVar("_tenant_prompt", default=None)


class AIAssistant:
    def __init__(self):
        # Initialize Gemini via Langchain
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.7,
        )

        # Memory saver for tracking conversation state (per phone number thread_id).
        self.memory = MemorySaver()

        # Create the agent with a dynamic prompt so each request can carry its own
        # tenant persona while sharing one compiled graph.
        self.agent = create_react_agent(
            self.llm,
            tools=business_tools,
            checkpointer=self.memory,
            prompt=self._build_prompt,
        )

    @staticmethod
    def _extract_text(content) -> str:
        """
        Normalize an AI message's content to a plain string.

        Newer Gemini models return `content` as a list of blocks
        (e.g. [{"type": "text", "text": "..."}, ...]) rather than a bare string,
        so we join the text blocks; otherwise the raw list would be sent to WhatsApp.
        """
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, dict):
                    if block.get("type") == "text" and block.get("text"):
                        parts.append(block["text"])
                elif isinstance(block, str):
                    parts.append(block)
            return "\n".join(parts).strip()
        return str(content)

    @staticmethod
    def _build_prompt(state):
        """Prepend base instructions + the current tenant's persona to the conversation."""
        tenant_persona = _tenant_prompt.get()
        system_text = BASE_INSTRUCTIONS
        if tenant_persona:
            system_text = f"{BASE_INSTRUCTIONS}\n\nBusiness-specific instructions:\n{tenant_persona}"
        return [SystemMessage(content=system_text)] + state["messages"]

    async def generate_response(self, user_message: str, phone_number: str, media_url: str = None,
                                trace: dict = None, system_prompt: str = None) -> str:
        """
        Process the user's message and generate an AI response using memory and tools.

        Supports optional media (images/audio) via URL or WhatsApp media ID.
        `system_prompt` is the tenant's persona (appended to the base instructions).
        If a `trace` dict is passed, it is populated with observability metadata
        ({"tools": [...]}) so callers can log which tools the agent invoked.
        """
        # Bind the tenant persona for the duration of this request only.
        token = _tenant_prompt.set(system_prompt)
        try:
            # Prepare the message content
            content = []

            # If media is provided, fetch, encode, and attach it in the right format.
            if media_url:
                from app.services.media_handler import fetch_media_as_base64
                media_data = await fetch_media_as_base64(media_url)
                if media_data:
                    mime = media_data.get("mime_type") or ""
                    b64 = media_data["data"]
                    if mime.startswith("audio/"):
                        # Gemini can understand audio natively — no separate transcription step.
                        content.append({"type": "media", "mime_type": mime, "data": b64})
                    else:
                        content.append({
                            "type": "image_url",  # Langchain uses image_url for inline base64 image data
                            "image_url": {"url": f"data:{mime};base64,{b64}"}
                        })

            # Choose the text turn. For a media-only message, nudge the model to act on it.
            if user_message:
                text = user_message
            elif len(content) > 0:
                text = "Please respond to the attached voice note / image."
            else:
                text = "Hello"

            # Prefix the phone number so tools that need it (book_appointment,
            # escalate_to_human) receive the real number instead of a hallucinated one.
            content.append({"type": "text", "text": f"[customer_phone: {phone_number}] {text}"})

            # Invoke the agent with the user input and the phone number as the thread_id
            config = {"configurable": {"thread_id": phone_number}}
            result = await self.agent.ainvoke(
                {"messages": [("user", content)]},
                config=config
            )

            # Surface which tools the agent called (for analytics / debugging).
            if trace is not None:
                tools_used = []
                for msg in result["messages"]:
                    for call in getattr(msg, "tool_calls", None) or []:
                        name = call.get("name") if isinstance(call, dict) else getattr(call, "name", None)
                        if name:
                            tools_used.append(name)
                trace["tools"] = tools_used

            # The last message in the state is the AI's response
            return self._extract_text(result["messages"][-1].content)
        except Exception as e:
            print(f"AI Generation Error: {e}")
            return "Sorry, I am having trouble processing your request right now. Please try again later."
        finally:
            _tenant_prompt.reset(token)


ai_assistant = AIAssistant()
