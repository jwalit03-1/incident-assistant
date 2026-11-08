---
title: Order lifecycle and states
doc_type: functional
system: api-backend
version: "2.2"
status: current
updated: 2026-09-25
tags: [orders, states, cancellation]
owner: product-team
---
# Order lifecycle and states

## States
An order moves through these states: `created`, `pending_payment`, `paid`, `fulfilled` and `completed`. An order can also end as `cancelled` or `refunded`.

## Allowed changes
- An order can be cancelled only before it is `fulfilled`.
- Payment can only be recorded on an order in `pending_payment`.
- A completed order cannot be edited, only refunded.
Any other change returns `ORD-409`.

## Notifications
Each state change publishes an event. Customers who registered a webhook receive `order.created`, `order.paid` or `order.refunded` accordingly.
