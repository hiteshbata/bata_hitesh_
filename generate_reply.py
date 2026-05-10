import time
import logging
from typing import Dict, List, Any

from config import settings, load_active_model
from model_provider import ModelProvider
from rag import perform_rag_search
from exceptions import MissingAPIKeyError, ModelAPIError

# In-memory chat history: {user_id: {"last_active": timestamp, "messages": []}}
# Each user history stores up to 5 messages.
chat_history: Dict[str, Dict[str, Any]] = {}

HISTORY_EXPIRY_SECONDS = 2 * 60 * 60  # 2 hours

def update_and_get_history(user_id: str, new_message: str) -> str:
    """
    Updates the chat history for a user, enforcing the 5-message limit and
    clearing history if inactive for more than 2 hours. Returns formatted history string.
    """
    current_time = time.time()

    # Check if we need to clear due to inactivity
    if user_id in chat_history:
        last_active = chat_history[user_id]["last_active"]
        if current_time - last_active > HISTORY_EXPIRY_SECONDS:
            logging.info(f"Clearing chat history for user {user_id} due to inactivity.")
            chat_history[user_id] = {"last_active": current_time, "messages": []}
    else:
        chat_history[user_id] = {"last_active": current_time, "messages": []}

    history = chat_history[user_id]
    history["last_active"] = current_time
    history["messages"].append({"role": "user", "content": new_message})

    # Keep only the last 5 messages
    if len(history["messages"]) > 5:
        history["messages"] = history["messages"][-5:]

    # Format history for prompt (optional: some models natively support roles,
    # but here we format it into the system prompt context for simplicity)
    formatted = ""
    if len(history["messages"]) > 1:
        formatted = "Recent Conversation History:\n"
        for msg in history["messages"][:-1]: # exclude the current message
            formatted += f"User: {msg['content']}\n"

    return formatted

def add_assistant_reply_to_history(user_id: str, reply: str):
    """Adds the assistant's reply to the chat history."""
    if user_id in chat_history:
        history = chat_history[user_id]
        history["last_active"] = time.time()
        history["messages"].append({"role": "assistant", "content": reply})
        if len(history["messages"]) > 5:
            history["messages"] = history["messages"][-5:]

async def generate_reply(
    message: str,
    business_id: str,
    user_id: str,
    override_provider: str = None,
    override_model: str = None
) -> str:
    """
    Generates a reply by running RAG, assembling the system prompt and history,
    and calling the active model provider.
    """

    system_prompt = """You are GujBot, a helpful AI assistant for {business_name}
located in Rajkot, Gujarat, India.

VERY IMPORTANT RULES:
1. ALWAYS respond in Gujarati language using Gujarati script
2. Only answer based on the business information provided
3. Be polite and friendly like a local Gujarati shop assistant
4. If asked something not in the context, say in Gujarati:
   'આ માહિતી મારી પાસે નથી, કૃપા કરીને દુકાન પર સંપર્ક કરો.'
5. Keep answers short and clear - 2 to 4 sentences max
6. Use simple everyday Gujarati, not formal language

Business Context:
{context}

{history}

Customer Question: {question}"""

    # 1. RAG Search
    try:
        rag_results = await perform_rag_search(message, business_id)
        if not rag_results:
            context = "No specific business information found for this query."
        else:
            context = "\n\n".join(rag_results)
    except Exception as e:
        logging.error(f"RAG search error during reply generation: {e}")
        context = "Information currently unavailable due to system error."

    # 2. Setup Provider
    if override_provider and override_model:
        provider = override_provider
        model = override_model
    else:
        active = load_active_model()
        provider = active.get("provider", "google")
        model = active.get("model", "gemini-3-flash-preview")

    provider_client = ModelProvider(provider, model)

    # 3. Assemble Prompt & History
    formatted_history = update_and_get_history(user_id, message)

    prompt = system_prompt.replace("{business_name}", settings.BUSINESS_NAME)
    prompt = prompt.replace("{history}", formatted_history)

    # 4. Call Model API
    try:
        reply = await provider_client.generate_response(
            system_prompt=prompt,
            user_message=message,
            context=context
        )
        add_assistant_reply_to_history(user_id, reply)
        return reply
    except MissingAPIKeyError as e:
        # Will be caught by bot.py to notify admin
        raise e
    except Exception as e:
        logging.error(f"Error generating reply: {e}")
        raise ModelAPIError(f"Failed to generate response: {e}")
