from fastapi import APIRouter, Request
from app.core.celery_app import celery_app
router = APIRouter()

@router.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    data = await request.json()
    message = data.get("message", {})
    chat_id = str(message.get("chat", {}).get("id", ""))
    text = message.get("text", "")
    celery_app.send_task("app.tasks.process_telegram_message", args=[chat_id, text])
    return {"status": "ok"}
