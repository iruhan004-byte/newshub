"""
Researcher agent: for each claim, gathers evidence from
  1. live web search (cross-referencing across outlets)
  2. domain credibility check on every source found
  3. Google Fact Check Tools DB (if configured)
"""
import config
from search import web_search
from domain_check import check_domain
from factcheck_api import query_factcheck_db


def research_claim(claim_obj: dict) -> dict:
    query = claim_obj.get("search_query") or claim_obj["claim"]

    search_results = web_search(query, max_results=config.MAX_SEARCH_RESULTS_PER_CLAIM)
    for r in search_results:
        r["credibility"] = check_domain(r["domain"])

    trusted_hits = [r for r in search_results if r["credibility"]["trust"] == "high"]
    factcheck_hits = query_factcheck_db(claim_obj["claim"])

    return {
        "claim": claim_obj["claim"],
        "search_results": search_results,
        "trusted_source_count": len(trusted_hits),
        "total_sources_found": len(search_results),
        "factcheck_hits": factcheck_hits,
    }


def research_all(claims: list[dict]) -> list[dict]:
    return [research_claim(c) for c in claims]
