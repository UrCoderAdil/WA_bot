from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import asyncio

# The main scheduler instance
scheduler = AsyncIOScheduler()

async def send_scheduled_message(phone_number: str, message: str):
    """
    Task that executes at the scheduled time to send a message via WhatsApp.
    We import whatsapp_service here to avoid circular imports.
    """
    from app.services.whatsapp import whatsapp_service
    print(f"[Scheduler] Executing scheduled message to {phone_number}: {message}")
    await whatsapp_service.send_text_message(phone_number, message)

def schedule_followup(phone_number: str, message: str, delay_minutes: int = 1):
    """
    Schedules a follow-up WhatsApp message.
    """
    run_date = datetime.now() + timedelta(minutes=delay_minutes)
    scheduler.add_job(
        send_scheduled_message,
        'date',
        run_date=run_date,
        args=[phone_number, message]
    )
    print(f"[Scheduler] Scheduled message to {phone_number} at {run_date}")
