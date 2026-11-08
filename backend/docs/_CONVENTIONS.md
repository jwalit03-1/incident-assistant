# Documentation conventions

This folder is the documentation source for the resolution finder. Files whose names start with `_` and any `README.md` are not indexed.

## Folder layout
docs/<doc_type>/<system>/<page>.md

- doc_type: `technical` (how it is built and configured), `functional` (how it should behave), `runbook` (what to do when it breaks).
- system: the product or component, for example `api-backend`, `billing`, `networking`.
- One topic per page. Use lowercase file names with hyphens.

## Front matter (all fields optional, but use them)
title, doc_type, system, version, status (current | draft | deprecated), updated (YYYY-MM-DD), tags (list), owner.
Deprecated pages are never returned by search.

## Writing rules
- One H1 per file, then H2 sections. Headings are used for ranking and for citations, so make them descriptive.
- Put exact error codes, setting names and endpoints in the text; search matches them literally.
- Keep sections short (a few paragraphs). Long sections are split automatically.
- Never include real secrets, customer data, emails or account numbers. Use placeholders such as <token>.
- Update `updated` and `version` when the content changes. Mark replaced pages `deprecated`.
