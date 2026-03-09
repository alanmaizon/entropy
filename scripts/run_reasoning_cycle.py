"""Run a complete Enthropy reasoning cycle from the command line.

Demonstrates the full cognitive loop without the API:
    1. Ingest sample documents
    2. Run reasoning cycles to generate and critique hypotheses
    3. Revisit past hypotheses with new evidence
    4. Print results

Usage:
    python scripts/run_reasoning_cycle.py
    python scripts/run_reasoning_cycle.py --topic "quantum entanglement"
    python scripts/run_reasoning_cycle.py --cycles 3
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(name)s | %(message)s")
logger = logging.getLogger("enthropy.runner")

SAMPLE_DOCUMENTS = [
    {
        "text": (
            "The theory of general relativity, developed by Albert Einstein, "
            "describes gravity as the curvature of spacetime caused by mass "
            "and energy. This replaced Newton's law of universal gravitation "
            "for high-mass, high-velocity scenarios."
        ),
        "source": "seed:relativity",
    },
    {
        "text": (
            "Quantum entanglement is a phenomenon where two particles become "
            "correlated such that the quantum state of one instantly influences "
            "the other, regardless of the distance between them. This was "
            "described by Einstein as 'spooky action at a distance'."
        ),
        "source": "seed:quantum",
    },
    {
        "text": (
            "The Standard Model of particle physics describes three of the four "
            "fundamental forces: electromagnetic, weak, and strong interactions. "
            "It does not include gravity, which is described by general relativity. "
            "Unifying these frameworks remains one of physics' greatest challenges."
        ),
        "source": "seed:standard-model",
    },
]


def _dump(label: str, data: dict) -> None:
    """Pretty-print a labelled result."""
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    print(json.dumps(data, indent=2, default=str))


async def main(topic: str, cycles: int, revisit: bool) -> None:
    from backend.ingestion.pipeline import IngestionPipeline
    from backend.memory.graph_memory import GraphMemory
    from backend.memory.vector_memory import VectorMemory
    from backend.orchestration.reasoning_loop import ReasoningLoop

    vector = VectorMemory()
    graph = GraphMemory()

    # --- Step 1: Ingest ---
    logger.info("Step 1: Ingesting %d sample documents...", len(SAMPLE_DOCUMENTS))
    pipeline = IngestionPipeline(vector_memory=vector, graph_memory=graph)
    for doc in SAMPLE_DOCUMENTS:
        result = await pipeline.run(doc["text"], source=doc["source"])
        logger.info(
            "  Ingested '%s': %d chunks, %d entities",
            doc["source"],
            result.chunks_stored,
            result.entities_extracted,
        )

    # --- Step 2: Reasoning cycles ---
    logger.info("Step 2: Running %d reasoning cycle(s) on topic '%s'...", cycles, topic)
    loop = ReasoningLoop(graph=graph, vector=vector)

    for i in range(cycles):
        logger.info("--- Cycle %d/%d ---", i + 1, cycles)
        result = await loop.run_cycle(topic)
        _dump(f"Cycle {i + 1} Result", result)

    # --- Step 3: Revisit past hypotheses ---
    if revisit:
        logger.info("Step 3: Revisiting past hypotheses...")
        revisit_results = await loop.revisit(max_items=3)
        for j, r in enumerate(revisit_results):
            _dump(f"Revisit {j + 1}", r)
        if not revisit_results:
            logger.info("  No hypotheses to revisit.")

    logger.info("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Enthropy reasoning cycle")
    parser.add_argument(
        "--topic",
        default="the relationship between gravity and quantum mechanics",
        help="Topic to reason about",
    )
    parser.add_argument(
        "--cycles", type=int, default=2, help="Number of reasoning cycles"
    )
    parser.add_argument(
        "--no-revisit",
        action="store_true",
        help="Skip the revisit step",
    )
    args = parser.parse_args()
    asyncio.run(main(args.topic, args.cycles, not args.no_revisit))
