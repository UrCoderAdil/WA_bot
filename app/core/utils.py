import asyncio
from datetime import datetime, timezone


def utcnow() -> datetime:
    """
    Return the current UTC time as a timezone-naive datetime.

    Replaces the deprecated ``datetime.utcnow()`` (removed-in-future on Python 3.12+)
    while preserving the naive-UTC semantics the models and analytics queries rely on.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


def run_coro_sync(coro):
    """
    Run an async coroutine from a synchronous context.

    LangChain tools are sync functions. The agent runs them in a worker thread that has
    no running event loop, so ``asyncio.run`` works directly; if a loop is already running
    in this thread, we offload to a fresh thread to avoid "loop already running" errors.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop is None:
        return asyncio.run(coro)

    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as pool:
        return pool.submit(asyncio.run, coro).result()
