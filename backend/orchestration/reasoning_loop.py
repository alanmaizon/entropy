"""Reasoning Loop.

Implements the core cognitive cycle:
    retrieve knowledge → generate hypothesis → critique → update → store trace

This is the central orchestrator that API routes and scripts delegate to.
It can be run as a one-shot cycle or as a continual learning loop that
revisits past hypotheses.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from backend.memory.episodic_memory import EpisodicMemory
from backend.memory.graph_memory import GraphMemory
from backend.memory.vector_memory import VectorMemory
from backend.models.hypothesis import (
    CritiqueResult,
    Hypothesis,
    HypothesisStatus,
)
from backend.models.knowledge import KnowledgeNode
from backend.reasoning.critic_evaluator import CriticEvaluator
from backend.reasoning.hypothesis_generator import HypothesisGenerator
from backend.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class ReasoningLoop:
    """Orchestrates the generate–critique–update reasoning cycle.

    Each call to :meth:`run_cycle` performs one full iteration:
        1. Generate a hypothesis about the topic
        2. Evaluate it with the critic
        3. Update the knowledge graph (if accepted)
        4. Record the episode in episodic memory

    The :meth:`revisit` method supports continual learning by
    re-evaluating past hypotheses against new evidence.
    """

    def __init__(
        self,
        generator: HypothesisGenerator | None = None,
        evaluator: CriticEvaluator | None = None,
        episodic: EpisodicMemory | None = None,
        graph: GraphMemory | None = None,
        vector: VectorMemory | None = None,
    ) -> None:
        self._generator = generator or HypothesisGenerator()
        self._evaluator = evaluator or CriticEvaluator()
        self._episodic = episodic or EpisodicMemory()
        self._graph = graph or GraphMemory()
        self._vector = vector or VectorMemory()
        self._embedder = EmbeddingService()

    async def run_cycle(self, topic: str) -> dict:
        """Execute one full reasoning cycle.

        Args:
            topic: The subject to reason about.

        Returns:
            A dict with ``hypothesis``, ``critique``, and ``action`` keys.
        """
        logger.info("Reasoning cycle started for topic: %s", topic)

        # 1. Generate
        hyp = await self._generator.generate(topic)
        logger.info("Generated hypothesis: %s", hyp.statement)

        # 2. Critique
        critique = await self._evaluator.evaluate(hyp)
        logger.info(
            "Critique: score=%.2f verdict=%s", critique.score, critique.verdict.value
        )

        # 3. Update
        action = await self._apply_update(hyp, critique)
        logger.info("Action taken: %s", action)

        # 4. Record
        self._episodic.record(hyp, critique)

        return {
            "hypothesis": hyp.model_dump(mode="json"),
            "critique": critique.model_dump(mode="json"),
            "action": action,
        }

    async def revisit(self, max_items: int = 5) -> list[dict]:
        """Re-evaluate past hypotheses against current evidence.

        Retrieves recent pending/uncertain hypotheses from episodic memory,
        runs them through the critic again, and updates their status.

        Args:
            max_items: Maximum number of hypotheses to revisit.

        Returns:
            List of updated results.
        """
        logger.info("Revisiting up to %d past hypotheses", max_items)
        results = []

        candidates = (
            self._episodic.get_by_status(HypothesisStatus.UNCERTAIN.value)
            + self._episodic.get_by_status(HypothesisStatus.PENDING.value)
        )[:max_items]

        for entry in candidates:
            hyp = entry.hypothesis
            logger.info("Revisiting: %s", hyp.statement)

            new_critique = await self._evaluator.evaluate(hyp)
            action = await self._apply_update(hyp, new_critique)
            self._episodic.record(hyp, new_critique)

            results.append({
                "hypothesis": hyp.model_dump(mode="json"),
                "critique": new_critique.model_dump(mode="json"),
                "action": action,
                "revisited": True,
            })

        logger.info("Revisited %d hypotheses", len(results))
        return results

    async def _apply_update(
        self, hyp: Hypothesis, critique: CritiqueResult
    ) -> str:
        """Apply critique outcome to hypothesis and knowledge graph.

        Returns a short description of the action taken.
        """
        hyp.status = critique.verdict
        hyp.confidence = critique.score
        hyp.updated_at = datetime.now(timezone.utc)

        if critique.verdict == HypothesisStatus.ACCEPTED:
            node = KnowledgeNode(
                label=hyp.statement,
                node_type="hypothesis",
                properties={
                    "confidence": critique.score,
                    "rationale": hyp.rationale,
                },
            )
            await self._graph.store_node(node)
            return "accepted_and_stored"
        elif critique.verdict == HypothesisStatus.REJECTED:
            return "rejected"
        else:
            return "uncertain_pending_review"
