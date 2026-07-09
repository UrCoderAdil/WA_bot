from datetime import datetime, timezone


def utcnow() -> datetime:
    """
    Return the current UTC time as a timezone-naive datetime.

    Replaces the deprecated ``datetime.utcnow()`` (removed-in-future on Python 3.12+)
    while preserving the naive-UTC semantics the models and analytics queries rely on.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
