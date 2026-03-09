"""Research Agent.

Finds supporting information and evidence for a given topic or hypothesis
by searching vector memory and the knowledge graph.
"""

from backend.agents.base_agent import AgentMessage, BaseAgent
from backend.memory.vector_memory import VectorMemory
from backend.services.embedding_service import EmbeddingService


class ResearchAgent(BaseAgent):
    """Retrieves relevant evidence from memory for a given query."""

    name = "researcher"

    def __init__(self) -> None:
        self._embedder = EmbeddingService()
        self._memory = VectorMemory()

    async def run(self, message: AgentMessage) -> AgentMessage:
        """Search memory for evidence related to the query in the message.

        Args:
            message: Must contain ``content["query"]`` as a string.

        Returns:
            A message with ``content["evidence"]`` containing a list of
            relevant text passages.
        """
        query = message.content.get("query", "")
        top_k = message.content.get("top_k", 5)

        query_vector = await self._embedder.embed(query)
        chunks = await self._memory.search(query_vector, top_k=top_k)

        evidence = [
            {"text": c.text, "source": c.source, "id": str(c.id)}
            for c in chunks
        ]

        return AgentMessage(
            sender=self.name,
            recipient=message.sender,
            content={"evidence": evidence, "query": query},
        )
