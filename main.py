import sys
from contextlib import asynccontextmanager

# Ensure UTF-8 console output so emoji in messages/logs don't crash on Windows (cp1252).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import webhook
from app.api import admin
from app.api import dashboard
from app.core.config import settings
from app.db.database import init_db
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.services.scheduler import scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database tables and background tasks on startup."""
    await init_db()
    print("[OK] Database initialized")
    
    # Start the APScheduler
    scheduler.start()
    print("[OK] Background Scheduler started")
    
    yield
    
    # Shutdown gracefully
    scheduler.shutdown()

app = FastAPI(
    title=settings.APP_NAME,
    description="WhatsApp Business API - Enterprise SaaS Platform",
    version="3.0.0",
    lifespan=lifespan,
)

# CORS — allow Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiter
app.add_middleware(RateLimiterMiddleware, max_requests=60, window_seconds=60)

# Include Routers
app.include_router(webhook.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "WhatsApp AI Assistant API is running", "version": "3.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)

