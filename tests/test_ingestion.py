"""
Tests for the ingestion pipeline.

Tests document loading, semantic chunking, and entity extraction parsing.
"""

import pytest

from backend.ingestion.chunker import SemanticChunker
from backend.ingestion.document_loader import DocumentLoader
from backend.ingestion.entity_extractor import EntityExtractor
from backend.models.knowledge import Chunk


class TestDocumentLoader:
    def test_load_text_strips_whitespace(self):
        loader = DocumentLoader()
        result = loader.load_text("  hello world  ")
        assert result == "hello world"

    def test_load_text_empty(self):
        loader = DocumentLoader()
        result = loader.load_text("")
        assert result == ""

    def test_load_file(self, tmp_path):
        p = tmp_path / "doc.txt"
        p.write_text("test content")
        loader = DocumentLoader()
        assert loader.load_file(p) == "test content"


class TestSemanticChunker:
    def test_chunk_short_text_produces_one_chunk(self):
        chunker = SemanticChunker(chunk_size=512, overlap=64)
        chunks = chunker.chunk("Short text.")
        assert len(chunks) == 1
        assert chunks[0].text == "Short text."

    def test_chunk_long_text_produces_multiple_chunks(self):
        chunker = SemanticChunker(chunk_size=50, overlap=10)
        text = "a" * 200
        chunks = chunker.chunk(text)
        assert len(chunks) > 1

    def test_chunk_sets_source(self):
        chunker = SemanticChunker()
        chunks = chunker.chunk("Some text.", source="doc.txt")
        assert chunks[0].source == "doc.txt"

    def test_chunk_returns_chunk_objects(self):
        chunker = SemanticChunker()
        chunks = chunker.chunk("Hello world")
        assert all(isinstance(c, Chunk) for c in chunks)

    def test_chunk_empty_text(self):
        chunker = SemanticChunker()
        chunks = chunker.chunk("")
        assert chunks == []


class TestEntityExtractorParsing:
    """Test the JSON parsing logic of EntityExtractor without an LLM."""

    def test_parse_valid_json(self, monkeypatch):
        import json

        from backend.models.knowledge import Chunk

        # We test that valid JSON is parsed correctly by calling extract
        # with a monkeypatched LLM that returns a known JSON string.
        extractor = EntityExtractor.__new__(EntityExtractor)

        chunk = Chunk(text="Alan Turing worked at GCHQ.")

        raw = json.dumps([
            {"name": "Alan Turing", "entity_type": "PERSON"},
            {"name": "GCHQ", "entity_type": "ORG"},
        ])

        import asyncio

        async def fake_chat(prompt, system=""):
            return raw

        class FakeLLM:
            chat = fake_chat

        extractor._llm = FakeLLM()

        entities = asyncio.run(extractor.extract(chunk))
        assert len(entities) == 2
        assert entities[0].name == "Alan Turing"
        assert entities[1].entity_type == "ORG"

    def test_parse_invalid_json_returns_empty(self, monkeypatch):
        import asyncio

        from backend.models.knowledge import Chunk

        extractor = EntityExtractor.__new__(EntityExtractor)
        chunk = Chunk(text="Some text")

        async def fake_chat(prompt, system=""):
            return "not valid json"

        class FakeLLM:
            chat = fake_chat

        extractor._llm = FakeLLM()
        entities = asyncio.run(extractor.extract(chunk))
        assert entities == []
