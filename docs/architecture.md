# Enthropy – Architecture

## System Loop

```
┌──────────────┐    ┌───────────────┐    ┌──────────────────────┐
│  Data Source │───>│  Ingestion    │───>│  Memory              │
└──────────────┘    │  Pipeline     │    │  ├── VectorDB        │
                    │  ├── Chunker  │    │  ├── GraphDB         │
                    │  ├── Entities │    │  └── EpisodicLog     │
                    │  └── Embedder │    └──────────┬───────────┘
                    └───────────────┘               │
                                         ┌──────────▼───────────┐
                                         │  Orchestration       │
                                         │  └── ReasoningLoop   │
                                         └──────────┬───────────┘
                                                    │
                              ┌──────────┬──────────┼──────────┐
                              ▼          ▼          ▼          ▼
                         ┌─────────┐ ┌────────┐ ┌──────────┐ ┌────────┐
                         │Explorer │ │Critic  │ │Researcher│ │Planner │
                         │Agent    │ │Agent   │ │Agent     │ │Agent   │
                         └────┬────┘ └───┬────┘ └────┬─────┘ └───┬────┘
                              └──────────┴───────────┴────────────┘
                                         │ MessageBus
                              ┌──────────▼───────────┐
                              │  World Model         │
                              │  └── Knowledge Graph │
                              └──────────┬───────────┘
                                         │
                              ┌──────────▼───────────┐
                              │  Knowledge Update    │───> repeat
                              └──────────────────────┘
```

## Module Responsibilities

| Module        | Responsibility                                              |
|---------------|-------------------------------------------------------------|
| ingestion     | Transform raw text → chunks → embeddings → entities         |
| memory        | Persist and retrieve knowledge (vector, graph, episodic)    |
| orchestration | Coordinate reasoning cycles via the ReasoningLoop           |
| reasoning     | Generate hypotheses, evaluate them, update world model      |
| agents        | Explorer, Critic, Researcher, Planner via message bus       |
| world_model   | Structured knowledge view, contradiction detection, causal inference |
| api           | Expose REST endpoints for external interaction               |
| services      | Plug-in abstractions for LLM and embedding providers        |
| config        | Centralised pydantic settings loaded from `.env`            |

## Data Flow

1. **Ingestion**: Raw text is loaded → split into semantic chunks →
   entities are extracted (LLM) → chunks are embedded.
2. **Memory storage**: Chunks are upserted into Qdrant (vector search).
   Entities and relationships are stored in Neo4j (graph traversal).
   Co-occurring entities are linked with RELATED_TO edges.
3. **Orchestration**: The `ReasoningLoop` coordinates the full cycle:
   generate → critique → update → record.
4. **Hypothesis generation**: The `HypothesisGenerator` embeds a topic
   query, retrieves relevant chunks, and prompts an LLM to propose a
   testable claim.
5. **Critic evaluation**: The `CriticEvaluator` retrieves evidence and
   scores the hypothesis, returning a confidence score and verdict.
6. **Knowledge update**: Accepted hypotheses are written to the graph.
   All episodes are logged to persistent episodic memory (SQLite).
7. **Continual learning**: The `ReasoningLoop.revisit()` method
   re-evaluates uncertain hypotheses against new evidence.
8. **World model**: Provides context retrieval, contradiction detection,
   and causal inference over the knowledge graph.

## Agent Architecture

Agents communicate via a `MessageBus` using structured `AgentMessage` objects:

| Agent | Role |
|-------|------|
| ExplorerAgent | Generates hypotheses from memory |
| CriticAgent | Evaluates hypotheses with evidence |
| ResearchAgent | Retrieves relevant evidence for queries |
| PlannerAgent | Plans reasoning cycles and prioritises topics |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /ingest | Ingest a document (full pipeline) |
| POST | /hypothesis | Generate and evaluate a hypothesis |
| POST | /reason | Run multi-cycle reasoning |
| GET | /knowledge | Retrieve episodic memory log |
| GET | /graph | Retrieve knowledge graph nodes |
| GET | /health | Service health check |

## Documentation

- [Reasoning Loop](reasoning-loop.md)
- [World Model](world-model.md)
- [Agents](agents.md)
- [Memory System](memory.md)

## Future Roadmap

- Multi-agent orchestration with async message queues
- Active learning: surface low-confidence areas for human review
- Temporal reasoning: track how beliefs evolve over time
- Plugin system for alternative LLM / embedding backends
- Persistent world model with causal graph
