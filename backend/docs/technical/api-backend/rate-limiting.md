---
title: Rate limiting
doc_type: technical
system: api-backend
version: "1.4"
status: current
updated: 2026-09-30
tags: [rate-limit, 429, throttling, redis]
owner: platform-team
---
# Rate limiting

## Limits
Each client may send 600 requests per minute, with bursts of up to 100 requests. Limits are tracked per client id in Redis using a sliding window. The default can be changed with `RATE_LIMIT_PER_MINUTE`.

## Response headers
Every response includes `X-RateLimit-Limit` and `X-RateLimit-Remaining`. When the limit is exceeded the API returns HTTP 429 with error code `RATE-429` and a `Retry-After` header giving the seconds to wait.

## Client guidance
Wait for the `Retry-After` period, then retry with exponential back-off and random jitter. Spread bulk jobs over time and cache read results. To request a higher limit, contact the platform team with the client id and the expected peak rate.
