# Enthropy

**Enthropy** is a continual-learning knowledge engine that ingests information, builds structured knowledge, generates hypotheses, critiques them, and updates a world model over time.

```
data ingestion → structured memory → hypothesis generation → critic evaluation → knowledge update → repeat
```

## Architecture Overview

```
enthropy/
├── backend/          # FastAPI backend
│   ├── api/          # REST endpoints
│   ├── ingestion/    # Document → structured knowledge pipeline
│   ├── memory/       # Hybrid memory (vector + graph + episodic)
│   ├── reasoning/    # Hypothesis engine
│   ├── agents/       # Explorer & Critic agents
│   ├── models/       # Pydantic data models
│   ├── services/     # LLM & embedding abstractions
│   └── config/       # Pydantic settings
├── frontend/         # React + Vite dashboard
├── infrastructure/   # Docker & docker-compose
├── docs/             # Architecture & module docs
├── tests/            # pytest test suite
└── scripts/          # Setup & utility scripts
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

| Method | Path          | Description                        |
|--------|---------------|------------------------------------|
| POST   | /ingest       | Ingest a document into memory      |
| POST   | /hypothesis   | Generate a hypothesis from memory  |
| GET    | /knowledge    | Retrieve stored knowledge          |
| GET    | /graph        | Retrieve the knowledge graph       |

## Development

```bash
make test     # Run tests
make lint     # Lint code
make format   # Auto-format code
```

## Documentation

- [Architecture](docs/architecture.md)
- [Agents](docs/agents.md)
- [Memory System](docs/memory.md)
