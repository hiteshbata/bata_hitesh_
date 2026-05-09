import asyncio
from app.core.celery_app import celery_app
from app.services.ai.orchestrator import AIOrchestrator

@celery_app.task(name="app.tasks.process_telegram_message")
def process_telegram_message(farmer_id: str, message: str):
    orchestrator = AIOrchestrator()
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(orchestrator.process_message(farmer_id, message))
    return result.dict()
