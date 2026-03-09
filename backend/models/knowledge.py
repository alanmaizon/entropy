"""
Knowledge data models.

Defines the structured objects that flow through the Entropy system.
"""

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Chunk(BaseModel):
    """A semantic chunk derived from a source document."""

    id: UUID = Field(default_factory=uuid4)
    text: str
    embedding: list[float] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    source: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Entity(BaseModel):
    """A named entity extracted from a chunk."""

    name: str
    entity_type: str  # e.g. PERSON, ORG, CONCEPT
    chunk_id: UUID
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeNode(BaseModel):
    """A node in the knowledge graph."""

    id: UUID = Field(default_factory=uuid4)
    label: str
    node_type: str
    properties: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeEdge(BaseModel):
    """A directed edge between two knowledge nodes."""

    source_id: UUID
    target_id: UUID
    relation: str
    weight: float = 1.0
    properties: dict[str, Any] = Field(default_factory=dict)
