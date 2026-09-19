"""
Cheap, offline-first domain credibility signal.
This is heuristic, not authoritative — it's one input among several that
the Critic agent weighs, not a standalone verdict.
"""
from urllib.parse import urlparse
import config


def check_domain(url_or_domain: str) -> dict:
    domain = urlparse(url_or_domain).netloc or url_or_domain
    domain = domain.replace("www.", "").lower()

    if domain in config.TRUSTED_INTL:
        return {"domain": domain, "trust": "high", "reason": "Established international outlet/fact-checker"}
    if domain in config.TRUSTED_BD:
        return {"domain": domain, "trust": "high", "reason": "Established Bangladeshi outlet/fact-checker"}
    if domain in config.KNOWN_UNRELIABLE:
        return {"domain": domain, "trust": "low", "reason": "Listed as known unreliable source"}

    # Weak heuristics for unknown domains
    flags = []
    if domain.count(".") >= 3:
        flags.append("unusually long subdomain chain")
    if any(ch.isdigit() for ch in domain.split(".")[0]):
        flags.append("digits in domain name")
    if domain.endswith((".tk", ".ml", ".ga", ".cf")):
        flags.append("free/low-cost TLD often used for disposable sites")

    return {
        "domain": domain,
        "trust": "unknown" if not flags else "suspect",
        "reason": "; ".join(flags) if flags else "Not in curated list — verify manually or extend config.py",
    }
