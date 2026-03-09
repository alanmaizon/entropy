# Enthropy – Architecture

## System Loop

```
┌──────────────┐    ┌───────────────┐    ┌──────────────────────┐
│  Data Source │───>│  Ingestion    │───>│  Memory              │
└──────────────┘    └───────────────┘    │  ├── VectorDB        │
                                         │  ├── GraphDB         │
                                         │  └── EpisodicLog     │
                                         └──────────┬───────────┘
                                                    │
                                         ┌──────────▼───────────┐
                                         │  Reasoning           │
                                         │  ├── HypothesisGen   │
                                         │  ├── CriticEval      │
                                         │  └── KnowledgeUpdate │
                                         └──────────────────────┘
                                                    │
                                         ┌──────────▼───────────┐
                                         │  Knowledge Update    │───> repeat
                                         └──────────────────────┘
```

## Module Responsibilities

| Module       | Responsibility                                              |
|--------------|-------------------------------------------------------------|
| ingestion    | Transform raw text → chunks → embeddings → entities        |
| memory       | Persist and retrieve knowledge (vector, graph, episodic)   |
| reasoning    | Generate hypotheses, evaluate them, update world model     |
| agents       | Orchestrate explorer–critic loop via message passing        |
| api          | Expose REST endpoints for external interaction              |
| services     | Plug-in abstractions for LLM and embedding providers       |
| config       | Centralised pydantic settings loaded from `.env`           |

## Data Flow

1. **Ingestion**: Raw text is loaded → split into semantic chunks →
   each chunk is embedded → entities are extracted.
2. **Memory storage**: Chunks are upserted into Qdrant (vector search).
   Entities and relationships are stored in Neo4j (graph traversal).
3. **Hypothesis generation**: The `HypothesisGenerator` embeds a topic
   query, retrieves relevant chunks, and prompts an LLM to propose a
   testable claim.
4. **Critic evaluation**: The `CriticEvaluator` retrieves evidence and
   scores the hypothesis, returning a confidence score and verdict.
5. **Knowledge update**: Accepted hypotheses are written to the graph.
   All episodes are logged to episodic memory.
6. **Repeat**: New knowledge feeds back into step 3, continuously
   refining the world model.

## Future Roadmap

- Multi-agent orchestration with message queues (e.g. Redis Streams)
- Active learning: surface low-confidence areas for human review
- Temporal reasoning: track how beliefs evolve over time
- Plugin system for alternative LLM / embedding backends
