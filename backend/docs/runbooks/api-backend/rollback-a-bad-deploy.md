---
title: Runbook - roll back a bad deployment
doc_type: runbook
system: api-backend
version: "1.2"
status: current
updated: 2026-10-27
tags: [rollback, deployment, release]
owner: platform-team
---
# Runbook - roll back a bad deployment

## When to roll back
Roll back when errors or latency increase right after a rollout and you cannot fix them within about 15 minutes.

## Steps
1. Find the previous good image tag in the deployment history.
2. Redeploy that tag. The rollout uses the same gradual process and health checks.
3. Confirm `/readyz` is healthy and the error rate returns to normal.
4. Do not reverse database migrations. They are backward compatible, so the old version runs on the new schema.
5. Open a ticket describing the failed change and block the release until it is fixed.
