from app.core.celery_app import celery_app
from app.services.telegram.parser import TelegramWebhookParser
from app.services.telegram.meta import TelegramBotService
from app.services.ai.orchestrator import AIOrchestrator
from app.db.supabase import get_supabase_client
import asyncio

@celery_app.task(name="app.services.telegram.tasks.process_telegram_message")
def process_telegram_message(payload: dict):
    asyncio.run(_async_process_telegram_message(payload))

async def _async_process_telegram_message(payload: dict):
    supabase = get_supabase_client()

    parsed = TelegramWebhookParser.extract_message_info(payload)
    if not parsed:
        return

    chat_id, message_body = parsed

    farmer_identifier = f"telegram_{chat_id}"

    farmer_id = None
    response = supabase.table("farmers").select("id").eq("phone_number", farmer_identifier).execute()
    if response.data:
        farmer_id = response.data[0]["id"]
    else:
        new_farmer = {
            "phone_number": farmer_identifier,
            "name": "Telegram Farmer"
        }
        res = supabase.table("farmers").insert(new_farmer).execute()
        farmer_id = res.data[0]["id"]

    supabase.table("conversations").insert({
        "farmer_id": farmer_id,
        "message_body": message_body,
        "sender": "user"
    }).execute()

    orchestrator = AIOrchestrator()
    insight = await orchestrator.process_message(farmer_id=farmer_id, user_message=message_body)

    supabase.table("conversations").insert({
        "farmer_id": farmer_id,
        "message_body": insight.conversational_response,
        "sender": "ai",
        "ai_structured_output": insight.model_dump()
    }).execute()

    await TelegramBotService.send_message(
        chat_id=chat_id,
        text=insight.conversational_response
    )
