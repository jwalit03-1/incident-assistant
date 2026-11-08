---
title: Configuration reference
doc_type: technical
system: api-backend
version: "2.0"
status: current
updated: 2026-10-14
tags: [configuration, environment-variables, settings]
owner: platform-team
---
# Configuration reference

## Environment variables
| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | none | Primary database connection |
| `REDIS_URL` | none | Cache and rate limiting |
| `JWT_ISSUER` / `JWT_AUDIENCE` | none | Expected token issuer and audience |
| `JWKS_CACHE_SECONDS` | 300 | How long signing keys are cached |
| `RATE_LIMIT_PER_MINUTE` | 600 | Per-client request limit |
| `DB_POOL_SIZE` | 10 | Connections per instance |
| `DB_MAX_OVERFLOW` | 5 | Extra connections under load |
| `REQUEST_TIMEOUT_SECONDS` | 30 | Maximum time for one request |
| `WEBHOOK_SIGNING_SECRET` | none | Key used to sign webhook payloads |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING` or `ERROR` |

## Secrets
Secrets come from the secret manager and are injected at start-up. They are never written to logs. Changing a value requires a restart of the instances.
