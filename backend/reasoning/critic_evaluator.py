"""
Critic Evaluator.

Evaluates proposed hypotheses against evidence stored in vector memory.
Assigns a confidence score and a verdict (accepted / rejected / uncertain).
"""

from backend.memory.vector_memory import VectorMemory
from backend.models.hypothesis import CritiqueResult, Hypothesis, HypothesisStatus
from backend.services.embedding_service import EmbeddingService
from backend.services.llm_service import LLMService

CRITIQUE_SYSTEM = (
    "You are a rigorous scientific critic. "
    "Given a hypothesis and supporting context, evaluate its logical consistency "
    "and evidence support. "
    "Respond with:\n"
    "SCORE: <0.0–1.0>\n"
    "VERDICT: <accepted|rejected|uncertain>\n"
    "REASONING: <brief explanation>"
)


class CriticEvaluator:
    """Evaluate hypotheses using evidence from memory."""

    def __init__(self) -> None:
        self._llm = LLMService()
        self._embedder = EmbeddingService()
        self._memory = VectorMemory()

    async def evaluate(self, hypothesis: Hypothesis) -> CritiqueResult:
        """Evaluate a hypothesis and return a critique result.

        Args:
            hypothesis: The hypothesis to evaluate.

        Returns:
            A :class:`~backend.models.hypothesis.CritiqueResult` with score and verdict.
        """
        query_vector = await self._embedder.embed(hypothesis.statement)
        evidence_chunks = await self._memory.search(query_vector, top_k=5)
        evidence_text = "\n\n".join(c.text for c in evidence_chunks)

        prompt = (
            f"HYPOTHESIS: {hypothesis.statement}\n\n"
            f"EVIDENCE:\n{evidence_text}"
        )
        response = await self._llm.chat(prompt=prompt, system=CRITIQUE_SYSTEM)

        score, verdict, reasoning = self._parse_response(response)
        return CritiqueResult(
            hypothesis_id=hypothesis.id,
            score=score,
            verdict=verdict,
            reasoning=reasoning,
        )

    @staticmethod
    def _parse_response(response: str) -> tuple[float, HypothesisStatus, str]:
        """Extract score, verdict, and reasoning from LLM output."""
        score = 0.5
        verdict = HypothesisStatus.UNCERTAIN
        reasoning = ""

        for line in response.splitlines():
            if line.startswith("SCORE:"):
                try:
                    score = float(line.removeprefix("SCORE:").strip())
                except ValueError:
                    pass
            elif line.startswith("VERDICT:"):
                raw = line.removeprefix("VERDICT:").strip().lower()
                verdict = HypothesisStatus(raw) if raw in HypothesisStatus._value2member_map_ else HypothesisStatus.UNCERTAIN
            elif line.startswith("REASONING:"):
                reasoning = line.removeprefix("REASONING:").strip()

        return score, verdict, reasoning
