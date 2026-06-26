from langchain_core.tools import tool
import random

@tool
def check_order_status(order_id: str) -> str:
    """
    Check the current delivery status of an order using the order_id.
    """
    print(f"[TOOL EXECUTION] Checking order status for: {order_id}")
    # Mocking order status logic
    statuses = [
        "In the kitchen, being prepared.",
        "Dispatched and on the way via rider.",
        "Delivered.",
        "Pending confirmation."
    ]
    # Return a deterministic mock result for testing based on the ID length
    if len(order_id) < 4:
        return f"Order {order_id} not found."
    return f"Order {order_id} status: {statuses[len(order_id) % len(statuses)]}"

@tool
def book_appointment(name: str, date: str, time: str) -> str:
    """
    Book an appointment for a user at the clinic/hospital.
    """
    print(f"[TOOL EXECUTION] Booking appointment for {name} on {date} at {time}")
    # Mocking appointment logic
    return f"Appointment successfully booked for {name} on {date} at {time}. We will send a reminder beforehand."

# List of tools to bind to the LLM
business_tools = [check_order_status, book_appointment]
