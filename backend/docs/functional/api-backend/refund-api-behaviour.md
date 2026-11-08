---
title: Refund API behaviour
doc_type: functional
system: api-backend
version: "1.6"
status: current
updated: 2026-10-02
tags: [refunds, partial-refund, idempotency]
owner: product-team
---
# Refund API behaviour

## Creating a refund
Send `POST /v1/orders/{id}/refunds` with an amount and an `Idempotency-Key`. The token needs the `refunds:write` scope.

## Rules
- Refunds are possible for orders in `paid`, `fulfilled` or `completed`, within 30 days of payment.
- Partial refunds are allowed. The total refunded can never exceed the amount paid.
- A refund above the remaining refundable amount returns `VAL-422`.

## Processing
Refunds are processed asynchronously. The refund starts as `pending` and becomes `succeeded` or `failed`. When the order is fully refunded, an `order.refunded` webhook is sent.
