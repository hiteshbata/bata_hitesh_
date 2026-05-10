import json
import logging
import httpx
import google.generativeai as genai

from config import settings
from exceptions import MissingAPIKeyError, ModelAPIError

class ModelProvider:

    def __init__(self, provider: str, model: str):
        self.provider = provider
        self.model = model

    async def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        context: str,
        max_tokens: int = 500
    ) -> str:

        logging.info(f"Generating response with {self.provider}:{self.model}")

        if self.provider == "anthropic":
            return await self._call_anthropic(system_prompt, user_message, context, max_tokens)
        elif self.provider == "openai":
            return await self._call_openai(system_prompt, user_message, context, max_tokens)
        elif self.provider == "google":
            return await self._call_google(system_prompt, user_message, context, max_tokens)
        elif self.provider == "openrouter":
            return await self._call_openrouter(system_prompt, user_message, context, max_tokens)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    async def _call_anthropic(self, system_prompt: str, user_message: str, context: str, max_tokens: int) -> str:
        if not settings.ANTHROPIC_API_KEY:
            raise MissingAPIKeyError("ANTHROPIC_API_KEY not found in .env")

        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": settings.ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        payload = {
            "model": self.model,
            "system": system_prompt.replace("{context}", context).replace("{question}", user_message),
            "messages": [
                {"role": "user", "content": user_message}
            ],
            "max_tokens": max_tokens
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                return data["content"][0]["text"]
        except Exception as e:
            raise ModelAPIError(f"Anthropic API Error: {str(e)}")

    async def _call_openai(self, system_prompt: str, user_message: str, context: str, max_tokens: int) -> str:
        # OpenAI expects an API key. For generic completion, we might reuse the embeddings key if not specifically set for completion.
        if not settings.OPENAI_API_KEY:
            raise MissingAPIKeyError("OPENAI_API_KEY not found in .env")

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        system = system_prompt.replace("{context}", context).replace("{question}", user_message)

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": max_tokens
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            raise ModelAPIError(f"OpenAI API Error: {str(e)}")

    async def _call_google(self, system_prompt: str, user_message: str, context: str, max_tokens: int) -> str:
        if not settings.GOOGLE_API_KEY:
            raise MissingAPIKeyError("GOOGLE_API_KEY not found in .env")

        genai.configure(api_key=settings.GOOGLE_API_KEY)

        system = system_prompt.replace("{context}", context).replace("{question}", user_message)

        try:
            model = genai.GenerativeModel(
                model_name=self.model,
                system_instruction=system
            )
            response = await model.generate_content_async(
                user_message,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=max_tokens,
                )
            )
            return response.text
        except Exception as e:
            raise ModelAPIError(f"Google API Error: {str(e)}")

    async def _call_openrouter(self, system_prompt: str, user_message: str, context: str, max_tokens: int) -> str:
        if not settings.OPENROUTER_API_KEY:
            raise MissingAPIKeyError("OPENROUTER_API_KEY not found in .env")

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://gujbot.app",
            "Content-Type": "application/json"
        }

        system = system_prompt.replace("{context}", context).replace("{question}", user_message)

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": max_tokens
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            raise ModelAPIError(f"OpenRouter API Error: {str(e)}")
