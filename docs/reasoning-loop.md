# Reasoning Loop

The reasoning loop is the core cognitive cycle of Enthropy. It drives the system's ability to generate, evaluate, and refine knowledge over time.

## Overview

```
observe → memory → generate → critique → update → repeat
```

Each iteration of the loop:

1. **Retrieves** relevant knowledge from vector memory
2. **Generates** a hypothesis about the topic using an LLM
3. **Critiques** the hypothesis against stored evidence
4. **Updates** the knowledge graph (if accepted) and records the episode

## Architecture

The loop is implemented in `backend/orchestration/reasoning_loop.py` as the `ReasoningLoop` class.

### Components involved

| Component | Role |
|-----------|------|
| `HypothesisGenerator` | Queries vector memory, prompts LLM to propose hypotheses |
| `CriticEvaluator` | Retrieves evidence, prompts LLM to score and verdict |
| `KnowledgeUpdater` | Stores accepted hypotheses in graph, logs to episodic memory |
| `EpisodicMemory` | Persistent SQLite log of all reasoning traces |
| `GraphMemory` | Neo4j knowledge graph storing accepted knowledge |

### Single cycle flow

```
ReasoningLoop.run_cycle(topic)
    │
    ├── HypothesisGenerator.generate(topic)
    │   ├── EmbeddingService.embed(topic)
    │   ├── VectorMemory.search(vector)
    │   └── LLMService.chat(context + topic)
    │       → Hypothesis
    │
    ├── CriticEvaluator.evaluate(hypothesis)
    │   ├── EmbeddingService.embed(statement)
    │   ├── VectorMemory.search(vector)
    │   └── LLMService.chat(hypothesis + evidence)
    │       → CritiqueResult (score, verdict, reasoning)
    │
    ├── _apply_update(hypothesis, critique)
    │   ├── if ACCEPTED → GraphMemory.store_node()
    │   └── update hypothesis status & confidence
    │
    └── EpisodicMemory.record(hypothesis, critique)
        → EpisodicEntry
```

## Continual Learning

The `ReasoningLoop.revisit()` method supports continual learning by:

1. Retrieving past uncertain/pending hypotheses from episodic memory
2. Re-evaluating them against the current evidence base
3. Updating their status based on new critique scores
4. Recording the new evaluation as another episode

This allows the system to refine its knowledge as new information is ingested.

## Running standalone

The reasoning loop can be run outside the API:

```bash
python scripts/run_reasoning_cycle.py --topic "quantum gravity" --cycles 3
```

This script:
1. Ingests sample documents into memory
2. Runs multiple reasoning cycles
3. Revisits past hypotheses
4. Prints all results to stdout

## Hypothesis lifecycle

```
PENDING → (critique) → ACCEPTED | REJECTED | UNCERTAIN
                                                │
                            (revisit) ──────────┘
                                │
                        ACCEPTED | REJECTED
```

Accepted hypotheses become knowledge nodes in the graph. Rejected hypotheses remain in episodic memory as negative evidence. Uncertain hypotheses are candidates for future revisitation.
