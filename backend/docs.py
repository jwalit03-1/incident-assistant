"""Local Markdown documentation search.

Layout: docs/<doc_type>/<system>/<page>.md with optional front matter
(title, doc_type, system, version, status, updated, tags). Files are split at headings,
redacted once at load time, and searched with a small keyword scorer (no extra services).
"""
import math
import os
import re
from collections import Counter
from pathlib import Path
from urllib.parse import quote

from redaction import redact

MAX_CHUNK = 1800
MAX_RETURN = 4000
HEADING = re.compile(r"^(#{1,4})\s+(.+?)\s*#*\s*$")
FENCE = re.compile(r"^\s*```")
_INDEX = None


def _front_matter(text):
    meta = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            for line in text[3:end].splitlines():
                if ":" not in line or line.lstrip().startswith("#"):
                    continue
                k, v = line.split(":", 1)
                v = re.sub(r"\s+#.*$", "", v).strip()
                if v.startswith("[") and v.endswith("]"):
                    meta[k.strip().lower()] = [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
                else:
                    meta[k.strip().lower()] = v.strip("'\"")
            return meta, text[end + 4:].lstrip("\n")
    return meta, text


def _split_long(text):
    """Split on blank lines outside code fences into pieces under MAX_CHUNK."""
    paras, cur, fence = [], [], False
    for line in text.split("\n"):
        if FENCE.match(line):
            fence = not fence
        if not line.strip() and not fence:
            if cur:
                paras.append("\n".join(cur))
                cur = []
        else:
            cur.append(line)
    if cur:
        paras.append("\n".join(cur))
    out, buf = [], ""
    for p in paras:
        if buf and len(buf) + len(p) + 2 > MAX_CHUNK:
            out.append(buf)
            buf = p
        else:
            buf = f"{buf}\n\n{p}" if buf else p
    if buf:
        out.append(buf)
    return out


def _chunks(body, title):
    stack, buf, chunks, fence = [], [], [], False

    def flush():
        text = "\n".join(buf).strip()
        if text:
            path = " > ".join(h for _, h in stack) or title
            chunks.extend((path, piece) for piece in _split_long(text))
        buf.clear()

    for line in body.split("\n"):
        if FENCE.match(line):
            fence = not fence
        m = None if fence else HEADING.match(line)
        if m:
            flush()
            level = len(m.group(1))
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, m.group(2)))
        else:
            buf.append(line)
    flush()
    return chunks


def load(root):
    root, files, chunks = Path(root), set(), []
    if not root.is_dir():
        return {"files": files, "chunks": chunks}
    for f in sorted(root.rglob("*.md")):
        if f.name.startswith("_") or f.name.lower() == "readme.md":
            continue
        rel = f.relative_to(root).as_posix()
        parts = rel.split("/")
        meta, body = _front_matter(f.read_text(encoding="utf-8", errors="ignore"))
        title = str(meta.get("title") or "")
        if not title:
            title = next((m.group(2) for m in map(HEADING.match, body.split("\n")) if m), f.stem)
        info = {
            "path": rel, "title": title,
            "doc_type": str(meta.get("doc_type") or (parts[0] if len(parts) > 1 else "")),
            "system": str(meta.get("system") or (parts[1] if len(parts) > 2 else "")),
            "version": str(meta.get("version") or ""),
            "status": str(meta.get("status") or "current").lower(),
            "updated": str(meta.get("updated") or ""),
        }
        tags = " ".join(meta.get("tags") or []) if isinstance(meta.get("tags"), list) else ""
        files.add(rel)
        for heading_path, piece in _chunks(body, title):
            text, pii = redact(piece)  # redact once, at index time
            chunks.append({**info, "heading_path": heading_path, "text": text, "pii": pii,
                           "text_l": text.lower(),
                           "head_l": f"{title} {heading_path} {tags} {f.stem}".lower()})
    return {"files": files, "chunks": chunks}


def reload(root=None):
    global _INDEX
    root = root or os.getenv("DOCS_PATH") or Path(__file__).parent / "docs"
    _INDEX = load(root)
    return _INDEX


def _index():
    return _INDEX if _INDEX is not None else reload()


def stats():
    idx = _index()
    return {"files": len(idx["files"]), "chunks": len(idx["chunks"])}


def _url(path):
    base = os.getenv("DOCS_BASE_URL", "").rstrip("/")
    return f"{base}/{quote(path)}" if base else None


def search_docs(keywords, doc_type=None, system=None, limit=5, include_deprecated=False):
    idx = _index()
    terms = [t.lower().strip()[:60] for t in keywords if t and t.strip()][:6]
    if not terms:
        return [], Counter()
    pool = [c for c in idx["chunks"]
            if (include_deprecated or c["status"] != "deprecated")
            and (not doc_type or c["doc_type"].lower() == str(doc_type).lower())
            and (not system or c["system"].lower() == str(system).lower())]
    scored = {id(c): [0, 0.0] for c in pool}  # matched terms, score
    for t in terms:
        df = sum(1 for c in pool if t in c["text_l"] or t in c["head_l"])
        idf = math.log(1 + len(pool) / (1 + df))
        for c in pool:
            tf, in_head = c["text_l"].count(t), t in c["head_l"]
            if tf or in_head:
                s = scored[id(c)]
                s[0] += 1
                s[1] += idf * ((1 + math.log(tf) if tf else 0) + (3 if in_head else 0))
    ranked = sorted((c for c in pool if scored[id(c)][0]), key=lambda c: tuple(scored[id(c)]), reverse=True)
    out, per_doc, counts = [], Counter(), Counter()
    for c in ranked:
        if per_doc[c["path"]] >= 2:
            continue
        per_doc[c["path"]] += 1
        counts.update(c["pii"])
        out.append({"path": c["path"], "title": c["title"], "heading_path": c["heading_path"],
                    "doc_type": c["doc_type"], "system": c["system"], "version": c["version"],
                    "updated": c["updated"], "excerpt": c["text"][:600], "url": _url(c["path"])})
        if len(out) >= max(1, min(int(limit), 8)):
            break
    return out, counts


def get_doc(path, section=None):
    cs = [c for c in _index()["chunks"] if c["path"] == path]  # only indexed paths: no filesystem access
    if not cs:
        return {"error": "Document not found"}, Counter()
    if section:
        sel = [c for c in cs if section.lower() in c["heading_path"].lower()]
        if not sel:
            return {"error": "Section not found", "sections": sorted({c["heading_path"] for c in cs})}, Counter()
    else:
        sel = cs
    parts, total, counts = [], 0, Counter()
    for c in sel:
        if total + len(c["text"]) > MAX_RETURN:
            break
        parts.append(f"## {c['heading_path']}\n{c['text']}")
        total += len(c["text"])
        counts.update(c["pii"])
    first = cs[0]
    return {"path": path, "title": first["title"], "doc_type": first["doc_type"], "system": first["system"],
            "version": first["version"], "updated": first["updated"], "url": _url(path),
            "content": "\n\n".join(parts), "truncated": len(parts) < len(sel)}, counts
