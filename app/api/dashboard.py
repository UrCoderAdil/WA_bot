from fastapi import APIRouter
from typing import Optional
from app.services.analytics import analytics_service
from app.services.crm import crm_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary")
async def get_summary(hours: int = 24):
    """Get analytics summary for the last N hours."""
    summary = await analytics_service.get_summary(hours)
    return summary

@router.get("/messages")
async def get_recent_messages(limit: int = 50):
    """Get recent message events."""
    messages = await analytics_service.get_recent_messages(limit)
    return {"messages": messages}

@router.get("/hourly")
async def get_hourly_volume(hours: int = 24):
    """Get message volume by hour for charts."""
    data = await analytics_service.get_hourly_volume(hours)
    return {"data": data}

@router.get("/customers")
async def get_customers(tenant_id: Optional[str] = None):
    """Get all customer profiles."""
    customers = await crm_service.get_all_customers(tenant_id)
    return {"customers": customers}

@router.get("/customers/count")
async def get_customer_count():
    """Get total customer count."""
    count = await crm_service.get_customer_count()
    return {"count": count}
