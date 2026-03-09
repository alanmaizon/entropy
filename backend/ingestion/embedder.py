"""
Embedder.

Attaches vector embeddings to Chunk objects using the EmbeddingService.
"""

from backend.models.knowledge import Chunk
from backend.services.embedding_service import EmbeddingService


class Embedder:
    """Enrich chunks with embedding vectors."""

    def __init__(self) -> None:
        self._service = EmbeddingService()

    async def embed_chunks(self, chunks: list[Chunk]) -> list[Chunk]:
        """Attach an embedding vector to each chunk in-place.

        Args:
            chunks: List of chunks without embeddings.

        Returns:
            The same list with the ``embedding`` field populated.
        """
        texts = [c.text for c in chunks]
        embeddings = await self._service.embed_batch(texts)
        for chunk, vector in zip(chunks, embeddings):
            chunk.embedding = vector
        return chunks
