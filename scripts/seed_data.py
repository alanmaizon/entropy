"""
Seed script: ingest sample documents into Enthropy via the REST API.

Usage:
    python scripts/seed_data.py
"""

import asyncio

import httpx

BASE_URL = "http://localhost:8000"

SAMPLE_DOCUMENTS = [
    {
        "text": (
            "The theory of general relativity, developed by Albert Einstein, "
            "describes gravity as the curvature of spacetime caused by mass and energy. "
            "This replaced Newton's law of universal gravitation for high-mass, "
            "high-velocity scenarios."
        ),
        "source": "seed:relativity",
    },
    {
        "text": (
            "Quantum entanglement is a phenomenon where two particles become correlated "
            "such that the quantum state of one instantly influences the other, "
            "regardless of the distance between them. "
            "This was described by Einstein as 'spooky action at a distance'."
        ),
        "source": "seed:quantum",
    },
]


async def seed():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as client:
        for doc in SAMPLE_DOCUMENTS:
            response = await client.post("/ingest", json=doc)
            response.raise_for_status()
            data = response.json()
            print(f"Ingested '{doc['source']}': {data['chunks_stored']} chunk(s) stored.")


if __name__ == "__main__":
    asyncio.run(seed())
