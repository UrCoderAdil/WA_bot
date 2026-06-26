from abc import ABC, abstractmethod

class PaymentGateway(ABC):
    @abstractmethod
    async def generate_payment_link(self, amount: float, method: str) -> str:
        """Generate a payment link for the user."""
        pass

class OrderManagementSystem(ABC):
    @abstractmethod
    async def check_order_status(self, order_id: str) -> str:
        """Get the current status of an order."""
        pass
