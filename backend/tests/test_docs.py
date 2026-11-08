import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("OPENROUTER_API_KEY", "x")
from collections import Counter
import docs, agent


def setup_module(_):
    docs.reload()


def test_sample_docs_load():
    s = docs.stats()
    assert s["files"] >= 6 and s["chunks"] >= 10


def test_search_skips_deprecated_and_cites_heading():
    res, _ = docs.search_docs(["vpn", "809"])
    assert res and res[0]["title"].startswith("VPN gateway")
    assert all("retired" not in r["title"].lower() for r in res)
    assert "Known issues" in res[0]["heading_path"]


def test_filters():
    res, _ = docs.search_docs(["refund"], doc_type="functional")
    assert res and all(r["doc_type"] == "functional" for r in res)
    res, _ = docs.search_docs(["refund"], system="email")
    assert res == []


def test_pii_redacted_in_search_and_get():
    res, counts = docs.search_docs(["RF-4021"])
    blob = str(res)
    assert "DE89" not in blob and "jane.doe@example.com" not in blob
    doc, c = docs.get_doc("technical/billing/refund-service-config.md", "Rejected")
    assert "[IBAN]" in doc["content"] and "[EMAIL]" in doc["content"] and c["IBAN"] == 1


def test_get_doc_unknown_path_and_section():
    assert docs.get_doc("../../etc/passwd")[0]["error"] == "Document not found"
    assert docs.get_doc("technical/networking/vpn-gateway-setup.md", "nope")[0]["error"] == "Section not found"


def test_search_all_merges_sources(monkeypatch):
    monkeypatch.setattr(agent.sn, "search_incidents",
                        lambda k, c=None, l=5: ([{"number": "INC1", "url": "u", "short_description": "VPN drop"}], Counter()))
    data, _ = agent._run_tool("search_all", {"keywords": ["vpn"]})
    assert data["incidents"] and data["docs"]
    sources = {}
    agent._collect(data, sources)
    assert {s["kind"] for s in sources.values()} == {"incident", "doc"}


def test_search_all_survives_servicenow_failure(monkeypatch):
    def boom(*a, **k): raise RuntimeError("down")
    monkeypatch.setattr(agent.sn, "search_incidents", boom)
    data, _ = agent._run_tool("search_all", {"keywords": ["vpn"]})
    assert data["incidents"] == [] and data["docs"] and "incident_search_error" in data


def test_api_backend_docs_complete_and_findable():
    docs.reload()
    chunks = [c for c in docs._index()["chunks"] if c["system"] == "api-backend"]
    assert len({c["path"] for c in chunks}) >= 14
    assert all(c["version"] and c["updated"] and c["status"] == "current" for c in chunks)
    assert {c["doc_type"] for c in chunks} == {"technical", "functional", "runbook"}
    assert not any(c["title"] in ("Documentation conventions", "<Short descriptive title>") for c in docs._index()["chunks"])  # _files are not indexed

    res, _ = docs.search_docs(["429", "retry-after"])
    assert any("rate-limiting" in r["path"] for r in res)
    res, _ = docs.search_docs(["connection", "pool"], doc_type="runbook")
    assert res and "database-connection-pool" in res[0]["path"]
    res, _ = docs.search_docs(["signature", "webhook"], doc_type="technical")
    assert res and "webhooks" in res[0]["path"]
    res, _ = docs.search_docs(["refund", "30 days"], doc_type="functional", system="api-backend")
    assert res and "refund-api" in res[0]["path"]
