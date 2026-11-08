---
title: REST API conventions
doc_type: technical
system: api-backend
version: "1.8"
status: current
updated: 2026-09-18
tags: [rest, pagination, idempotency, errors, versioning]
owner: platform-team
---
# REST API conventions

## Versioning and formats
The version is part of the path, for example `/v1/orders`. Requests and responses use JSON. Timestamps are ISO 8601 in UTC, for example `2026-11-01T09:30:00Z`. Amounts are integers in the smallest currency unit.

## Pagination
List endpoints use cursor pagination. Pass `limit` (default 25, maximum 100) and the `cursor` value from the previous response's `next_cursor`. When `next_cursor` is null there are no more pages.

## Idempotency
Send an `Idempotency-Key` header on every POST that creates something. The same key with the same body returns the original result for 24 hours. The same key with a different body returns `IDEM-409`.

## Error format
Every error has the same shape:
```json
{ "error": { "code": "ORD-404", "message": "Order not found", "request_id": "req_8f2c1d" } }
```
Quote the `request_id` when contacting support.
