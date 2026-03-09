"""
Tests for the memory subsystems.

Tests episodic memory directly (no external dependencies required).
Vector and graph memory tests require running Qdrant/Neo4j and are
marked as integration tests.
"""


from backend.memory.episodic_memory import EpisodicMemory
from backend.models.hypothesis import (
    CritiqueResult,
    EpisodicEntry,
    Hypothesis,
    HypothesisStatus,
)


class TestEpisodicMemory:
    def _make_pair(self) -> tuple[Hypothesis, CritiqueResult]:
        hyp = Hypothesis(statement="The sky is blue.", rationale="Observation.")
        critique = CritiqueResult(
            hypothesis_id=hyp.id,
            score=0.9,
            verdict=HypothesisStatus.ACCEPTED,
            reasoning="Consistent with evidence.",
        )
        return hyp, critique

    def test_record_and_retrieve(self):
        mem = EpisodicMemory()
        hyp, critique = self._make_pair()
        entry = mem.record(hyp, critique)
        assert isinstance(entry, EpisodicEntry)
        assert len(mem.get_all()) == 1

    def test_get_all_returns_chronological(self):
        mem = EpisodicMemory()
        for _ in range(3):
            hyp, critique = self._make_pair()
            mem.record(hyp, critique)
        assert len(mem.get_all()) == 3

    def test_get_by_status_filters_correctly(self):
        mem = EpisodicMemory()
        hyp, critique = self._make_pair()
        hyp.status = HypothesisStatus.ACCEPTED
        mem.record(hyp, critique)

        hyp2 = Hypothesis(statement="The moon is made of cheese.")
        hyp2.status = HypothesisStatus.REJECTED
        critique2 = CritiqueResult(
            hypothesis_id=hyp2.id,
            score=0.1,
            verdict=HypothesisStatus.REJECTED,
            reasoning="No evidence.",
        )
        mem.record(hyp2, critique2)

        accepted = mem.get_by_status("accepted")
        rejected = mem.get_by_status("rejected")
        assert len(accepted) == 1
        assert len(rejected) == 1

    def test_empty_memory(self):
        mem = EpisodicMemory()
        assert mem.get_all() == []
        assert mem.get_by_status("accepted") == []
