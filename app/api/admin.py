from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.tenant_manager import tenant_manager
from app.services.knowledge_base import kb_service
from app.services.handoff import handoff_manager

router = APIRouter(prefix="/admin", tags=["Admin"])


# --- Pydantic schemas ---

class TenantCreate(BaseModel):
    name: str
    business_type: str  # restaurant, clinic, fashion
    phone_number_id: str
    system_prompt: Optional[str] = None
    tools_enabled: Optional[list] = None

class KnowledgeCreate(BaseModel):
    title: str
    content: str
    category: Optional[str] = None
    tenant_id: Optional[str] = None


# --- Tenant endpoints ---

@router.post("/tenants")
async def create_tenant(data: TenantCreate):
    """Register a new business tenant."""
    tenant = await tenant_manager.create_tenant(
        name=data.name,
        business_type=data.business_type,
        phone_number_id=data.phone_number_id,
        system_prompt=data.system_prompt,
        tools_enabled=data.tools_enabled,
    )
    return {"status": "created", "tenant": tenant}

@router.get("/tenants")
async def list_tenants():
    """List all registered tenants."""
    tenants = await tenant_manager.get_all_tenants()
    return {"tenants": tenants}

@router.get("/tenants/{tenant_id}")
async def get_tenant(tenant_id: str):
    """Get a specific tenant by ID."""
    tenant = await tenant_manager.get_tenant_by_id(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {"tenant": tenant}


# --- Knowledge Base endpoints ---

@router.post("/knowledge")
async def add_knowledge(data: KnowledgeCreate):
    """Add a knowledge base entry."""
    entry = await kb_service.add_entry(
        title=data.title,
        content=data.content,
        category=data.category,
        tenant_id=data.tenant_id,
    )
    return {"status": "created", "entry": entry}

@router.get("/knowledge")
async def list_knowledge(tenant_id: Optional[str] = None):
    """List all knowledge base entries."""
    entries = await kb_service.get_all(tenant_id)
    return {"entries": entries}

@router.delete("/knowledge/{entry_id}")
async def delete_knowledge(entry_id: str):
    """Delete a knowledge base entry."""
    deleted = await kb_service.delete_entry(entry_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"status": "deleted"}


# --- Human handoff endpoints ---

@router.get("/handoffs")
async def list_handoffs():
    """List conversations currently owned by a human agent (AI paused)."""
    return {"handoffs": handoff_manager.list_active()}


@router.post("/handoffs/{phone_number}/release")
async def release_handoff(phone_number: str):
    """Hand a conversation back to the AI so it resumes replying."""
    released = handoff_manager.release(phone_number)
    if not released:
        raise HTTPException(status_code=404, detail="No active human session for this number")
    return {"status": "released", "phone_number": phone_number}
