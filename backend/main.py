import hmac
import logging
import os
from typing import Literal

from dotenv import load_dotenv

load_dotenv()  # must run before modules that read env at import time

from fastapi import FastAPI, Header, HTTPException  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

import agent  # noqa: E402

log = logging.getLogger("incident-assistant")
ACCESS_KEY = os.getenv("ACCESS_KEY", "")
app = FastAPI(title="Incident resolution assistant")
app.add_middleware(CORSMiddleware,
                   allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
                   allow_methods=["POST", "GET"], allow_headers=["Content-Type", "X-Access-Key"])


class Turn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=4000)


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    history: list[Turn] = Field(default_factory=list, max_length=20)


@app.get("/api/health")
def health():
    return {"ok": True}


@app.post("/api/chat")
def chat(body: ChatIn, x_access_key: str = Header(default="")):
    if os.getenv("VERCEL") and not ACCESS_KEY:  # fail closed: never expose a public deployment without a key
        raise HTTPException(503, "ACCESS_KEY is not configured on the server.")
    if ACCESS_KEY and not hmac.compare_digest(x_access_key.encode(), ACCESS_KEY.encode()):
        raise HTTPException(401, "Access key required.")
    try:
        out = agent.chat([t.model_dump() for t in body.history], body.message)
        log.info("chat sources=%d redactions=%s", len(out["sources"]), out["redactions"])  # counts only
        return out
    except Exception:
        log.exception("chat failed")
        raise HTTPException(502, "The assistant is unavailable. Check the API keys and ServiceNow instance, then retry.")
