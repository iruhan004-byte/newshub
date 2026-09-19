"""
Planner agent: breaks the input news text into a small set of discrete,
independently-checkable factual claims. This keeps the Researcher focused
instead of trying to verify a whole article as one blob.
"""
from llm import call_llm_json

SYSTEM = (
    "You are a meticulous news analyst. Your only job is to extract the "
    "core FACTUAL claims from a piece of news text — the specific, checkable "
    "assertions (who/what/when/where/how much), not opinions or framing."
)

PROMPT_TEMPLATE = """News text to analyze:
---
{text}
---

Extract 2-6 distinct, checkable factual claims from this text.
For each claim also note:
- any named entities (people, organizations, places) involved
- any dates or numbers mentioned
- a short search-friendly query to look this up

Return JSON in this exact shape:
{{
  "claims": [
    {{
      "claim": "short factual statement",
      "entities": ["..."],
      "search_query": "short query"
    }}
  ]
}}
"""


def extract_claims(news_text: str) -> list[dict]:
    result = call_llm_json(PROMPT_TEMPLATE.format(text=news_text.strip()), system=SYSTEM)
    return result.get("claims", [])
