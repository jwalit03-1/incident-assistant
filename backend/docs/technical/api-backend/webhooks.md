---
title: Webhooks
doc_type: technical
system: api-backend
version: "1.7"
status: current
updated: 2026-10-08
tags: [webhooks, signature, hmac, retries]
owner: platform-team
---
# Webhooks

## Events
The API sends `order.created`, `order.paid` and `order.refunded` events as POST requests with a JSON body to the URL registered for the client.

## Verifying the signature
Each request has an `X-Signature` header and an `X-Timestamp` header. The signature is the HMAC-SHA256 of the raw request body, using the signing secret. Compute it over the exact bytes received, not a re-serialised copy of the JSON, or the signature will not match. Reject requests whose timestamp is older than 5 minutes.

## Delivery and retries
Respond with a 2xx status within 10 seconds. Otherwise the delivery is retried 5 times with increasing delays of 1 minute, 5 minutes, 30 minutes, 2 hours and 12 hours. After the last attempt the event is marked failed and can be replayed by the platform team.
