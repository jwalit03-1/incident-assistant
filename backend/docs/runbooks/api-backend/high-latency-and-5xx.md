---
title: Runbook - high latency or 5xx errors
doc_type: runbook
system: api-backend
version: "1.4"
status: current
updated: 2026-10-18
tags: [latency, 5xx, incident, scaling]
owner: platform-team
---
# Runbook - high latency or 5xx errors

## Symptoms
The p95 latency is above 1.5 seconds or more than 2 percent of requests return 5xx errors (`SRV-500`, `SRV-503` or `PAY-502`).

## Steps
1. Open the service dashboard and note when the problem started.
2. Check whether a deployment happened at that time. If so, roll back the previous image.
3. Check database pool usage and Redis health. Saturation shows as `SRV-503`.
4. If errors are `PAY-502`, check the payment gateway status page before changing anything.
5. If load is simply high, add instances, keeping the total database connections under the limit.

## Follow-up
Record the cause and the fix in the incident ticket and add any missing alert.
