# Career Intelligence Platform

An AI-powered platform that analyzes a student's current skills and career
profile, compares them with job-market requirements, identifies skill gaps,
and provides a personalized path toward career readiness.

## Core Differentiator

**Evidence-based skill intelligence.** This platform doesn't match resume
keywords against job descriptions — it models skills backed by verifiable
evidence from resumes, GitHub repositories, and projects, then performs
evidence-aware gap analysis against target roles.

## Status

🚧 Phase 1 — MVP Development (Project Scaffolding)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14+ (App Router), TypeScript |
| Backend | FastAPI, Python 3.12+, SQLAlchemy 2.0 (async) |
| Database | PostgreSQL 16 |
| AI/LLM | Provider abstraction (Ollama / OpenAI / Gemini) |
| Auth | GitHub OAuth via NextAuth.js |

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- Git

### 1. Clone and configure

```bash
git clone https://github.com/balajikalidhas2007/Career_Intelligence_Platform.git
cd Career_Intelligence_Platform
cp .env.example .env
# Edit .env with your GitHub OAuth credentials
```

### 2. Start infrastructure

```bash
docker compose up -d
```

This starts PostgreSQL (port 5432) and Redis (port 6379).

### 3. Backend

```bash
cd backend
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Backend runs at http://localhost:8000. API docs at http://localhost:8000/docs.

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:3000.

### 5. Run tests

```bash
# Backend
cd backend
.\.venv\Scripts\pytest --tb=short -q

# Frontend
cd frontend
npm run lint
```

## Project Structure

```
Career_Intelligence_Platform/
├── frontend/          # Next.js application
├── backend/           # FastAPI application
│   ├── app/
│   │   ├── api/       # Route handlers
│   │   ├── models/    # SQLAlchemy ORM models
│   │   ├── schemas/   # Pydantic schemas
│   │   ├── services/  # Business logic
│   │   ├── ai/        # LLM provider abstraction
│   │   └── storage/   # File storage abstraction
│   ├── alembic/       # Database migrations
│   ├── seed/          # Curated seed data
│   └── tests/         # Test suite
├── docs/              # Architecture documentation
├── .github/workflows/ # CI/CD pipeline
└── docker-compose.yml # Local infrastructure
```

## Development Approach

This project is being developed incrementally using AI-assisted engineering,
automated testing, Git, and GitHub. See [AGENTS.md](AGENTS.md) for development
principles.

## License

Private — All rights reserved.
