# Enthropy – Memory System

## Overview

Enthropy uses a **hybrid memory architecture** combining three complementary
storage systems.

## Vector Memory (Qdrant)

**Purpose**: Semantic similarity search over document chunks.

**When used**:
- Retrieving context for hypothesis generation
- Finding evidence for critic evaluation

**Key operations**:
```python
await vector_memory.store(chunk)          # upsert a chunk
await vector_memory.search(vector, top_k) # similarity search
```

## Graph Memory (Neo4j)

**Purpose**: Structured relational knowledge storage.

**When used**:
- Storing accepted hypotheses as nodes
- Storing extracted entities and their relationships
- Graph traversal queries (`GET /graph`)

**Key operations**:
```python
await graph_memory.store_entity(entity)
await graph_memory.store_node(node)
await graph_memory.store_edge(edge)
await graph_memory.get_all_nodes()
```

## Episodic Memory (in-process)

**Purpose**: Append-only log of hypothesis evaluation cycles.

**When used**:
- Recording every generate → evaluate → update cycle
- Providing a replay buffer for future learning

**Key operations**:
```python
episodic.record(hypothesis, critique)
episodic.get_all()
episodic.get_by_status("accepted")
```

> **Note**: The current episodic memory is in-process only.
> For production use, migrate to a persistent store (PostgreSQL, Redis, etc.).

## Extending the Memory System

Each memory class is independently replaceable. To swap backends:
1. Create a new class with the same public async interface.
2. Update the dependency injection in `backend/api/dependencies.py`.
3. No other application code needs to change.
