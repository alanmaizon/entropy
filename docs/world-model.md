# World Model

The world model is Enthropy's internal representation of structured knowledge. It provides a higher-level reasoning interface over the raw memory stores.

## Purpose

While vector memory stores semantic chunks and graph memory stores entities and relationships, the world model provides:

- **Context retrieval** — aggregated relevant knowledge for a topic
- **Contradiction detection** — checking logical consistency between statements
- **Causal inference** — proposing cause-effect relationships from the knowledge graph
- **Entity lookup** — finding related concepts via semantic search

## Architecture

The world model is implemented in `backend/world_model/model.py` as the `WorldModel` class.

```
WorldModel
    ├── GraphMemory (Neo4j)      — structured entity/relationship queries
    ├── VectorMemory (Qdrant)    — semantic similarity search
    ├── LLMService               — logical reasoning (contradictions, causal links)
    └── EmbeddingService         — query vectorization
```

## Capabilities

### Context retrieval

```python
context = await world_model.get_context("quantum entanglement", top_k=5)
```

Returns concatenated text from the most relevant chunks in vector memory. Used by agents to ground their reasoning in stored knowledge.

### Contradiction detection

```python
contradicts = await world_model.check_contradiction(
    "Gravity is instantaneous",
    "Gravitational effects propagate at the speed of light"
)
# → True
```

Uses an LLM to determine whether two statements are logically contradictory.

### Causal link proposal

```python
links = await world_model.propose_causal_links()
# → ["CAUSE: mass -> EFFECT: spacetime curvature because general relativity"]
```

Queries the knowledge graph for entities and uses an LLM to propose plausible causal relationships.

### Related concept search

```python
related = await world_model.find_related("dark matter", top_k=5)
```

Returns knowledge graph entries semantically related to the query.

## World state snapshot

```python
state = await world_model.get_state()
# WorldState(entities=[...], relationships=[...], contradictions=[...])
```

Returns all current knowledge graph nodes as a structured snapshot.

## Design philosophy

The world model is currently a lightweight abstraction. It delegates to existing memory and service layers rather than maintaining its own data store. This design allows it to evolve toward a full causal model without requiring architectural changes to the rest of the system.

Future directions:
- Causal graph construction from entity relationships
- Temporal reasoning (how knowledge changes over time)
- Prediction generation based on causal chains
- Conflict resolution between contradictory knowledge
