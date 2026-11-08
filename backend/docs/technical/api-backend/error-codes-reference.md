---
title: Error codes reference
doc_type: technical
system: api-backend
version: "1.6"
status: current
updated: 2026-10-20
tags: [errors, codes, http-status]
owner: platform-team
---
# Error codes reference

## Client errors
| Code | HTTP | Meaning |
|---|---|---|
| `AUTH-401` | 401 | Token missing, invalid or expired |
| `AUTH-403` | 403 | Token valid but the scope is missing |
| `VAL-422` | 422 | Request body failed validation; see `details` |
| `ORD-404` | 404 | Order not found |
| `ORD-409` | 409 | Order state does not allow the action |
| `IDEM-409` | 409 | Idempotency key reused with a different body |
| `RATE-429` | 429 | Rate limit exceeded |

## Server errors
| Code | HTTP | Meaning |
|---|---|---|
| `SRV-500` | 500 | Unexpected error; report the request id |
| `SRV-503` | 503 | A dependency (database or Redis) is unavailable or saturated |
| `PAY-502` | 502 | The payment gateway returned an error or timed out |
