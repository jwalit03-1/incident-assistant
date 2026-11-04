import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from redaction import redact, _D, _P

def types(t):
    return dict(redact(t)[1])

def test_iban_with_spaces_and_trailing_word():
    out, c = redact("Refund failed, IBAN DE89 3704 0044 0532 0130 00 was rejected")
    assert out == "Refund failed, IBAN [IBAN] was rejected" and c["IBAN"] == 1

def test_iban_lowercase_and_zero_width():
    assert types("de89370400440532013000") == {"IBAN": 1}
    assert types("DE89 3704\u200b0044 0532 0130 00") == {"IBAN": 1}

def test_invalid_iban_kept():
    assert "IBAN" not in types("DE89 3704 0044 0532 0130 01")

def test_card_luhn():
    assert types("card 4111 1111 1111 1111") == {"CARD": 1}
    assert "CARD" not in types("order 4111 1111 1111 1112")

def test_aadhaar_verhoeff():
    inv = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]
    payload, c = "23456789012", 0
    for i, ch in enumerate(reversed(payload)):
        c = _D[c][_P[(i + 1) % 8][int(ch)]]
    valid = payload + str(inv[c])
    assert types(f"aadhaar {valid}") == {"AADHAAR": 1}

def test_misc():
    t = types("mail a.b@corp.com from 10.1.2.3 password: hunter2 call +91 98765 43210")
    assert t == {"EMAIL": 1, "IP": 1, "SECRET": 1, "PHONE": 1}

def test_incident_numbers_untouched():
    assert redact("See INC0010023 and KB0012345")[0] == "See INC0010023 and KB0012345"
