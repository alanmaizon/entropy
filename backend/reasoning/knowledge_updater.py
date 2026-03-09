"""
Knowledge Updater.

Applies accepted hypothesis results to the knowledge graph and logs
the evaluation episode to episodic memory.
"""

from backend.memory.episodic_memory import EpisodicMemory
from backend.memory.graph_memory import GraphMemory
from backend.models.hypothesis import CritiqueResult, Hypothesis, HypothesisStatus
from backend.models.knowledge import KnowledgeNode


class KnowledgeUpdater:
    """Persist accepted hypotheses and log all evaluation episodes."""

    def __init__(self) -> None:
        self._graph = GraphMemory()
        self._episodic = EpisodicMemory()

    async def update(
        self, hypothesis: Hypothesis, critique: CritiqueResult
    ) -> None:
        """Apply the critique outcome and update knowledge stores.

        If the hypothesis is accepted, a new node is added to the knowledge graph.
        All outcomes are logged to episodic memory regardless of verdict.

        Args:
            hypothesis: The evaluated hypothesis.
            critique: The critic's verdict and score.
        """
        hypothesis.status = critique.verdict
        hypothesis.confidence = critique.score

        if critique.verdict == HypothesisStatus.ACCEPTED:
            node = KnowledgeNode(
                label=hypothesis.statement,
                node_type="hypothesis",
                properties={"confidence": critique.score, "rationale": hypothesis.rationale},
            )
            await self._graph.store_node(node)

        self._episodic.record(hypothesis, critique)
