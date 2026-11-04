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
