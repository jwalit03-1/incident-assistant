---
title: API backend architecture overview
doc_type: technical
system: api-backend
version: "2.3"
status: current
updated: 2026-10-12
tags: [architecture, components, request-flow]
owner: platform-team
---
# API backend architecture overview

## Components
The Orders API is a stateless HTTP service behind an API gateway. It stores data in PostgreSQL (one primary and one read replica), uses Redis for caching and rate limiting, and publishes webhook events to a message queue consumed by a delivery worker.

## Request flow
1. The gateway terminates TLS and forwards the request with an `X-Request-Id` header.
2. The service validates the bearer token, applies the rate limit, then runs the handler.
3. Writes go to the primary database. Reporting endpoints read from the replica.
4. State changes publish an event to the queue; the worker delivers it to customer webhooks.

## Observability
Every log line carries the request id. Metrics cover request rate, error rate, p95 latency, database pool usage and queue depth. Dashboards and alerts are owned by the platform team.
