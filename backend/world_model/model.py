"""World Model.

A structured view of the knowledge graph that supports:
    - querying entity relationships
    - detecting contradictions
    - generating predictions / causal hypotheses
    - providing context to reasoning agents

Currently a lightweight abstraction over the Neo4j graph, designed to
evolve into a full causal model.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from backend.memory.graph_memory import GraphMemory
from backend.memory.vector_memory import VectorMemory
from backend.services.embedding_service import EmbeddingService
from backend.services.llm_service import LLMService

logger = logging.getLogger(__name__)

CONTRADICTION_SYSTEM = (
    "You are a logical consistency checker. "
    "Given two statements, determine if they contradict each other. "
    "Respond with exactly one word: YES or NO."
)

CAUSAL_SYSTEM = (
    "You are a causal reasoning assistant. "
    "Given the following entities and their relationships from a knowledge graph, "
    "propose one plausible causal link between them. "
    "Format: CAUSE: <entity> -> EFFECT: <entity> because <reason>"
)


@dataclass
class WorldState:
    """A snapshot of the world model at a point in time."""

    entities: list[dict] = field(default_factory=list)
    relationships: list[dict] = field(default_factory=list)
    contradictions: list[dict] = field(default_factory=list)


class WorldModel:
    """Structured view over the knowledge graph.

    Provides higher-level reasoning primitives for agents and the
    orchestration layer.
    """

    def __init__(
        self,
        graph: GraphMemory | None = None,
        vector: VectorMemory | None = None,
    ) -> None:
        self._graph = graph or GraphMemory()
        self._vector = vector or VectorMemory()
        self._llm = LLMService()
        self._embedder = EmbeddingService()

    async def get_state(self) -> WorldState:
        """Return a snapshot of all knowledge graph nodes."""
        nodes = await self._graph.get_all_nodes()
        return WorldState(entities=nodes)

    async def get_context(self, topic: str, top_k: int = 5) -> str:
        """Retrieve relevant context for a topic from vector memory.

        Useful for providing grounding information to reasoning agents.

        Args:
            topic: The subject to look up.
            top_k: Number of chunks to retrieve.

        Returns:
            Concatenated text of the most relevant chunks.
        """
        query_vector = await self._embedder.embed(topic)
        chunks = await self._vector.search(query_vector, top_k=top_k)
        return "\n\n".join(c.text for c in chunks)

    async def check_contradiction(
        self, statement_a: str, statement_b: str
    ) -> bool:
        """Check whether two statements contradict each other.

        Uses an LLM to perform logical consistency checking.

        Args:
            statement_a: First statement.
            statement_b: Second statement.

        Returns:
            True if the statements contradict.
        """
        prompt = f"Statement A: {statement_a}\nStatement B: {statement_b}"
        response = await self._llm.chat(prompt=prompt, system=CONTRADICTION_SYSTEM)
        return response.strip().upper().startswith("YES")

    async def propose_causal_links(self) -> list[str]:
        """Query the knowledge graph and propose causal relationships.

        Returns:
            A list of proposed causal link descriptions.
        """
        nodes = await self._graph.get_all_nodes()
        if not nodes:
            return []

        node_descriptions = "\n".join(
            f"- {n.get('label', 'unknown')} ({n.get('node_type', '')})"
            for n in nodes[:20]  # Limit to avoid huge prompts
        )

        prompt = f"Known entities and facts:\n{node_descriptions}"
        response = await self._llm.chat(prompt=prompt, system=CAUSAL_SYSTEM)
        return [line.strip() for line in response.splitlines() if line.strip()]

    async def find_related(self, topic: str, top_k: int = 5) -> list[dict]:
        """Find knowledge graph nodes related to a topic via semantic search.

        Args:
            topic: The subject to search for.
            top_k: Number of results.

        Returns:
            List of related chunk dicts.
        """
        query_vector = await self._embedder.embed(topic)
        chunks = await self._vector.search(query_vector, top_k=top_k)
        return [{"text": c.text, "source": c.source, "id": str(c.id)} for c in chunks]
