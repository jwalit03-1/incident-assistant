---
title: Runbook - database connection pool exhausted
doc_type: runbook
system: api-backend
version: "1.2"
status: current
updated: 2026-10-21
tags: [database, connection-pool, timeout, SRV-503]
owner: platform-team
---
# Runbook - database connection pool exhausted

## Symptoms
Requests fail with `SRV-503`. Logs show the message "QueuePool limit of size 10 overflow 5 reached, connection timed out". Latency rises before the errors start.

## Diagnose
1. Check the pool usage metric for each instance.
2. On the primary database, list sessions that are "idle in transaction" or have run for a long time.
3. Look for a recent change that opens transactions without closing them, or a slow query.

## Fix
1. End the stuck sessions on the database.
2. If the load is legitimate, raise `DB_POOL_SIZE` temporarily, up to 20, and restart the instances. Make sure the total across instances stays under the database limit.
3. Fix the root cause: close sessions in a finally block, add an index, or shorten the transaction.
