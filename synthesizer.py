"""
Synthesizer agent: turns raw evidence (search snippets, domain trust,
fact-check hits) into a concise, neutral written summary per claim.
"""
from llm import call_llm

SYSTEM = (
    "You are a neutral evidence synthesizer. You never make a final verdict — "
    "you only summarize what the gathered evidence shows and where it "
    "conflicts or is thin."
)

PROMPT_TEMPLATE = """Claim being checked: "{claim}"

Evidence gathered:
{evidence_block}

Write a short (3-5 sentence) neutral summary of what this evidence shows.
Note explicitly if sources agree, conflict, or if evidence is thin/absent.
Do not give a final genuine/fake verdict — that's a separate step.
"""


def _format_evidence(research_result: dict) -> str:
    lines = []
    for r in research_result["search_results"]:
        cred = r["credibility"]
        lines.append(
            f"- [{cred['trust']} trust | {r['domain']}] {r['title']}: {r['snippet'][:200]}"
        )
    for f in research_result["factcheck_hits"]:
        lines.append(
            f"- [FACT-CHECK | {f['publisher']}] rated \"{f['rating']}\" for: {f['claim_text']}"
        )
    if not lines:
        lines.append("- No search results or fact-check entries found.")
    return "\n".join(lines)


def synthesize(research_result: dict) -> dict:
    evidence_block = _format_evidence(research_result)
    summary = call_llm(
        PROMPT_TEMPLATE.format(claim=research_result["claim"], evidence_block=evidence_block),
        system=SYSTEM,
    )
    return {**research_result, "summary": summary}


def synthesize_all(research_results: list[dict]) -> list[dict]:
    return [synthesize(r) for r in research_results]
