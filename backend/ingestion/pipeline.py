"""Ingestion Pipeline.

Orchestrates the full document ingestion flow:
    raw text → chunks → entities → embeddings → vector memory + graph memory

This module ties together the individual ingestion components so that
API routes and scripts can ingest documents with a single call.
"""

from dataclasses import dataclass

from backend.ingestion.chunker import SemanticChunker
from backend.ingestion.document_loader import DocumentLoader
from backend.ingestion.embedder import Embedder
from backend.ingestion.entity_extractor import EntityExtractor
from backend.memory.graph_memory import GraphMemory
from backend.memory.vector_memory import VectorMemory
from backend.models.knowledge import Chunk, Entity


@dataclass
class IngestionResult:
    """Summary of a completed ingestion run."""

    chunks_stored: int
    entities_extracted: int


class IngestionPipeline:
    """End-to-end document ingestion into vector and graph memory."""

    def __init__(
        self,
        vector_memory: VectorMemory,
        graph_memory: GraphMemory,
    ) -> None:
        self._vector = vector_memory
        self._graph = graph_memory
        self._loader = DocumentLoader()
        self._chunker = SemanticChunker()
        self._embedder = Embedder()
        self._extractor = EntityExtractor()

    async def run(self, text: str, source: str = "") -> IngestionResult:
        """Ingest a document through the full pipeline.

        Steps:
            1. Load and clean text
            2. Chunk into semantic segments
            3. Extract entities from each chunk (LLM)
            4. Embed chunks
            5. Store chunks in vector memory
            6. Store entities and relationships in graph memory

        Args:
            text: Raw document text.
            source: Optional source label.

        Returns:
            An IngestionResult with counts of stored objects.
        """
        cleaned = self._loader.load_text(text)
        if not cleaned:
            return IngestionResult(chunks_stored=0, entities_extracted=0)

        chunks = self._chunker.chunk(cleaned, source=source)
        chunks = await self._embedder.embed_chunks(chunks)

        # Extract entities from each chunk
        all_entities: list[Entity] = []
        for chunk in chunks:
            entities = await self._extractor.extract(chunk)
            all_entities.extend(entities)

        # Store in vector memory
        await self._vector.ensure_collection()
        for chunk in chunks:
            await self._vector.store(chunk)

        # Store entities and relationships in graph memory
        for entity in all_entities:
            await self._graph.store_entity(entity)

        # Link entities that co-occur within the same chunk
        await self._link_cooccurrences(chunks, all_entities)

        return IngestionResult(
            chunks_stored=len(chunks),
            entities_extracted=len(all_entities),
        )

    async def _link_cooccurrences(
        self, chunks: list[Chunk], entities: list[Entity]
    ) -> None:
        """Create RELATED_TO edges between entities from the same chunk."""
        from backend.models.knowledge import KnowledgeNode, KnowledgeEdge

        # Group entities by chunk_id
        by_chunk: dict[str, list[Entity]] = {}
        for ent in entities:
            key = str(ent.chunk_id)
            by_chunk.setdefault(key, []).append(ent)

        for chunk_entities in by_chunk.values():
            if len(chunk_entities) < 2:
                continue
            # Ensure each entity exists as a KnowledgeNode
            nodes = []
            for ent in chunk_entities:
                node = KnowledgeNode(
                    label=ent.name,
                    node_type=ent.entity_type,
                    properties={"source_chunk": str(ent.chunk_id)},
                )
                await self._graph.store_node(node)
                nodes.append(node)
            # Create pairwise edges
            for i, a in enumerate(nodes):
                for b in nodes[i + 1 :]:
                    edge = KnowledgeEdge(
                        source_id=a.id,
                        target_id=b.id,
                        relation="related_to",
                    )
                    await self._graph.store_edge(edge)
