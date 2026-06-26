from langchain_core.tools import tool
import random

import asyncio
from app.integrations.sandbox import SandboxOMS, SandboxPaymentGateway

# Instantiate adapters
oms_adapter = SandboxOMS()
payment_adapter = SandboxPaymentGateway()

@tool
def check_order_status(order_id: str) -> str:
    """
    Check the current delivery status of an order using the order_id.
    """
    print(f"[TOOL EXECUTION] Checking order status for: {order_id}")
    # Use the adapter (run async function synchronously for LangChain tool)
    return asyncio.run(oms_adapter.check_order_status(order_id))

@tool
def book_appointment(name: str, phone_number: str, date: str, time: str) -> str:
    """
    Book an appointment for a user at the clinic/hospital.
    """
    from app.services.scheduler import schedule_followup
    
    print(f"[TOOL EXECUTION] Booking appointment for {name} on {date} at {time}")
    
    # Schedule a reminder 1 minute from now for testing purposes (in production: 24h prior)
    reminder_msg = f"Reminder: Hi {name}, you have an appointment on {date} at {time}. See you soon!"
    schedule_followup(phone_number, reminder_msg, delay_minutes=1)
    
    return f"Appointment successfully booked for {name} on {date} at {time}. We have scheduled a reminder."

# Global set to track which sessions (phone numbers) have been escalated to a human.
# In a real app, this would be in Redis or a Database.
human_mode_sessions = set()

@tool
def escalate_to_human(phone_number: str, reason: str) -> str:
    """
    Escalate the conversation to a human agent. Use this if the user is angry, 
    requests a human, or has a complex issue the AI cannot solve.
    """
    print(f"\n[🚨 HUMAN HANDOFF TRIGGERED 🚨] Phone: {phone_number} | Reason: {reason}\n")
    human_mode_sessions.add(phone_number)
    return "Successfully escalated. The human agent will take over shortly. Tell the user a human agent is joining."

@tool
def generate_payment_link(amount: float, method: str) -> str:
    """
    Generate a payment link for the user to checkout.
    Supported methods: 'easypaisa', 'jazzcash', 'card'.
    """
    print(f"[TOOL EXECUTION] Generating {method} payment link for Rs. {amount}")
    return asyncio.run(payment_adapter.generate_payment_link(amount, method))

@tool
def get_upsell_recommendations(current_item: str) -> str:
    """
    Get smart upselling recommendations based on what the user is currently ordering.
    """
    current_item = current_item.lower()
    if "spicy" in current_item or "burger" in current_item:
        return "Recommend adding a Mint Margarita or Loaded Fries to cool down the spice!"
    elif "pizza" in current_item:
        return "Recommend adding Garlic Bread and a 1-liter Pepsi."
    return "Recommend adding a dessert like Chocolate Lava Cake."

# List of tools to bind to the LLM
business_tools = [
    check_order_status, 
    book_appointment, 
    escalate_to_human, 
    generate_payment_link, 
    get_upsell_recommendations
]
