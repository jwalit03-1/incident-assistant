---
title: Runbook - payment gateway timeouts
doc_type: runbook
system: billing
version: "1.3"
status: current
updated: 2026-07-30
tags: [timeout, gateway, payments]
---
# Runbook - payment gateway timeouts

## Symptoms
Customers see "payment pending" for more than two minutes. The logs show gateway error GW-504.

## Steps
1. Check the gateway status page for an incident.
2. If the gateway is healthy, restart the payment worker and watch the queue depth.
3. If the queue keeps growing, enable the fallback gateway flag and inform the on-call lead.
