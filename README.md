# Enthropy

**Enthropy** is a continual-learning knowledge engine that ingests information, builds structured knowledge, generates hypotheses, critiques them, and updates a world model over time.

```
data ingestion → structured memory → hypothesis generation → critic evaluation → knowledge update → repeat
```

## Architecture Overview

```
enthropy/
├── backend/
│   ├── api/              # REST endpoints
│   ├── ingestion/        # Document → chunks → entities → embeddings
│   ├── memory/           # Hybrid memory (vector + graph + episodic/SQLite)
│   ├── orchestration/    # ReasoningLoop — core cognitive cycle
│   ├── reasoning/        # Hypothesis generator + critic evaluator
│   ├── agents/           # Explorer, Critic, Researcher, Planner + MessageBus
│   ├── world_model/      # Structured knowledge view + causal inference
│   ├── models/           # Pydantic data models
│   ├── services/         # LLM & embedding abstractions
│   └── config/           # Pydantic settings
├── frontend/             # React + Vite dashboard
├── infrastructure/       # Docker & docker-compose
├── docs/                 # Architecture & module docs
├── tests/                # pytest test suite (30 tests)
└── scripts/              # Reasoning cycle runner & seed data
```

See [docs/architecture.md](docs/architecture.md) for the full system design.

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose

### 1. Clone & configure environment
```bash
cp .env.example .env
# Edit .env with your API keys and service URLs
```

### 2. Start infrastructure
```bash
make docker-up
```

### 3. Install & run the backend
```bash
make install
make dev
```

### 4. Install & run the frontend
```bash
make frontend-install
make frontend-dev
```

The API will be available at http://localhost:8000
The frontend will be available at http://localhost:5173
API docs at http://localhost:8000/docs

## API Endpoints

| Method | Path          | Description                            |
|--------|---------------|----------------------------------------|
| POST   | /ingest       | Ingest a document (full pipeline)      |
| POST   | /hypothesis   | Generate and evaluate a hypothesis     |
| POST   | /reason       | Run multi-cycle reasoning on a topic   |
| GET    | /knowledge    | Retrieve episodic memory log           |
| GET    | /graph        | Retrieve knowledge graph nodes         |
| GET    | /health       | Service health check                   |

## Development

```bash
make test     # Run tests
make lint     # Lint code
make format   # Auto-format code
```

## Standalone Reasoning

Run the full reasoning cycle without the API:

```bash
python scripts/run_reasoning_cycle.py --topic "quantum gravity" --cycles 2
```

## Documentation

- [Architecture](docs/architecture.md)
- [Reasoning Loop](docs/reasoning-loop.md)
- [World Model](docs/world-model.md)
- [Agents](docs/agents.md)
- [Memory System](docs/memory.md)
