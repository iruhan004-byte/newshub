"""
Google Fact Check Tools API (free, needs a Google Cloud API key with the
'Fact Check Tools API' enabled). Skipped gracefully if no key is set.
"""
import requests
import config


def query_factcheck_db(claim: str) -> list[dict]:
    if not config.GOOGLE_FACTCHECK_API_KEY:
        return []
    try:
        r = requests.get(
            "https://factchecktools.googleapis.com/v1alpha1/claims:search",
            params={"query": claim, "key": config.GOOGLE_FACTCHECK_API_KEY},
            timeout=20,
        )
        r.raise_for_status()
        data = r.json()
    except Exception as e:  # noqa: BLE001
        print(f"[factcheck_api] lookup failed: {e}")
        return []

    out = []
    for c in data.get("claims", []):
        for review in c.get("claimReview", []):
            out.append({
                "claim_text": c.get("text", claim),
                "publisher": review.get("publisher", {}).get("name", ""),
                "rating": review.get("textualRating", ""),
                "url": review.get("url", ""),
            })
    return out
