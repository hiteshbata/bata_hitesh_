import httpx
from app.core.config import settings

class TelegramBotService:
    @staticmethod
    async def send_message(chat_id: str, text: str) -> dict:
        if not settings.TELEGRAM_BOT_TOKEN:
            return {"error": "TELEGRAM_BOT_TOKEN not configured"}

        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Error sending Telegram message: {e}")
                return {"error": str(e)}
