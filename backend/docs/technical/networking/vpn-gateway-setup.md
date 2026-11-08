---
title: VPN gateway setup and client configuration
doc_type: technical
system: networking
version: "3.1"
status: current
updated: 2026-09-02
tags: [vpn, remote-access, windows]
---
# VPN gateway setup and client configuration

## Overview
Staff connect through the corporate VPN gateway using the managed client profile. Split tunnelling is disabled for finance users.

## Client configuration
Import the profile from the software portal. Keep the adapter MTU at 1350 on mobile broadband, because larger packets are fragmented and the tunnel drops under load.

## Known issues
Error 809 means the gateway could not be reached on UDP 500 or 4500. Check that the local router allows IPsec pass-through and that the machine clock is accurate.
After a major Windows feature update the VPN adapter can be reset. Re-import the profile and restart the "IKE and AuthIP IPsec Keying Modules" service.
