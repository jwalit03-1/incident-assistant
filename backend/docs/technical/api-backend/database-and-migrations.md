---
title: Database and migrations
doc_type: technical
system: api-backend
version: "1.5"
status: current
updated: 2026-09-22
tags: [postgresql, alembic, migrations, connection-pool]
owner: platform-team
---
# Database and migrations

## Database
The service uses PostgreSQL 15 with a primary and a read replica. Reporting endpoints read from the replica and may lag the primary by a few seconds.

## Connection pool
Each service instance keeps a pool of `DB_POOL_SIZE` connections (default 10) plus `DB_MAX_OVERFLOW` extra connections (default 5). When all are in use, requests wait and then fail with `SRV-503`. Total connections across all instances must stay below the database connection limit.

## Migrations
Schema changes use Alembic. Run `alembic upgrade head` during deployment before the new version starts receiving traffic. Migrations must be backward compatible: add columns first, deploy the code, and remove old columns in a later release.
