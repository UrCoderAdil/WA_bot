from app.core.utils import utcnow


class HandoffManager:
    """
    Tracks conversations currently being handled by a human agent.

    In-memory for a single instance. The interface is intentionally small so it can
    be backed by Redis later without touching callers (escalate / release / is_active).
    """

    def __init__(self):
        # phone_number -> {"reason": str, "since": iso-timestamp}
        self._sessions: dict[str, dict] = {}

    def escalate(self, phone_number: str, reason: str = "") -> None:
        """Put a conversation into human mode (idempotent)."""
        self._sessions[phone_number] = {"reason": reason, "since": utcnow().isoformat()}

    def release(self, phone_number: str) -> bool:
        """Hand a conversation back to the AI. Returns True if it was in human mode."""
        return self._sessions.pop(phone_number, None) is not None

    def is_active(self, phone_number: str) -> bool:
        """True if the AI should stay silent because a human owns this conversation."""
        return phone_number in self._sessions

    def list_active(self) -> list[dict]:
        """All conversations currently owned by a human, most recent first."""
        items = [{"phone_number": p, **meta} for p, meta in self._sessions.items()]
        return sorted(items, key=lambda x: x["since"], reverse=True)


handoff_manager = HandoffManager()
