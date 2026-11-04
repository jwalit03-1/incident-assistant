import os, sys, json, types
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("OPENROUTER_API_KEY", "x")
os.environ["ACCESS_KEY"] = "s3cret"
os.environ["CORS_ORIGINS"] = "https://app.vercel.app/ , https://other.vercel.app"
from fastapi.testclient import TestClient
import main, agent


def test_requires_access_key(monkeypatch):
    monkeypatch.setattr(main.agent, "chat", lambda prior, msg: {"reply": f"ok:{len(prior)}", "sources": [], "redactions": {}})
    c = TestClient(main.app)
    assert c.post("/api/chat", json={"message": "hi"}).status_code == 401
    r = c.post("/api/chat", json={"message": "hi", "history": [{"role": "user", "content": "a"}]},
               headers={"X-Access-Key": "s3cret"})
    assert r.status_code == 200 and r.json()["reply"] == "ok:1"


def test_fail_closed_on_vercel_without_key(monkeypatch):
    monkeypatch.setattr(main, "ACCESS_KEY", "")
    monkeypatch.setenv("VERCEL", "1")
    assert TestClient(main.app).post("/api/chat", json={"message": "hi"}).status_code == 503


def test_agent_is_stateless_and_redacts_history(monkeypatch):
    sent = []
    def fake_create(**kw):
        sent.append(json.dumps(kw["messages"]))
        m = types.SimpleNamespace(content="done", tool_calls=None)
        return types.SimpleNamespace(choices=[types.SimpleNamespace(message=m)])
    monkeypatch.setattr(agent.client.chat.completions, "create", fake_create)
    out = agent.chat([{"role": "assistant", "content": "orphan"}, {"role": "user", "content": "mail a@b.com"},
                      {"role": "assistant", "content": "ok"}], "next question")
    assert "a@b.com" not in sent[0] and "[EMAIL]" in sent[0] and "orphan" not in sent[0]
    assert out["reply"] == "done"


def test_cors_preflight_and_health():
    c = TestClient(main.app)
    h = {"Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "content-type,x-access-key"}
    ok = c.options("/api/chat", headers={"Origin": "https://app.vercel.app", **h})
    assert ok.status_code == 200 and ok.headers["access-control-allow-origin"] == "https://app.vercel.app"
    assert c.options("/api/chat", headers={"Origin": "https://evil.example", **h}).status_code == 400
    assert c.get("/api/health").json()["cors_origins"] == ["https://app.vercel.app", "https://other.vercel.app"]
