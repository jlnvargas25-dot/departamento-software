"""Static CWE/OWASP lookup for security-related Tier C rules."""

from __future__ import annotations

CWE_MAP: dict[str, str] = {
    "CSP-UNSAFE-EVAL": "https://cwe.mitre.org/data/definitions/95.html",
    "CSP-UNSAFE-INLINE": "https://cwe.mitre.org/data/definitions/79.html",
}

OWASP_MAP: dict[str, str] = {
    "CSP-UNSAFE-EVAL": "A03:2021 Injection",
    "CSP-UNSAFE-INLINE": "A07:2021 Cross-Site Scripting (XSS)",
}


def get_security_links(rule_id: str) -> dict[str, str]:
    """Return CWE and OWASP references for a rule_id, if any.

    Args:
        rule_id: The rule identifier to look up.

    Returns:
        Dict with 'cwe' and/or 'owasp' keys. Empty dict if no links.
    """
    links: dict[str, str] = {}
    if rule_id in CWE_MAP:
        links["cwe"] = CWE_MAP[rule_id]
    if rule_id in OWASP_MAP:
        links["owasp"] = OWASP_MAP[rule_id]
    return links
