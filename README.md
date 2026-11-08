# Incident resolution assistant

React chat UI → FastAPI backend → LLM via OpenRouter (tool calling) → ServiceNow Table API (read-only).
A redaction layer (`backend/redaction.py`) runs on user input, ServiceNow text and the final answer.

## Run
```bash
# backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # add OPENROUTER_API_KEY, pick a tool-capable OPENROUTER_MODEL, add PDI details
pytest -q                   # redaction tests
uvicorn main:app --reload --port 8000

# frontend (new terminal)
cd frontend && npm install && npm run dev    # http://localhost:5173
```

## ServiceNow setup
Create a service account (e.g. `svc_ai_agent`) with read access to `incident` only. Seed 100+ resolved
incidents with meaningful `close_notes`; retrieval quality depends on them.

## Redaction
IBAN (mod-97), cards (Luhn), Aadhaar (Verhoeff), PAN, email, phone, IPv4 and `password:`/token patterns.
Optional names/locations via Presidio: install it and set `REDACT_NER=true`.
Placeholders look like `[IBAN]`; only types and counts are logged or shown, never values.

## Known limits
Regex detection is not perfect (free-text names/addresses especially), sessions are in memory,
and basic auth is for a PDI prototype only. Use OAuth, a shared session store and a DPIA before real data.

## Deploy to Vercel (two projects from one repo)
1. **Backend**: import the repo, Root Directory `backend`, add the env vars from `backend/.env.example`
   (including `ACCESS_KEY`; the API refuses to run on Vercel without it) and
   `CORS_ORIGINS=https://YOUR-FRONTEND-DOMAIN`. Turn off Deployment Protection for this project.
   Verify `https://YOUR-BACKEND-DOMAIN/api/health` returns `{"ok":true}`.
2. **Frontend**: second project, Root Directory `frontend`, env var `VITE_API_BASE=https://YOUR-BACKEND-DOMAIN`
   (no trailing slash). Vite bakes it in at build time, so redeploy after changing it.
3. Open the frontend, send a message, and enter the access key when asked.
The frontend is static, so it has no `/api/health` of its own; check the backend URL instead.
The backend is stateless: the browser sends prior turns with each request.

## Documentation search (local Markdown)
Docs live in `backend/docs/<doc_type>/<system>/<page>.md` and ship with the backend deployment.
Optional front matter: `title, doc_type, system, version, status (current|draft|deprecated), updated, tags`.
Folders supply `doc_type` and `system` when front matter omits them. Files starting with `_` and `README.md` are skipped.
Deprecated pages are never returned. Text is split at headings, redacted at load time, and searched by keyword.
- `DOCS_PATH` overrides the folder; `DOCS_BASE_URL` makes results link to your Git host (for example a GitHub blob URL).
- Add or edit a page, push, and Vercel redeploys with the new content.
- `/api/health` shows `docs.files` and `docs.chunks`; if they are 0 on Vercel the docs folder was not bundled.
- The sample pages are fictional; replace them with your own.

### Sample documentation set (api-backend)
`backend/docs/` contains a fictional Orders API documentation set to demo and to copy as a pattern:
```
docs/
  _CONVENTIONS.md  _TEMPLATE.md            (not indexed; rules and a starter page)
  technical/api-backend/   architecture-overview, authentication-and-tokens, rest-api-conventions,
                           rate-limiting, error-codes-reference, database-and-migrations,
                           configuration-reference, webhooks, deployment-and-environments
  functional/api-backend/  order-lifecycle, refund-api-behaviour
  runbooks/api-backend/    high-latency-and-5xx, database-connection-pool-exhausted,
                           token-validation-failures, webhook-delivery-failures, rollback-a-bad-deploy
```
