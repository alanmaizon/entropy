"""
Vector Memory.

Interface to Qdrant for storing and retrieving chunk embeddings.
Provides semantic similarity search over the knowledge base.
"""

from uuid import UUID

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from backend.config.settings import get_settings
from backend.models.knowledge import Chunk


class VectorMemory:
    """Store and query chunk embeddings in Qdrant."""

    def __init__(self) -> None:
        settings = get_settings()
        self._client = AsyncQdrantClient(url=settings.qdrant_url)
        self._collection = settings.qdrant_collection

    async def ensure_collection(self, vector_size: int = 1536) -> None:
        """Create the Qdrant collection if it does not already exist.

        Args:
            vector_size: Dimensionality of the embedding vectors.
        """
        collections = await self._client.get_collections()
        names = [c.name for c in collections.collections]
        if self._collection not in names:
            await self._client.create_collection(
                collection_name=self._collection,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )

    async def store(self, chunk: Chunk) -> None:
        """Persist a chunk and its embedding to Qdrant.

        Args:
            chunk: An embedded :class:`~backend.models.knowledge.Chunk`.
        """
        point = PointStruct(
            id=str(chunk.id),
            vector=chunk.embedding,
            payload={"text": chunk.text, "source": chunk.source},
        )
        await self._client.upsert(collection_name=self._collection, points=[point])

    async def search(self, query_vector: list[float], top_k: int = 5) -> list[Chunk]:
        """Return the top-k most similar chunks to the query vector.

        Args:
            query_vector: The embedding vector to search against.
            top_k: Number of results to return.

        Returns:
            List of matching :class:`~backend.models.knowledge.Chunk` objects.
        """
        results = await self._client.search(
            collection_name=self._collection,
            query_vector=query_vector,
            limit=top_k,
        )
        chunks = []
        for hit in results:
            payload = hit.payload or {}
            chunks.append(
                Chunk(
                    id=UUID(hit.id) if isinstance(hit.id, str) else hit.id,
                    text=payload.get("text", ""),
                    source=payload.get("source", ""),
                    embedding=query_vector,
                )
            )
        return chunks
