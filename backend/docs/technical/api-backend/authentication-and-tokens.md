---
title: Authentication and access tokens
doc_type: technical
system: api-backend
version: "2.1"
status: current
updated: 2026-10-05
tags: [oauth2, jwt, scopes, jwks, auth]
owner: platform-team
---
# Authentication and access tokens

## Getting a token
Clients use the OAuth2 client credentials flow. Send a POST request to `/v1/oauth/token` with the client id and client secret. The response contains an access token that is valid for 3600 seconds. Request a new token shortly before expiry instead of on every call.

## Using the token
Send the token in the header `Authorization: Bearer <token>`. Tokens are JWTs signed with RS256. The service verifies the signature using the public keys published at `/.well-known/jwks.json`, and checks the issuer, audience and expiry. A clock skew of 60 seconds is tolerated.

## Scopes
| Scope | Allows |
|---|---|
| `orders:read` | Read orders and customers |
| `orders:write` | Create and update orders |
| `refunds:write` | Create refunds |

A missing scope returns `AUTH-403`. An invalid or expired token returns `AUTH-401`.

## Key rotation
Signing keys rotate every 90 days. The new key appears in the key set before it is used. The service caches the key set for `JWKS_CACHE_SECONDS` (default 300), so validation of tokens signed with a new key can fail briefly if the cache is stale.
