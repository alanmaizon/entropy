"""
Hypothesis Generator.

Queries vector memory for relevant context, then prompts an LLM to propose
new hypotheses about the knowledge domain.
"""

from backend.memory.vector_memory import VectorMemory
from backend.models.hypothesis import Hypothesis
from backend.services.embedding_service import EmbeddingService
from backend.services.llm_service import LLMService

GENERATION_SYSTEM = (
    "You are a scientific hypothesis generator. "
    "Given the following context from a knowledge base, propose one testable hypothesis. "
    "State the hypothesis clearly in a single sentence, then briefly explain your rationale. "
    "Format your response as:\n"
    "HYPOTHESIS: <statement>\n"
    "RATIONALE: <explanation>"
)


class HypothesisGenerator:
    """Generate hypotheses by querying memory and prompting an LLM."""

    def __init__(self) -> None:
        self._llm = LLMService()
        self._embedder = EmbeddingService()
        self._memory = VectorMemory()

    async def generate(self, topic: str) -> Hypothesis:
        """Generate a hypothesis about the given topic.

        The generator:
        1. Embeds the topic query.
        2. Retrieves the most relevant chunks from vector memory.
        3. Prompts the LLM to propose a hypothesis from that context.

        Args:
            topic: The subject or question to explore.

        Returns:
            A new :class:`~backend.models.hypothesis.Hypothesis` instance.
        """
        query_vector = await self._embedder.embed(topic)
        relevant_chunks = await self._memory.search(query_vector, top_k=5)
        context = "\n\n".join(c.text for c in relevant_chunks)

        prompt = f"Topic: {topic}\n\nContext:\n{context}"
        response = await self._llm.chat(prompt=prompt, system=GENERATION_SYSTEM)

        statement, rationale = self._parse_response(response)
        return Hypothesis(statement=statement, rationale=rationale)

    @staticmethod
    def _parse_response(response: str) -> tuple[str, str]:
        """Extract hypothesis and rationale from LLM output."""
        statement = ""
        rationale = ""
        for line in response.splitlines():
            if line.startswith("HYPOTHESIS:"):
                statement = line.removeprefix("HYPOTHESIS:").strip()
            elif line.startswith("RATIONALE:"):
                rationale = line.removeprefix("RATIONALE:").strip()
        return statement or response.strip(), rationale
