import asyncio
import random
from app.integrations.base import PaymentGateway, OrderManagementSystem

class SandboxPaymentGateway(PaymentGateway):
    async def generate_payment_link(self, amount: float, method: str) -> str:
        """Simulate a network call to a payment provider (e.g. JazzCash)."""
        await asyncio.sleep(0.5)  # Simulate latency
        return f"https://sandbox.pay.example.com/checkout/{random.randint(10000, 99999)}?amt={amount}&m={method}"

class SandboxOMS(OrderManagementSystem):
    async def check_order_status(self, order_id: str) -> str:
        """Simulate a network call to an ERP/POS system."""
        await asyncio.sleep(0.5)  # Simulate latency
        statuses = [
            "In the kitchen, being prepared.",
            "Dispatched and on the way via rider.",
            "Delivered.",
            "Pending confirmation."
        ]
        if len(order_id) < 4:
            return f"Order {order_id} not found."
        return f"Order {order_id} status: {statuses[len(order_id) % len(statuses)]}"
