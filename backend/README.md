# Echo AI - Backend

Python/FastAPI backend for the Echo AI visibility intelligence platform.

## Stack

- **Framework**: FastAPI + Uvicorn
- **Database**: SQLAlchemy 2.0 (async) + PostgreSQL
- **Validation**: Pydantic v2
- **Task Queue**: Celery + Redis
- **Auth**: JWT tokens

## Structure

```
backend/
├── app/
│   ├── core/           # Config, database, security
│   ├── models/         # SQLAlchemy ORM models
│   ├── routers/        # API endpoints
│   ├── schemas/        # Pydantic request/response models
│   ├── services/       # Business logic
│   └── builders/       # LLM provider integrations
├── scripts/            # Dev utilities
└── tests/              # Test files
```

## Key Modules

| Module | Purpose |
|--------|---------|
| `routers/auth.py` | Authentication (login, register, tokens) |
| `routers/experiments.py` | Experiment CRUD and execution |
| `routers/brand.py` | Brand profile management |
| `routers/billing.py` | Stripe integration |
| `routers/admin.py` | Admin panel endpoints |
| `builders/providers.py` | OpenAI, Anthropic, Perplexity clients |

## Running Locally

```bash
# Start backend
uv run uvicorn backend.app.main:app --reload --port 8000

# Start Celery worker (for async experiments)
uv run celery -A backend.app.celery_app worker --loglevel=info

# Run migrations
uv run alembic upgrade head
```

## API Documentation

- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## Testing

```bash
uv run pytest tests/
```
