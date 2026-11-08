---
title: Runbook - Outlook not syncing mail
doc_type: runbook
system: email
version: "1.1"
status: current
updated: 2026-06-11
tags: [outlook, mail, sync, ost]
---
# Runbook - Outlook not syncing mail

## Quick checks
Confirm the status bar shows "Connected". Disable work offline mode. Check that the mailbox is not over its size limit.

## Rebuild the cache
Close Outlook, rename the OST file in the local Outlook data folder, and start Outlook so it rebuilds the cache. A full resync of a large mailbox can take an hour.
