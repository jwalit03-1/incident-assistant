---
title: Runbook - spike in AUTH-401 token failures
doc_type: runbook
system: api-backend
version: "1.1"
status: current
updated: 2026-10-23
tags: [auth, jwt, jwks, key-rotation, AUTH-401]
owner: platform-team
---
# Runbook - spike in AUTH-401 token failures

## Symptoms
Many clients suddenly receive `AUTH-401` although their credentials did not change. Tokens that worked a minute ago are rejected.

## Likely causes
- A signing key was rotated and the service still holds an old key set in its cache.
- The server clock drifted more than 60 seconds.
- The audience setting `JWT_AUDIENCE` was changed or is wrong in one environment.

## Steps
1. Compare the `kid` in a rejected token with the keys listed at `/.well-known/jwks.json`.
2. If the key is missing from the service's view, restart the instances to clear the key cache. A shorter `JWKS_CACHE_SECONDS` reduces this risk.
3. Check the system clock and time synchronisation on the hosts.
4. Confirm the issuer and audience settings match the token.
