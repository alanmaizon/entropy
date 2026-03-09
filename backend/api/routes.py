"""
API Routes.

Exposes the core Enthropy endpoints:

  POST /ingest      – ingest a document into memory
  POST /hypothesis  – generate and evaluate a hypothesis
  POST /reason      – run a full reasoning cycle on a topic
  GET  /knowledge   – retrieve episodic knowledge log
  GET  /graph       – retrieve knowledge graph nodes
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.api.dependencies import (
    get_episodic_memory,
    get_graph_memory,
    get_ingestion_pipeline,
)
from backend.ingestion.pipeline import IngestionPipeline
from backend.memory.episodic_memory import EpisodicMemory
from backend.memory.graph_memory import GraphMemory

router = APIRouter()


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class IngestRequest(BaseModel):
    text: str
    source: str = ""


class IngestResponse(BaseModel):
    chunks_stored: int
    entities_extracted: int


class HypothesisRequest(BaseModel):
    topic: str


class HypothesisResponse(BaseModel):
    hypothesis: dict
    critique: dict


class ReasonRequest(BaseModel):
    topic: str
    cycles: int = 1


class ReasonResponse(BaseModel):
    results: list[dict]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/ingest", response_model=IngestResponse)
async def ingest(
    request: IngestRequest,
    pipeline: IngestionPipeline = Depends(get_ingestion_pipeline),
) -> IngestResponse:
    """Ingest a document through the full pipeline.

    Chunks the text, extracts entities, embeds, and stores in both
    vector memory and graph memory.
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Empty document provided.")

    result = await pipeline.run(request.text, source=request.source)
    return IngestResponse(
        chunks_stored=result.chunks_stored,
        entities_extracted=result.entities_extracted,
    )


@router.post("/hypothesis", response_model=HypothesisResponse)
async def hypothesis(request: HypothesisRequest) -> HypothesisResponse:
    """Generate a hypothesis for the given topic and evaluate it.

    Delegates to the orchestration layer's ReasoningLoop.
    """
    from backend.orchestration.reasoning_loop import ReasoningLoop

    loop = ReasoningLoop()
    cycle_result = await loop.run_cycle(request.topic)
    return HypothesisResponse(
        hypothesis=cycle_result["hypothesis"],
        critique=cycle_result["critique"],
    )


@router.post("/reason", response_model=ReasonResponse)
async def reason(request: ReasonRequest) -> ReasonResponse:
    """Run one or more full reasoning cycles on a topic.

    Each cycle generates a hypothesis, critiques it, and updates knowledge.
    """
    from backend.orchestration.reasoning_loop import ReasoningLoop

    loop = ReasoningLoop()
    results = []
    for _ in range(request.cycles):
        cycle_result = await loop.run_cycle(request.topic)
        results.append(cycle_result)
    return ReasonResponse(results=results)


@router.get("/knowledge")
async def knowledge(
    episodic: EpisodicMemory = Depends(get_episodic_memory),
) -> dict:
    """Return all recorded hypothesis evaluation episodes."""
    entries = episodic.get_all()
    return {"episodes": [e.model_dump(mode="json") for e in entries]}


@router.get("/graph")
async def graph(
    graph_memory: GraphMemory = Depends(get_graph_memory),
) -> dict:
    """Return all nodes currently stored in the knowledge graph."""
    nodes = await graph_memory.get_all_nodes()
    return {"nodes": nodes}
