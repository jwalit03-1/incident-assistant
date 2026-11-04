"""Read-only ServiceNow Table API client. All free text is redacted on the way out."""
import os
import re
from collections import Counter

import httpx

from redaction import redact

BASE = os.getenv("SERVICENOW_INSTANCE", "").rstrip("/")
AUTH = (os.getenv("SERVICENOW_USER", ""), os.getenv("SERVICENOW_PASSWORD", ""))
FIELDS = ("sys_id,number,short_description,description,category,subcategory,"
          "close_code,close_notes,resolved_at")
LIMITS = {"short_description": 200, "description": 600, "close_notes": 900}


def _get(params):
    if not BASE:
        raise RuntimeError("SERVICENOW_INSTANCE is not configured")
    r = httpx.get(f"{BASE}/api/now/table/incident", params=params, auth=AUTH,
                  headers={"Accept": "application/json"}, timeout=20)
    r.raise_for_status()
    return r.json()["result"]


def _clean(rec, counts: Counter, full: bool):
    out = {
        "number": rec.get("number"),
        "short_description": rec.get("short_description"),
        "category": rec.get("category"),
        "close_code": rec.get("close_code"),
        "resolved_at": rec.get("resolved_at"),
        "close_notes": rec.get("close_notes"),
        "url": f"{BASE}/nav_to.do?uri=incident.do?sys_id={rec.get('sys_id')}",
    }
    if full:
        out["description"] = rec.get("description")
    for k, limit in LIMITS.items():
        if out.get(k):
            out[k], c = redact(out[k][:limit])
            counts.update(c)
    return out


def _safe(term: str) -> str:
    return re.sub(r"[\^\r\n]", " ", term).strip()[:60]  # block encoded-query injection


def search_incidents(keywords, category=None, limit=5):
    """Resolved/closed incidents with resolution notes, ranked by #keywords matched."""
    counts, hits, recs = Counter(), Counter(), {}
    for term in [t for t in map(_safe, keywords) if t][:4]:
        q = (f"stateIN6,7^short_descriptionLIKE{term}^ORdescriptionLIKE{term}"
             f"^ORclose_notesLIKE{term}^close_notesISNOTEMPTY")
        if category and re.fullmatch(r"[\w ]{1,40}", category):
            q += f"^category={category}"
        q += "^ORDERBYDESCresolved_at"
        rows = _get({"sysparm_query": q, "sysparm_fields": FIELDS, "sysparm_limit": 10,
                     "sysparm_display_value": "true"})
        for r in rows:
            hits[r["sys_id"]] += 1
            recs[r["sys_id"]] = r
    ranked = [i for i, _ in hits.most_common(max(1, min(int(limit), 8)))]
    return [_clean(recs[i], counts, full=False) for i in ranked], counts


def get_incident(number):
    counts = Counter()
    if not re.fullmatch(r"INC\d{4,12}", number or ""):
        return {"error": "Invalid incident number"}, counts
    rows = _get({"sysparm_query": f"number={number}", "sysparm_fields": FIELDS,
                 "sysparm_limit": 1, "sysparm_display_value": "true"})
    if not rows:
        return {"error": "Incident not found"}, counts
    return _clean(rows[0], counts, full=True), counts
