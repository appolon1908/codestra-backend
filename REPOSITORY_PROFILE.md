# Repository Profile — `codestra-backend`

## Identity

- **Repository:** `appolon1908-hue/codestra-backend`
- **Category:** Corporate backend — recovered API
- **Visibility:** `private`
- **Default branch:** `main`
- **Authority:** Recovered Codestra Django API; authority must be reconciled with `backend2`
- **Status:** Implemented recovered Django API with Gunicorn, Celery, PostgreSQL, and Redis.

## Purpose

Backend API for the Codestra React frontend, providing server-side content, application functions, and asynchronous processing.

## Owns

- Recovered Django API source
- Celery jobs and backend persistence
- Media/static/API deployment configuration

## Does not own

- Beyvra trading backend
- Duplicate CMS authority without reconciliation
- Frontend presentation

## Key integrations

- `codestra` frontend
- PostgreSQL
- Redis
- Caddy or another TLS reverse proxy

## Current priorities

1. Reconcile overlap with `backend2` and declare one canonical backend
2. Document API surface and data ownership
3. Rotate historical secrets and image credentials
4. Add migration, backup, restore, and rollback evidence

## Governance and safety

- Target promotion model: `feature/docs/fix/security/upgrade -> development -> test -> staging -> production -> main`.
- Use pull requests and exact-head/merge-result validation; merging source never authorizes deployment.
- Never commit secrets, credentials, private keys, customer data, database dumps, or secret-bearing evidence.
- Production images and releases must be immutable; mutable `latest` tags are not release authority.
- This document does not deploy software, enable live effects, apply identity state, alter DNS/firewalls, reload Caddy, expose native ports, initialize OpenBao, or activate production.

## Account-wide catalog

See `appolon1908-hue/documentaions/REPOSITORY_CATALOG.md`.
