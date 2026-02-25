# Vinted Optimizer API

FastAPI backend for the Vinted Optimizer Enterprise application.

## Features

- FastAPI with async support
- PostgreSQL with SQLAlchemy 2.0
- Redis for caching and sessions
- OpenTelemetry observability
- Sentry error tracking

## Development

```bash
# Install dependencies
uv pip install -e ".[dev]"

# Run locally
uvicorn src.main:app --reload

# Run tests
pytest
```

## Deployment

Deployed on Fly.io with Docker.