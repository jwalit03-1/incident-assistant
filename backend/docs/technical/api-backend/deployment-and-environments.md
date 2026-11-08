---
title: Deployment and environments
doc_type: technical
system: api-backend
version: "1.9"
status: current
updated: 2026-10-27
tags: [deployment, ci, environments, health-checks]
owner: platform-team
---
# Deployment and environments

## Environments
There are three environments: development, staging and production. Staging mirrors production configuration with smaller capacity and test data.

## Pipeline
A merge to the main branch builds a container image, runs the tests, applies database migrations, and rolls the new image out gradually. The rollout pauses if health checks fail.

## Health checks
`/healthz` reports that the process is running. `/readyz` also checks the database and Redis, and is used by the load balancer to route traffic.

## Rollback
To roll back, redeploy the previous image tag. Migrations are backward compatible, so the previous version can run against the current schema.
