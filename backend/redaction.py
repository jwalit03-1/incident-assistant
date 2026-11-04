"""PII redaction layer.

Deterministic detectors (checksum-validated where the format has one) plus an
optional Presidio NER pass for names/locations. Everything that leaves this
service towards the LLM (user input, ServiceNow text, final answer) goes
through redact(). Only entity types and counts are ever logged, never values.
"""
import os
import re
from collections import Counter

ZERO_WIDTH = re.compile("[\u200b\u200c\u200d\u2060\ufeff]")

# ---------- validators ----------
def iban_ok(s: str) -> bool:
    if not (15 <= len(s) <= 34 and s[:2].isalpha() and s[2:4].isdigit() and s.isalnum()):
        return False
    moved = s[4:] + s[:4]
    return int("".join(str(int(c, 36)) for c in moved)) % 97 == 1


def luhn_ok(digits: str) -> bool:
    total = 0
    for i, ch in enumerate(reversed(digits)):
        n = int(ch)
        if i % 2:
            n = n * 2 - 9 if n > 4 else n * 2
        total += n
    return total % 10 == 0


_D = [[0,1,2,3,4,5,6,7,8,9],[1,2,3,4,0,6,7,8,9,5],[2,3,4,0,1,7,8,9,5,6],[3,4,0,1,2,8,9,5,6,7],
      [4,0,1,2,3,9,5,6,7,8],[5,9,8,7,6,0,4,3,2,1],[6,5,9,8,7,1,0,4,3,2],[7,6,5,9,8,2,1,0,4,3],
      [8,7,6,5,9,3,2,1,0,4],[9,8,7,6,5,4,3,2,1,0]]
_P = [[0,1,2,3,4,5,6,7,8,9],[1,5,7,6,2,8,3,0,9,4],[5,8,0,3,7,9,6,1,4,2],[8,9,1,6,0,4,3,5,2,7],
      [9,4,5,3,1,2,6,8,7,0],[4,2,8,6,5,7,3,9,0,1],[2,7,9,3,8,0,6,4,1,5],[7,0,4,6,9,1,3,2,5,8]]


def verhoeff_ok(digits: str) -> bool:  # Aadhaar checksum
    c = 0
    for i, ch in enumerate(reversed(digits)):
        c = _D[c][_P[i % 8][int(ch)]]
    return c == 0


# ---------- patterns ----------
IBAN_CAND = re.compile(r"(?<![A-Za-z0-9])[A-Za-z]{2}\d{2}(?:[ \-]?[A-Za-z0-9]){11,30}")
CARD = re.compile(r"(?<![\w-])(?:\d[ -]?){12,18}\d(?![\w-])")
AADHAAR = re.compile(r"(?<!\d)[2-9]\d{3}[ -]?\d{4}[ -]?\d{4}(?!\d)")
EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
PAN = re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b")
IPV4 = re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b")
PHONE_INTL = re.compile(r"(?<![\w.])\+\d{1,3}[ -]?\(?\d{1,4}\)?(?:[ -]?\d{2,5}){2,4}(?!\w)")
PHONE_10 = re.compile(r"(?<![\w.])\d{10}(?![\w.])")
SECRET_KV = re.compile(
    r"(?i)\b(?:password|passwd|pwd|passcode|secret|token|api[_-]?key)\s*(?:is\b|[:=])\s*(\S+)")
BEARER = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._\-]{16,}")

_ner = None


def _ner_spans(text):
    global _ner
    if os.getenv("REDACT_NER", "false").lower() != "true":
        return []
    if _ner is None:
        try:
            from presidio_analyzer import AnalyzerEngine
            _ner = AnalyzerEngine()
        except Exception:
            _ner = False
    if not _ner:
        return []
    res = _ner.analyze(text=text, language="en", entities=["PERSON", "LOCATION"])
    return [(r.start, r.end, r.entity_type) for r in res if r.score >= 0.6]


IBAN_LEN = {"AL":28,"AD":24,"AT":20,"AZ":28,"BH":22,"BE":16,"BA":20,"BG":22,"HR":21,"CY":28,"CZ":24,
            "DK":18,"DO":28,"EE":20,"FO":18,"FI":18,"FR":27,"GE":22,"DE":22,"GI":23,"GR":27,"GL":18,
            "HU":28,"IS":26,"IE":22,"IL":23,"IT":27,"JO":30,"KZ":20,"XK":20,"KW":30,"LV":21,"LB":28,
            "LI":21,"LT":20,"LU":20,"MK":19,"MT":31,"MR":27,"MU":30,"MD":24,"MC":27,"ME":22,"NL":18,
            "NO":15,"PK":24,"PS":29,"PL":28,"PT":25,"QA":29,"RO":24,"SM":27,"SA":24,"RS":22,"SK":24,
            "SI":19,"ES":24,"SE":24,"CH":21,"TN":24,"TR":26,"AE":23,"GB":22,"VG":24}


def _iban_spans(text):
    for m in IBAN_CAND.finditer(text):
        idx = [i for i in range(m.start(), m.end()) if text[i].isalnum()]
        comp = "".join(text[i] for i in idx).upper()
        # known country -> exact length (avoids swallowing following words); else shortest valid
        lengths = [IBAN_LEN[comp[:2]]] if comp[:2] in IBAN_LEN else range(15, len(comp) + 1)
        for n in lengths:
            if n <= len(comp) and iban_ok(comp[:n]):
                yield idx[0], idx[n - 1] + 1
                break


def find_pii(text: str):
    found = []

    def add(s, e, label):
        if all(e <= a or s >= b for a, b, _ in found):
            found.append((s, e, label))

    for s, e in _iban_spans(text):
        add(s, e, "IBAN")
    for m in CARD.finditer(text):
        d = re.sub(r"\D", "", m.group())
        if 13 <= len(d) <= 19 and luhn_ok(d):
            add(m.start(), m.end(), "CARD")
    for m in AADHAAR.finditer(text):
        if verhoeff_ok(re.sub(r"\D", "", m.group())):
            add(m.start(), m.end(), "AADHAAR")
    for m in SECRET_KV.finditer(text):
        add(m.start(1), m.end(1), "SECRET")
    for m in BEARER.finditer(text):
        add(m.start(), m.end(), "SECRET")
    for m in EMAIL.finditer(text):
        add(m.start(), m.end(), "EMAIL")
    for m in PAN.finditer(text):
        add(m.start(), m.end(), "PAN")
    if os.getenv("REDACT_IPS", "true").lower() == "true":
        for m in IPV4.finditer(text):
            add(m.start(), m.end(), "IP")
    for rx in (PHONE_INTL, PHONE_10):
        for m in rx.finditer(text):
            add(m.start(), m.end(), "PHONE")
    for s, e, label in _ner_spans(text):
        add(s, e, label)
    return sorted(found)


def redact(text):
    """Return (redacted_text, Counter of entity types)."""
    if not text:
        return text or "", Counter()
    text = ZERO_WIDTH.sub("", text)
    spans = find_pii(text)
    for s, e, label in reversed(spans):
        text = text[:s] + f"[{label}]" + text[e:]
    return text, Counter(label for _, _, label in spans)
