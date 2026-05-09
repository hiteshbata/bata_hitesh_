from fastapi import APIRouter, Request
from app.services.telegram.tasks import process_telegram_message

router = APIRouter()

@router.post("/telegram")
async def receive_message(request: Request):
    payload = await request.json()
    process_telegram_message.delay(payload)
    return {"status": "received"}
