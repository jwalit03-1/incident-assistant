---
title: Print queue and printer offline setup
doc_type: technical
system: printing
version: "1.0"
status: current
updated: 2026-05-02
tags: [printer, offline, queue]
---
# Print queue and printer offline setup

## Floor printers
Each floor printer is published from the print server. If a printer shows offline for a whole floor, check the print spooler service on the server first and then the printer's network link.

## Clearing a stuck queue
Stop the print spooler service, delete the files in the spool folder, and start the service again.
