"""
Hypothesis data models.

Represents proposed hypotheses and their evaluation results.
"""

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class HypothesisStatus(str, Enum):
    """Lifecycle status of a hypothesis."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    UNCERTAIN = "uncertain"


class Hypothesis(BaseModel):
    """A proposed claim generated from memory."""

    id: UUID = Field(default_factory=uuid4)
    statement: str
    rationale: str = ""
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    status: HypothesisStatus = HypothesisStatus.PENDING
    evidence_ids: list[UUID] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CritiqueResult(BaseModel):
    """Result of evaluating a hypothesis."""

    hypothesis_id: UUID
    score: float = Field(ge=0.0, le=1.0)
    verdict: HypothesisStatus
    reasoning: str
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)


class EpisodicEntry(BaseModel):
    """A log entry capturing one hypothesis evaluation cycle."""

    id: UUID = Field(default_factory=uuid4)
    hypothesis: Hypothesis
    critique: CritiqueResult
    timestamp: datetime = Field(default_factory=datetime.utcnow)
