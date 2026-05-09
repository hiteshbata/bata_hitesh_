from typing import Optional, Tuple

class WhatsAppWebhookParser:
    @staticmethod
    def extract_message_info(payload: dict) -> Optional[Tuple[str, str]]:
        try:
            entry = payload.get("entry", [])[0]
            changes = entry.get("changes", [])[0]
            value = changes.get("value", {})
            messages = value.get("messages", [])

            if not messages:
                return None

            msg = messages[0]

            sender_phone = msg.get("from")

            if msg.get("type") == "text":
                message_body = msg.get("text", {}).get("body", "")
                return sender_phone, message_body
            else:
                return sender_phone, "[Non-text message received. Only text is supported currently.]"

        except (IndexError, KeyError):
            return None
