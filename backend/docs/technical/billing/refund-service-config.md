---
title: Refund service configuration
doc_type: technical
system: billing
version: "4.2"
status: current
updated: 2026-09-14
tags: [refunds, sepa, iban, gateway]
owner: payments-team
---
# Refund service configuration

## Settings
`REFUND_RETRY_COUNT` controls automatic retries (default 3). `REFUND_GATEWAY_TIMEOUT_MS` defaults to 8000. Raise it only after checking the gateway status page.

## Rejected refunds
Error RF-4021 means the destination account failed validation. Example payload used in testing for account DE89 3704 0044 0532 0130 00, owner contact jane.doe@example.com. Ask the customer to confirm the account number and resubmit.

## Retries
Failed refunds are retried with a 10 minute back-off. After the final retry the refund moves to the manual review queue.
