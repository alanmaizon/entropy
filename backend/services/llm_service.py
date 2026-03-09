"""
LLM Service abstraction.

Provides a pluggable interface to any OpenAI-compatible language model API.
Swap the backend by changing settings without touching application logic.
"""

from openai import AsyncOpenAI

from backend.config.settings import get_settings


class LLMService:
    """Wrapper around an OpenAI-compatible chat completion API."""

    def __init__(self) -> None:
        settings = get_settings()
        self._client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_api_base,
        )
        self._model = settings.openai_model

    async def chat(self, prompt: str, system: str = "") -> str:
        """Send a chat prompt and return the response text.

        Args:
            prompt: The user message to send.
            system: Optional system-level instruction.

        Returns:
            The model's text response.
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
        )
        return response.choices[0].message.content or ""
