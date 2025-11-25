# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

This is a FastAPI-based Todo API with PostgreSQL database, OpenTelemetry instrumentation, and Kubernetes deployment via ArgoCD.

### Application Structure

- **Entry Point**: [src/app.py](src/app.py) - FastAPI application with lifespan management, middleware registration, and route configuration
- **API Endpoints**: [src/api/](src/api/) - Health, info, and CRUD endpoints
- **Models**: [src/models/](src/models/) - SQLAlchemy ORM models and Pydantic schemas
- **Framework**: [src/framework/](src/framework/) - Database session management and custom middleware
- **Tests**: [tests/](tests/) - Separate unit and integration test suites

### Key Design Patterns

**Environment-Aware Configuration**: The application detects `TESTING` environment variable to disable middleware and OpenTelemetry during test execution. This is set in [tests/unit/conftest.py](tests/unit/conftest.py#L12).

**Database Initialization**:
- Production: Uses environment variables (`POSTGRES_USER`, `POSTGRES_PASSWORD`, etc.) with connection pooling
- Testing: Uses `DATABASE_URL` environment variable or in-memory SQLite
- The `init_db()` function in [src/framework/db.py](src/framework/db.py) handles both scenarios

**Middleware Architecture**: [src/framework/middleware.py](src/framework/middleware.py) provides structured logging with:
- Transaction ID tracking (added to response headers)
- Endpoint normalization (replaces numeric IDs with `{id}` placeholders)
- Request/response body logging for non-GET methods
- Integration with OpenTelemetry logging handlers

**Application Lifespan**: [src/app.py](src/app.py#L46-L87) implements retry logic for database connections at startup (5 retries with 2-second delays), but only when not in testing mode.

## Development Commands

### Running Tests

```bash
# Set PYTHONPATH for imports
export PYTHONPATH=./src

# Run all unit tests
pytest tests/unit

# Run all integration tests
pytest tests/integration

# Run with coverage report (70% minimum)
pytest tests/unit \
  --cov=src \
  --cov-report=xml:coverage.xml \
  --cov-report=html:coverage_html \
  --cov-report=term-missing \
  --cov-fail-under=70 \
  --junitxml=results.xml

# Run a single test file
pytest tests/unit/test_models.py

# Run a specific test function
pytest tests/unit/test_models.py::test_function_name
```

### Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Development (requires PostgreSQL environment variables)
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=password
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=mydb

cd src
uvicorn app:app --host 0.0.0.0 --port 5001 --reload

# Production (with OpenTelemetry)
opentelemetry-instrument \
  --logs_exporter otlp \
  --traces_exporter otlp \
  uvicorn app:app --host 0.0.0.0 --port 5001
```

### Docker

```bash
# Build image
docker build -t todo:latest .

# Run container
docker run -p 5001:5001 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_HOST=db \
  -e POSTGRES_PORT=5432 \
  -e POSTGRES_DB=mydb \
  todo:latest
```

## API Endpoints

All endpoints are prefixed with `/api/v1/todo` and documented at `/api/v1/todo/docs` (Swagger).

### Standard Endpoints
- `GET /api/v1/todo/health` - Health check
- `GET /api/v1/todo/info` - Application info

### CRUD Operations
- `GET /api/v1/todo` - List todos (pagination: `?page=1&limit=10`)
- `GET /api/v1/todo/{id}` - Get todo by ID
- `POST /api/v1/todo` - Create todo (requires `username`, `email`, optional `full_name`)
- `PUT /api/v1/todo/{id}` - Full update (all fields required)
- `PATCH /api/v1/todo/{id}` - Partial update (only provided fields)
- `DELETE /api/v1/todo/{id}` - Delete todo

### Static Files
- `/todo/test/todo.html` - Test page for manual API testing

## Database

**Model**: The Todo model ([src/models/todo.py](src/models/todo.py)) includes:
- `id` (int, primary key)
- `username` (str, unique, indexed)
- `email` (str, unique, indexed)
- `full_name` (str, optional)
- `create_date` (datetime, auto-set)
- `update_date` (datetime, auto-updated)

**Session Management**: Use the `get_db()` dependency from [src/framework/db.py](src/framework/db.py) in FastAPI routes. Sessions are automatically closed after request completion.

## Testing

Tests are automatically marked as `unit` or `integration` based on directory location via [tests/conftest.py](tests/conftest.py).

**Unit Tests**: Use in-memory SQLite with the `TESTING=true` environment variable to disable middleware and OpenTelemetry. The fixtures in [tests/unit/conftest.py](tests/unit/conftest.py) provide isolated database sessions with transaction rollback.

**Integration Tests**: Note that [tests/integration/conftest.py](tests/integration/conftest.py) has outdated imports referencing non-existent modules (`db`, `models.ChuckJoke`, `main`). This file needs updating to match the current codebase structure.

## CI/CD

The GitHub Actions workflow ([.github/workflows/cicd.yaml](.github/workflows/cicd.yaml)) implements:

1. **Change Detection**: Determines if only Helm charts changed (skips Docker build)
2. **CI Job**: Builds and pushes Docker image to Docker Hub (currently test steps are commented out)
3. **CD Job**: Updates Helm chart values and syncs ArgoCD application to Kubernetes
4. **Charts-Only CD**: Syncs ArgoCD when only chart files change

**Important**: The CI job has commented-out test execution steps. Uncomment these before relying on CI for quality gates.

## Deployment

Uses Helm charts in [charts/todo/](charts/todo/) with environment-specific values:
- [charts/todo/values-dev.yaml](charts/todo/values-dev.yaml) - Development environment
- [charts/todo/values-prod.yaml](charts/todo/values-prod.yaml) - Production environment

ArgoCD configuration: [charts/argocd/values-argo.yaml](charts/argocd/values-argo.yaml)

## Environment Variables

### Production
- `POSTGRES_USER` - Database username
- `POSTGRES_PASSWORD` - Database password
- `POSTGRES_HOST` - Database host
- `POSTGRES_PORT` - Database port (default: 5432)
- `POSTGRES_DB` - Database name
- `DB_POOL_SIZE` - Connection pool size (default: 10)
- `DB_MAX_OVERFLOW` - Max overflow connections (default: 20)
- `DB_POOL_RECYCLE` - Connection recycle time in seconds (default: 3600)

### Testing
- `TESTING` - Set to `"true"` to disable middleware and OpenTelemetry
- `DATABASE_URL` - Full database URL (e.g., `sqlite:///:memory:`)
