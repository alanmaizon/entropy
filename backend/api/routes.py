"""
API Routes.

Exposes the four core Enthropy endpoints:

  POST /ingest      – ingest a document into memory
  POST /hypothesis  – generate and evaluate a hypothesis
  GET  /knowledge   – retrieve episodic knowledge log
  GET  /graph       – retrieve knowledge graph nodes
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.api.dependencies import (
    get_critic_evaluator,
    get_episodic_memory,
    get_graph_memory,
    get_hypothesis_generator,
    get_knowledge_updater,
    get_vector_memory,
)
from backend.ingestion.chunker import SemanticChunker
from backend.ingestion.document_loader import DocumentLoader
from backend.ingestion.embedder import Embedder
from backend.memory.episodic_memory import EpisodicMemory
from backend.memory.graph_memory import GraphMemory
from backend.memory.vector_memory import VectorMemory
from backend.reasoning.critic_evaluator import CriticEvaluator
from backend.reasoning.hypothesis_generator import HypothesisGenerator
from backend.reasoning.knowledge_updater import KnowledgeUpdater

router = APIRouter()


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class IngestRequest(BaseModel):
    text: str
    source: str = ""


class IngestResponse(BaseModel):
    chunks_stored: int


class HypothesisRequest(BaseModel):
    topic: str


class HypothesisResponse(BaseModel):
    hypothesis: dict
    critique: dict


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/ingest", response_model=IngestResponse)
async def ingest(
    request: IngestRequest,
    vector_memory: VectorMemory = Depends(get_vector_memory),
) -> IngestResponse:
    """Ingest a document: chunk it, embed it, and store it in vector memory.

    Args:
        request: Contains the raw ``text`` and an optional ``source`` label.

    Returns:
        The number of chunks stored.
    """
    loader = DocumentLoader()
    chunker = SemanticChunker()
    embedder = Embedder()

    text = loader.load_text(request.text)
    if not text:
        raise HTTPException(status_code=400, detail="Empty document provided.")

    chunks = chunker.chunk(text, source=request.source)
    chunks = await embedder.embed_chunks(chunks)

    await vector_memory.ensure_collection()
    for chunk in chunks:
        await vector_memory.store(chunk)

    return IngestResponse(chunks_stored=len(chunks))


@router.post("/hypothesis", response_model=HypothesisResponse)
async def hypothesis(
    request: HypothesisRequest,
    generator: HypothesisGenerator = Depends(get_hypothesis_generator),
    evaluator: CriticEvaluator = Depends(get_critic_evaluator),
    updater: KnowledgeUpdater = Depends(get_knowledge_updater),
) -> HypothesisResponse:
    """Generate a hypothesis for the given topic and evaluate it.

    Args:
        request: Contains the ``topic`` to explore.

    Returns:
        The generated hypothesis and its critique result.
    """
    hyp = await generator.generate(request.topic)
    critique = await evaluator.evaluate(hyp)
    await updater.update(hyp, critique)
    return HypothesisResponse(
        hypothesis=hyp.model_dump(mode="json"),
        critique=critique.model_dump(mode="json"),
    )


@router.get("/knowledge")
async def knowledge(
    episodic: EpisodicMemory = Depends(get_episodic_memory),
) -> dict:
    """Return all recorded hypothesis evaluation episodes.

    Returns:
        A dict with a ``episodes`` list.
    """
    entries = episodic.get_all()
    return {"episodes": [e.model_dump(mode="json") for e in entries]}


@router.get("/graph")
async def graph(
    graph_memory: GraphMemory = Depends(get_graph_memory),
) -> dict:
    """Return all nodes currently stored in the knowledge graph.

    Returns:
        A dict with a ``nodes`` list.
    """
    nodes = await graph_memory.get_all_nodes()
    return {"nodes": nodes}
