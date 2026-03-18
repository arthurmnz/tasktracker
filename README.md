# TaskTracker Backend

TaskTracker is a backend-only REST API for managing tasks with support for customizable recurrence rules.

Stack

- Python 3.11+
- FastAPI
- Async SQLAlchemy 2.0 + asyncpg
- PostgreSQL
- Alembic for migrations
- Celery + Redis for background jobs and scheduling (Celery Beat)
- Pydantic v2 / pydantic-settings
- JWT auth (`python-jose`) and password hashing (`passlib[bcrypt]`)

Project layout (principal)

app/
api/v1/routers/ # endpoints: auth, tasks, recurrence-rules
core/ # config, security, dependencies
db/ # SQLAlchemy base & session
models/ # ORM models (User, Task, RecurrenceRule)
schemas/ # Pydantic schemas (requests/responses)
repositories/ # DB access layer
services/ # business logic (incl. recurrence)
workers/ # Celery app & tasks
main.py # FastAPI app + lifespan + health

Quickstart (Docker)

1. Copy `.env.example` to `.env` and set `SECRET_KEY` (use a secure random value):

```sh
cp .env.example .env
# edit .env and set SECRET_KEY
```

2. Build and start services (API, Postgres, Redis, Celery worker, Celery beat):

```sh
docker-compose up --build
```

Notes:

- The API will be available at `http://localhost:8000`.
- Celery worker and Celery Beat run as separate services in `docker-compose`.

Database migrations

To run Alembic migrations from inside the `api` container:

```sh
# open a shell in the api container
docker-compose run --rm api bash
# inside container
alembic upgrade head
```

Or run Alembic from host if you have Python environment configured.

Running tests

Tests use `pytest` and `httpx.AsyncClient`. To run tests locally (host), install dependencies and run:

```sh
pip install -r requirements.txt
pytest -q
```

API overview (selected endpoints)

- `POST /api/v1/auth/register` — register new user
- `POST /api/v1/auth/login` — obtain JWT
- `GET /api/v1/tasks` — list tasks (auth required)
- `POST /api/v1/tasks` — create task (supports `is_recurring` + `recurrence_rule`)
- `POST /api/v1/tasks/{task_id}/complete` — mark done and generate next occurrence if recurring
- `POST /api/v1/tasks/{task_id}/skip` — mark skipped and generate next occurrence if recurring
- `GET /api/v1/recurrence-rules` — manage recurrence rules
- `GET /health` — health checks for DB and Redis

Recurrence behavior (summary)

- Recurrence rules are stored in `recurrence_rules` and may be of type DAILY/WEEKLY/MONTHLY/YEARLY/CUSTOM.
- `CUSTOM` uses `croniter` to compute next occurrences from a cron expression.
- When a recurring task is completed or skipped, the service will attempt to generate the next occurrence using the recurrence rule.
- A periodic Celery Beat job `check_recurring_tasks` runs hourly to ensure missed occurrences are generated.

Troubleshooting

- If `docker-compose up --build` fails during `pip install`, ensure `requirements.txt` pins packages to versions compatible with Python 3.11. If you see an error about `croniter`, update the pinned `croniter` version (already adjusted to a compatible release).
- Check logs for `api`, `postgres`, `redis`, `celery-worker`, and `celery-beat` services.

Next steps

- Configure HTTPS in front of the API for production.
- Add integration tests that spin up containers and run end-to-end scenarios.
- Add more robust migration and startup checks.
