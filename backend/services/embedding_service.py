"""
Embedding Service abstraction.

Provides a pluggable interface for generating vector embeddings.
Currently backed by an OpenAI-compatible embeddings endpoint.
"""

from openai import AsyncOpenAI

from backend.config.settings import get_settings

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536


class EmbeddingService:
    """Generates dense vector embeddings for text."""

    def __init__(self) -> None:
        settings = get_settings()
        self._client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_api_base,
        )

    async def embed(self, text: str) -> list[float]:
        """Return an embedding vector for the given text.

        Args:
            text: The input string to embed.

        Returns:
            A list of floats representing the embedding vector.
        """
        response = await self._client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text,
        )
        return response.data[0].embedding

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Return embeddings for a batch of texts.

        Args:
            texts: List of input strings.

        Returns:
            List of embedding vectors in the same order.
        """
        response = await self._client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts,
        )
        return [item.embedding for item in response.data]
