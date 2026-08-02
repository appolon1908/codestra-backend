# Codestra backend

Recovered Django API for the Codestra frontend. This repository is independent
from the trading platform backend and the Codestra React frontend.

## Run with Docker

```bash
cp .env.example .env
# Replace every placeholder in .env before deployment.
docker compose up --build -d
docker compose ps
```

The API listens on `127.0.0.1:9000` by default. Put a TLS reverse proxy in
front of it for production use.

The stack contains separate containers for Gunicorn, Celery worker, Celery
beat, PostgreSQL, and Redis. PostgreSQL, media, static files, and Redis data use
named volumes.

## Verification

```bash
docker compose config --quiet
docker build -t codestra-backend:local .
docker compose up -d db redis web
curl --fail http://127.0.0.1:9000/
```

## Security

- Never commit `.env`, database files, or production uploads.
- Use unique production values for `SECRET_KEY` and `POSTGRES_PASS`.
- Restrict `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, and
  `CSRF_TRUSTED_ORIGINS` to deployed domains.
- Rotate all secrets that were present in historical Docker images.
