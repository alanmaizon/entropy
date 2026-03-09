"""
Tests for the API endpoints.

Uses monkeypatching to mock external services (LLM, embeddings, Qdrant, Neo4j)
so tests run without any infrastructure.
"""

import json

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.models.knowledge import Chunk


# ---------------------------------------------------------------------------
# Fakes — lightweight stand-ins for external services
# ---------------------------------------------------------------------------


class FakeLLM:
    async def chat(self, prompt: str, system: str = "") -> str:
        if "named-entity" in system.lower():
            return json.dumps([
                {"name": "Einstein", "entity_type": "PERSON"},
                {"name": "Gravity", "entity_type": "CONCEPT"},
            ])
        if "hypothesis" in system.lower():
            return "HYPOTHESIS: Gravity affects time.\nRATIONALE: General relativity."
        if "critic" in system.lower():
            return "SCORE: 0.8\nVERDICT: accepted\nREASONING: Well supported."
        return "OK"


class FakeEmbedding:
    async def embed(self, text: str) -> list[float]:
        return [0.1] * 1536

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [[0.1] * 1536 for _ in texts]


class FakeVectorMemory:
    def __init__(self, *a, **kw):
        self._store: list[Chunk] = []

    async def ensure_collection(self, vector_size: int = 1536) -> None:
        pass

    async def store(self, chunk: Chunk) -> None:
        self._store.append(chunk)

    async def search(self, query_vector, top_k=5) -> list[Chunk]:
        if self._store:
            return self._store[:top_k]
        return [Chunk(text="Gravity curves spacetime.", source="test")]


class FakeGraphMemory:
    def __init__(self, *a, **kw):
        self._nodes = []

    async def store_entity(self, entity) -> None:
        pass

    async def store_node(self, node) -> None:
        self._nodes.append(node)

    async def store_edge(self, edge) -> None:
        pass

    async def get_all_nodes(self) -> list[dict]:
        return [{"label": n.label, "node_type": n.node_type} for n in self._nodes]

    async def close(self) -> None:
        pass


# Shared instances so all code paths (DI + inline construction) use the same fakes
_fake_vector = FakeVectorMemory()
_fake_graph = FakeGraphMemory()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _mock_services(monkeypatch):
    """Patch all external service constructors so nothing connects to real infra."""
    # Reset shared state
    _fake_vector._store.clear()
    _fake_graph._nodes.clear()

    fake_llm = FakeLLM()
    fake_embed = FakeEmbedding()

    # Patch service classes at the module level
    monkeypatch.setattr(
        "backend.services.llm_service.LLMService.__init__", lambda self: None
    )
    monkeypatch.setattr(
        "backend.services.llm_service.LLMService.chat", fake_llm.chat
    )
    monkeypatch.setattr(
        "backend.services.embedding_service.EmbeddingService.__init__",
        lambda self: None,
    )
    monkeypatch.setattr(
        "backend.services.embedding_service.EmbeddingService.embed",
        fake_embed.embed,
    )
    monkeypatch.setattr(
        "backend.services.embedding_service.EmbeddingService.embed_batch",
        fake_embed.embed_batch,
    )

    # Patch memory constructors so any code that does VectorMemory() gets the fake
    monkeypatch.setattr(
        "backend.memory.vector_memory.VectorMemory.__init__",
        FakeVectorMemory.__init__,
    )
    monkeypatch.setattr(
        "backend.memory.vector_memory.VectorMemory.ensure_collection",
        FakeVectorMemory.ensure_collection,
    )
    monkeypatch.setattr(
        "backend.memory.vector_memory.VectorMemory.store",
        FakeVectorMemory.store,
    )
    monkeypatch.setattr(
        "backend.memory.vector_memory.VectorMemory.search",
        FakeVectorMemory.search,
    )
    monkeypatch.setattr(
        "backend.memory.graph_memory.GraphMemory.__init__",
        FakeGraphMemory.__init__,
    )
    monkeypatch.setattr(
        "backend.memory.graph_memory.GraphMemory.store_entity",
        FakeGraphMemory.store_entity,
    )
    monkeypatch.setattr(
        "backend.memory.graph_memory.GraphMemory.store_node",
        FakeGraphMemory.store_node,
    )
    monkeypatch.setattr(
        "backend.memory.graph_memory.GraphMemory.store_edge",
        FakeGraphMemory.store_edge,
    )
    monkeypatch.setattr(
        "backend.memory.graph_memory.GraphMemory.get_all_nodes",
        FakeGraphMemory.get_all_nodes,
    )

    # Patch episodic memory DI to use in-memory SQLite
    from backend.memory.episodic_memory import EpisodicMemory

    mem = EpisodicMemory(db_path=":memory:")
    monkeypatch.setattr(
        "backend.api.dependencies.get_episodic_memory", lambda: mem
    )

    # Clear lru_cache on DI providers so patches take effect
    from backend.api import dependencies
    for fn_name in [
        "get_vector_memory", "get_graph_memory",
        "get_hypothesis_generator", "get_critic_evaluator",
        "get_knowledge_updater", "get_ingestion_pipeline",
    ]:
        fn = getattr(dependencies, fn_name)
        if hasattr(fn, "cache_clear"):
            fn.cache_clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestIngestEndpoint:
    def test_ingest_success(self, client):
        response = client.post(
            "/ingest",
            json={"text": "Einstein developed general relativity.", "source": "test"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["chunks_stored"] >= 1
        assert "entities_extracted" in data

    def test_ingest_empty_text_returns_400(self, client):
        response = client.post("/ingest", json={"text": "", "source": "test"})
        assert response.status_code == 400

    def test_ingest_whitespace_only_returns_400(self, client):
        response = client.post("/ingest", json={"text": "   ", "source": "test"})
        assert response.status_code == 400


class TestHypothesisEndpoint:
    def test_hypothesis_success(self, client):
        client.post(
            "/ingest",
            json={"text": "Gravity curves spacetime.", "source": "test"},
        )
        response = client.post("/hypothesis", json={"topic": "gravity"})
        assert response.status_code == 200
        data = response.json()
        assert "hypothesis" in data
        assert "critique" in data


class TestReasonEndpoint:
    def test_reason_single_cycle(self, client):
        client.post(
            "/ingest",
            json={"text": "Quantum mechanics describes particle behavior.", "source": "test"},
        )
        response = client.post(
            "/reason", json={"topic": "quantum mechanics", "cycles": 1}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1


class TestKnowledgeEndpoint:
    def test_knowledge_returns_episodes(self, client):
        response = client.get("/knowledge")
        assert response.status_code == 200
        assert "episodes" in response.json()


class TestGraphEndpoint:
    def test_graph_returns_nodes(self, client):
        response = client.get("/graph")
        assert response.status_code == 200
        assert "nodes" in response.json()


class TestHealthEndpoint:
    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
