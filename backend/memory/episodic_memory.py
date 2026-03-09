"""Episodic Memory.

Persistent log of hypothesis evaluation cycles backed by SQLite.
Records each hypothesis and its critique so the system can learn from
past attempts. Data survives server restarts.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from backend.models.hypothesis import (
    CritiqueResult,
    EpisodicEntry,
    Hypothesis,
)

DEFAULT_DB_PATH = Path("data/episodic_memory.db")


class EpisodicMemory:
    """Append-only log of hypothesis evaluation episodes.

    Backed by SQLite for persistence across restarts.
    Pass ``":memory:"`` as *db_path* for a transient in-memory store (useful
    for testing).
    """

    def __init__(self, db_path: str | Path | None = None) -> None:
        path = str(db_path) if db_path else str(DEFAULT_DB_PATH)
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self) -> None:
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS episodes (
                id TEXT PRIMARY KEY,
                hypothesis_json TEXT NOT NULL,
                critique_json TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        self._conn.commit()

    def record(
        self, hypothesis: Hypothesis, critique: CritiqueResult
    ) -> EpisodicEntry:
        """Record a completed hypothesis evaluation cycle.

        Args:
            hypothesis: The evaluated hypothesis.
            critique: The critic's verdict and reasoning.

        Returns:
            The newly created EpisodicEntry.
        """
        entry = EpisodicEntry(hypothesis=hypothesis, critique=critique)
        self._conn.execute(
            "INSERT OR REPLACE INTO episodes "
            "(id, hypothesis_json, critique_json, timestamp) VALUES (?, ?, ?, ?)",
            (
                str(entry.id),
                entry.hypothesis.model_dump_json(),
                entry.critique.model_dump_json(),
                entry.timestamp.isoformat(),
            ),
        )
        self._conn.commit()
        return entry

    def get_all(self) -> list[EpisodicEntry]:
        """Return all recorded episodes in chronological order."""
        rows = self._conn.execute(
            "SELECT * FROM episodes ORDER BY timestamp"
        ).fetchall()
        return [self._row_to_entry(row) for row in rows]

    def get_by_status(self, status: str) -> list[EpisodicEntry]:
        """Return episodes whose hypothesis matches the given status.

        Args:
            status: The HypothesisStatus value string (e.g. ``"accepted"``).

        Returns:
            Filtered list of entries.
        """
        all_entries = self.get_all()
        return [e for e in all_entries if e.hypothesis.status.value == status]

    def clear(self) -> None:
        """Delete all episodes. Useful for testing."""
        self._conn.execute("DELETE FROM episodes")
        self._conn.commit()

    @staticmethod
    def _row_to_entry(row: sqlite3.Row) -> EpisodicEntry:
        """Deserialise a database row into an EpisodicEntry."""
        hyp = Hypothesis.model_validate_json(row["hypothesis_json"])
        critique = CritiqueResult.model_validate_json(row["critique_json"])
        return EpisodicEntry(
            id=row["id"],
            hypothesis=hyp,
            critique=critique,
            timestamp=row["timestamp"],
        )

    def close(self) -> None:
        """Close the database connection."""
        self._conn.close()
