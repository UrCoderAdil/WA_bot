from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from typing import Dict

# For MVP, we use an in-memory store so it works out of the box without a Redis server running.
# In a production environment, you would use RedisChatMessageHistory from langchain_community.
store: Dict[str, BaseChatMessageHistory] = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """
    Returns the chat history for a given session_id (which is usually the phone number).
    """
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]
