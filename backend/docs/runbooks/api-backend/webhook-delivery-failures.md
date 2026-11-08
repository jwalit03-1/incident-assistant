---
title: Runbook - webhook delivery failures
doc_type: runbook
system: api-backend
version: "1.3"
status: current
updated: 2026-10-26
tags: [webhooks, delivery, retries, signature]
owner: platform-team
---
# Runbook - webhook delivery failures

## Symptoms
A customer reports missing events, or the delivery dashboard shows many failed or retrying deliveries.

## Steps
1. Open the delivery log for the client and read the last HTTP status and error.
2. Timeouts mean the customer endpoint takes longer than 10 seconds. Ask them to acknowledge quickly and process later.
3. TLS errors mean an expired or untrusted certificate on the customer side.
4. A customer reporting "signature mismatch" is usually hashing a re-serialised body. They must use the raw bytes.
5. After the customer fixes the endpoint, replay the failed events from the admin tool.
