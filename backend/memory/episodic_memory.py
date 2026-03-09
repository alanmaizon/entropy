"""
Episodic Memory.

In-process log of hypothesis evaluation cycles.
Records each hypothesis and its critique so the system can learn from past attempts.
In production, this should be persisted to a database.
"""

from backend.models.hypothesis import CritiqueResult, EpisodicEntry, Hypothesis


class EpisodicMemory:
    """Append-only log of hypothesis evaluation episodes."""

    def __init__(self) -> None:
        self._log: list[EpisodicEntry] = []

    def record(self, hypothesis: Hypothesis, critique: CritiqueResult) -> EpisodicEntry:
        """Record a completed hypothesis evaluation cycle.

        Args:
            hypothesis: The evaluated hypothesis.
            critique: The critic's verdict and reasoning.

        Returns:
            The newly created :class:`~backend.models.hypothesis.EpisodicEntry`.
        """
        entry = EpisodicEntry(hypothesis=hypothesis, critique=critique)
        self._log.append(entry)
        return entry

    def get_all(self) -> list[EpisodicEntry]:
        """Return all recorded episodes in chronological order."""
        return list(self._log)

    def get_by_status(self, status: str) -> list[EpisodicEntry]:
        """Return episodes whose hypothesis matches the given status.

        Args:
            status: The :class:`~backend.models.hypothesis.HypothesisStatus` value.

        Returns:
            Filtered list of entries.
        """
        return [e for e in self._log if e.hypothesis.status.value == status]
