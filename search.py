"""
Free web search via the `ddgs` (DuckDuckGo Search) library.
No API key required. Swap in SearXNG/Brave here later if you hit rate limits,
same as you did in the multi-agent research pipeline.
"""
from urllib.parse import urlparse


def web_search(query: str, max_results: int = 6) -> list[dict]:
    """Returns a list of {title, url, snippet, domain}."""
    try:
        from ddgs import DDGS
    except ImportError:
        from duckduckgo_search import DDGS  # older package name fallback

    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            url = r.get("href") or r.get("url", "")
            domain = urlparse(url).netloc.replace("www.", "")
            results.append({
                "title": r.get("title", ""),
                "url": url,
                "snippet": r.get("body", ""),
                "domain": domain,
            })
    return results
