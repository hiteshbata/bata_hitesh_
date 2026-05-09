from fastapi import APIRouter, Request, Query, HTTPException
from app.core.config import settings
from app.services.whatsapp.tasks import process_whatsapp_message

router = APIRouter()

@router.get("/whatsapp")
def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: int = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    if hub_mode == "subscribe" and hub_verify_token == settings.META_WEBHOOK_VERIFY_TOKEN:
        return hub_challenge
    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/whatsapp")
async def receive_message(request: Request):
    payload = await request.json()
    process_whatsapp_message.delay(payload)
    return {"status": "received"}
