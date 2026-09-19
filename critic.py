"""
Critic agent: the final judge. Weighs all synthesized evidence across all
claims and produces an overall confidence score + verdict + reasoning.
Deliberately never outputs 100% — see README for why.
"""
from llm import call_llm_json

SYSTEM = (
    "You are a skeptical, rigorous fact-checking editor, similar to Reuters "
    "Fact Check or AFP Fact Check. You weigh evidence quality (source "
    "credibility, cross-referencing, fact-check DB hits, conflicts) and "
    "produce a calibrated confidence score. You NEVER output 100 or 0 — "
    "genuine uncertainty always remains. You are explicit about what would "
    "increase your confidence further."
)

PROMPT_TEMPLATE = """Here is the per-claim evidence synthesis for a news item:

{claim_summaries}

Based on ALL of this, produce a JSON verdict in this exact shape:
{{
  "overall_verdict": "Likely Genuine | Uncertain | Likely Fake",
  "confidence_score": 0-99,
  "reasoning": "2-4 sentences explaining the score, citing which claims were well or poorly supported",
  "per_claim_verdicts": [
    {{"claim": "...", "verdict": "Supported | Contradicted | Unverified", "confidence": 0-99}}
  ],
  "what_would_increase_confidence": "1-2 sentences"
}}
"""


def _format_claims(synthesized: list[dict]) -> str:
    blocks = []
    for s in synthesized:
        blocks.append(
            f"Claim: {s['claim']}\n"
            f"Trusted sources found: {s['trusted_source_count']}/{s['total_sources_found']}\n"
            f"Fact-check DB hits: {len(s['factcheck_hits'])}\n"
            f"Summary: {s['summary']}\n"
        )
    return "\n---\n".join(blocks)


def final_verdict(synthesized_results: list[dict]) -> dict:
    return call_llm_json(
        PROMPT_TEMPLATE.format(claim_summaries=_format_claims(synthesized_results)),
        system=SYSTEM,
    )
