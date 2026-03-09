"""
Entity Extractor.

Identifies named entities and key concepts within text chunks using an LLM.
Extracted entities are stored as :class:`~backend.models.knowledge.Entity` objects.
"""

import json

from backend.models.knowledge import Chunk, Entity
from backend.services.llm_service import LLMService

EXTRACTION_SYSTEM = (
    "You are a named-entity recognition system. "
    "Extract all named entities (persons, organisations, locations, concepts) "
    "from the provided text. "
    "Return a JSON array of objects with keys 'name' and 'entity_type'. "
    "Respond ONLY with the JSON array."
)


class EntityExtractor:
    """Extract named entities from text chunks using an LLM."""

    def __init__(self) -> None:
        self._llm = LLMService()

    async def extract(self, chunk: Chunk) -> list[Entity]:
        """Extract entities from a single chunk.

        Args:
            chunk: A text chunk to analyse.

        Returns:
            List of :class:`~backend.models.knowledge.Entity` objects.
        """
        raw = await self._llm.chat(prompt=chunk.text, system=EXTRACTION_SYSTEM)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return []

        entities = []
        for item in data:
            if isinstance(item, dict) and "name" in item and "entity_type" in item:
                entities.append(
                    Entity(
                        name=item["name"],
                        entity_type=item["entity_type"],
                        chunk_id=chunk.id,
                    )
                )
        return entities
