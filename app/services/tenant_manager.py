from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.tenant import Tenant
from app.db.database import async_session


class TenantManager:
    """Manages multi-tenant operations."""

    async def create_tenant(self, name: str, business_type: str, phone_number_id: str,
                            system_prompt: str = None, tools_enabled: list = None) -> dict:
        """Register a new tenant (business)."""
        async with async_session() as session:
            tenant = Tenant(
                name=name,
                business_type=business_type,
                phone_number_id=phone_number_id,
                system_prompt=system_prompt,
                tools_enabled=tools_enabled or [],
            )
            session.add(tenant)
            await session.commit()
            await session.refresh(tenant)
            return self._to_dict(tenant)

    async def get_tenant_by_phone_id(self, phone_number_id: str) -> dict | None:
        """Resolve a tenant from the incoming WhatsApp Phone Number ID."""
        async with async_session() as session:
            result = await session.execute(
                select(Tenant).where(Tenant.phone_number_id == phone_number_id)
            )
            tenant = result.scalar_one_or_none()
            return self._to_dict(tenant) if tenant else None

    async def get_all_tenants(self) -> list[dict]:
        """List all registered tenants."""
        async with async_session() as session:
            result = await session.execute(select(Tenant).where(Tenant.is_active == True))
            tenants = result.scalars().all()
            return [self._to_dict(t) for t in tenants]

    async def get_tenant_by_id(self, tenant_id: str) -> dict | None:
        """Get a tenant by ID."""
        async with async_session() as session:
            result = await session.execute(
                select(Tenant).where(Tenant.id == tenant_id)
            )
            tenant = result.scalar_one_or_none()
            return self._to_dict(tenant) if tenant else None

    def _to_dict(self, tenant: Tenant) -> dict:
        return {
            "id": tenant.id,
            "name": tenant.name,
            "business_type": tenant.business_type,
            "phone_number_id": tenant.phone_number_id,
            "system_prompt": tenant.system_prompt,
            "tools_enabled": tenant.tools_enabled,
            "is_active": tenant.is_active,
            "created_at": str(tenant.created_at),
        }


tenant_manager = TenantManager()
