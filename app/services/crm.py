from sqlalchemy import select, func
from app.models.customer import Customer
from app.db.database import async_session
from app.core.utils import utcnow
from langchain_core.tools import tool


class CRMService:
    """Lightweight CRM to track customer profiles."""

    async def get_or_create_customer(self, phone_number: str, tenant_id: str = None) -> dict:
        """Get existing customer or create a new profile."""
        async with async_session() as session:
            result = await session.execute(
                select(Customer).where(Customer.phone_number == phone_number)
            )
            customer = result.scalar_one_or_none()

            if not customer:
                customer = Customer(
                    phone_number=phone_number,
                    tenant_id=tenant_id,
                )
                session.add(customer)
                await session.commit()
                await session.refresh(customer)

            return self._to_dict(customer)

    async def update_customer(self, phone_number: str, **kwargs) -> dict:
        """Update customer profile fields."""
        async with async_session() as session:
            result = await session.execute(
                select(Customer).where(Customer.phone_number == phone_number)
            )
            customer = result.scalar_one_or_none()
            if customer:
                for key, value in kwargs.items():
                    if hasattr(customer, key):
                        setattr(customer, key, value)
                customer.last_interaction = utcnow()
                await session.commit()
                await session.refresh(customer)
                return self._to_dict(customer)
            return None

    async def get_all_customers(self, tenant_id: str = None) -> list[dict]:
        """List all customers, optionally filtered by tenant."""
        async with async_session() as session:
            query = select(Customer).order_by(Customer.last_interaction.desc())
            if tenant_id:
                query = query.where(Customer.tenant_id == tenant_id)
            result = await session.execute(query)
            customers = result.scalars().all()
            return [self._to_dict(c) for c in customers]

    async def get_customer_count(self) -> int:
        """Get total customer count."""
        async with async_session() as session:
            result = await session.execute(select(func.count(Customer.id)))
            return result.scalar()

    def _to_dict(self, customer: Customer) -> dict:
        return {
            "id": customer.id,
            "phone_number": customer.phone_number,
            "name": customer.name,
            "preferred_language": customer.preferred_language,
            "total_orders": customer.total_orders,
            "total_appointments": customer.total_appointments,
            "tags": customer.tags,
            "notes": customer.notes,
            "tenant_id": customer.tenant_id,
            "first_interaction": str(customer.first_interaction),
            "last_interaction": str(customer.last_interaction),
        }


crm_service = CRMService()


@tool
def lookup_customer(phone_number: str) -> str:
    """
    Look up a customer's profile by their phone number.
    Returns their name, order history, preferences, and tags.
    """
    from app.core.utils import run_coro_sync
    try:
        result = run_coro_sync(crm_service.get_or_create_customer(phone_number))
        return str(result)
    except Exception as e:
        return f"Could not look up customer: {e}"


@tool
def update_customer_profile(phone_number: str, name: str = None,
                            preferred_language: str = None, notes: str = None) -> str:
    """
    Save what you learn about a customer so it's remembered in future conversations.
    Use this when the customer tells you their name, their preferred language
    (en / ur / roman_urdu), or a preference worth remembering (e.g. allergies,
    favorite order). Only pass the fields you actually learned.
    """
    from app.core.utils import run_coro_sync
    fields = {k: v for k, v in {
        "name": name,
        "preferred_language": preferred_language,
        "notes": notes,
    }.items() if v is not None}
    if not fields:
        return "Nothing to update."
    try:
        result = run_coro_sync(crm_service.update_customer(phone_number, **fields))
        if result is None:
            return "Customer not found."
        return f"Saved profile updates: {', '.join(fields.keys())}."
    except Exception as e:
        return f"Could not update customer: {e}"
