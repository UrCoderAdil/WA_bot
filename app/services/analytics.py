from datetime import timedelta
from sqlalchemy import select, func, and_
from app.models.analytics import AnalyticsEvent
from app.db.database import async_session
from app.core.utils import utcnow


class AnalyticsService:
    """Tracks and aggregates platform analytics."""

    async def log_event(self, phone_number: str, message_type: str = "text",
                        user_message: str = None, ai_response: str = None,
                        tool_called: str = None, response_time_ms: float = None,
                        escalated: bool = False, tenant_id: str = None):
        """Log an analytics event."""
        async with async_session() as session:
            event = AnalyticsEvent(
                tenant_id=tenant_id,
                phone_number=phone_number,
                message_type=message_type,
                user_message=user_message[:1000] if user_message else None,
                ai_response=ai_response[:2000] if ai_response else None,
                tool_called=tool_called,
                response_time_ms=response_time_ms,
                escalated=escalated,
            )
            session.add(event)
            await session.commit()

    async def get_summary(self, hours: int = 24) -> dict:
        """Get analytics summary for the last N hours."""
        since = utcnow() - timedelta(hours=hours)
        async with async_session() as session:
            # Total messages
            total = await session.execute(
                select(func.count(AnalyticsEvent.id)).where(AnalyticsEvent.created_at >= since)
            )
            total_messages = total.scalar() or 0

            # Unique users
            users = await session.execute(
                select(func.count(func.distinct(AnalyticsEvent.phone_number))).where(
                    AnalyticsEvent.created_at >= since
                )
            )
            active_users = users.scalar() or 0

            # Avg response time
            avg_rt = await session.execute(
                select(func.avg(AnalyticsEvent.response_time_ms)).where(
                    and_(AnalyticsEvent.created_at >= since, AnalyticsEvent.response_time_ms.isnot(None))
                )
            )
            avg_response_time = round(avg_rt.scalar() or 0, 2)

            # Escalation count
            esc = await session.execute(
                select(func.count(AnalyticsEvent.id)).where(
                    and_(AnalyticsEvent.created_at >= since, AnalyticsEvent.escalated == True)
                )
            )
            escalations = esc.scalar() or 0

            # Tool usage breakdown
            tools = await session.execute(
                select(AnalyticsEvent.tool_called, func.count(AnalyticsEvent.id))
                .where(and_(AnalyticsEvent.created_at >= since, AnalyticsEvent.tool_called.isnot(None)))
                .group_by(AnalyticsEvent.tool_called)
            )
            tool_usage = {row[0]: row[1] for row in tools.all()}

            # Message type breakdown
            types = await session.execute(
                select(AnalyticsEvent.message_type, func.count(AnalyticsEvent.id))
                .where(AnalyticsEvent.created_at >= since)
                .group_by(AnalyticsEvent.message_type)
            )
            message_types = {row[0]: row[1] for row in types.all()}

            return {
                "period_hours": hours,
                "total_messages": total_messages,
                "active_users": active_users,
                "avg_response_time_ms": avg_response_time,
                "escalations": escalations,
                "escalation_rate": round((escalations / total_messages * 100) if total_messages > 0 else 0, 1),
                "tool_usage": tool_usage,
                "message_types": message_types,
            }

    async def get_recent_messages(self, limit: int = 50) -> list[dict]:
        """Get recent message events."""
        async with async_session() as session:
            result = await session.execute(
                select(AnalyticsEvent)
                .order_by(AnalyticsEvent.created_at.desc())
                .limit(limit)
            )
            events = result.scalars().all()
            return [
                {
                    "id": e.id,
                    "phone_number": e.phone_number,
                    "message_type": e.message_type,
                    "user_message": e.user_message,
                    "ai_response": e.ai_response,
                    "tool_called": e.tool_called,
                    "response_time_ms": e.response_time_ms,
                    "escalated": e.escalated,
                    "created_at": str(e.created_at),
                }
                for e in events
            ]

    async def get_hourly_volume(self, hours: int = 24) -> list[dict]:
        """Get message volume grouped by hour for charting."""
        since = utcnow() - timedelta(hours=hours)
        async with async_session() as session:
            # Use date_trunc for PostgreSQL, strftime for SQLite
            try:
                result = await session.execute(
                    select(
                        func.date_trunc('hour', AnalyticsEvent.created_at).label('hour'),
                        func.count(AnalyticsEvent.id).label('count')
                    )
                    .where(AnalyticsEvent.created_at >= since)
                    .group_by('hour')
                    .order_by('hour')
                )
            except Exception:
                # Fallback for SQLite
                result = await session.execute(
                    select(
                        func.strftime('%Y-%m-%d %H:00', AnalyticsEvent.created_at).label('hour'),
                        func.count(AnalyticsEvent.id).label('count')
                    )
                    .where(AnalyticsEvent.created_at >= since)
                    .group_by('hour')
                    .order_by('hour')
                )
            return [{"hour": str(row[0]), "count": row[1]} for row in result.all()]


analytics_service = AnalyticsService()
