from app.core.celery_app import celery_app
from app.services.whatsapp.parser import WhatsAppWebhookParser
from app.services.whatsapp.meta import MetaWhatsAppService
from app.services.ai.orchestrator import AIOrchestrator
from app.db.supabase import get_supabase_client
import asyncio

@celery_app.task(name="app.services.whatsapp.tasks.process_whatsapp_message")
def process_whatsapp_message(payload: dict):
    asyncio.run(_async_process_whatsapp_message(payload))

async def _async_process_whatsapp_message(payload: dict):
    supabase = get_supabase_client()

    parsed = WhatsAppWebhookParser.extract_message_info(payload)
    if not parsed:
        return

    phone_number, message_body = parsed

    farmer_id = None
    response = supabase.table("farmers").select("id").eq("phone_number", phone_number).execute()
    if response.data:
        farmer_id = response.data[0]["id"]
    else:
        new_farmer = {
            "phone_number": phone_number,
            "name": "Unknown Farmer"
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

    await MetaWhatsAppService.send_message(
        to_phone_number=phone_number,
        message_body=insight.conversational_response
    )
