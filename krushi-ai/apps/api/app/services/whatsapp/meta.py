import httpx
from app.core.config import settings

class MetaWhatsAppService:
    @staticmethod
    async def send_message(to_phone_number: str, message_body: str) -> dict:
        url = f"https://graph.facebook.com/v19.0/{settings.META_WHATSAPP_PHONE_ID}/messages"
        headers = {
            "Authorization": f"Bearer {settings.META_WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone_number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message_body
            }
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Error sending WhatsApp message: {e}")
                return {"error": str(e)}
