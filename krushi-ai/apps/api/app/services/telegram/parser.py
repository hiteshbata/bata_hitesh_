from typing import Optional, Tuple

class TelegramWebhookParser:
    @staticmethod
    def extract_message_info(payload: dict) -> Optional[Tuple[str, str]]:
        try:
            message = payload.get("message")
            if not message:
                return None

            chat_id = str(message.get("chat", {}).get("id"))
            text = message.get("text")

            if chat_id and text:
                return chat_id, text
            else:
                return None

        except (IndexError, KeyError):
            return None
