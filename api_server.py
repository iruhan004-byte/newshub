"""
API layer for the News Verifier pipeline, so it can be called from a
mobile app instead of only the command line.

Run locally:
    uvicorn api_server:app --reload --port 8000

Deploy: push this whole backend/ folder to Render/Railway with the start
command:
    uvicorn api_server:app --host 0.0.0.0 --port $PORT
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from planner import extract_claims
from researcher import research_all
from synthesizer import synthesize_all
from critic import final_verdict

app = FastAPI(title="News Verifier API")

# Allow the Flutter app (or anything) to call this API from any origin.
# Tighten this to your app's domain once you're past prototyping.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class VerifyRequest(BaseModel):
    text: str


class SourceOut(BaseModel):
    title: str
    url: str
    domain: str
    trust: str


class ClaimEvidenceOut(BaseModel):
    claim: str
    summary: str
    trusted_source_count: int
    total_sources_found: int
    sources: list[SourceOut]


class PerClaimVerdictOut(BaseModel):
    claim: str
    verdict: str
    confidence: int


class VerdictOut(BaseModel):
    overall_verdict: str
    confidence_score: int
    reasoning: str
    per_claim_verdicts: list[PerClaimVerdictOut]
    what_would_increase_confidence: str


class VerifyResponse(BaseModel):
    input_text: str
    per_claim_evidence: list[ClaimEvidenceOut]
    verdict: VerdictOut


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/verify", response_model=VerifyResponse)
def verify(req: VerifyRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="text must not be empty")

    try:
        claims = extract_claims(text)
        if not claims:
            raise HTTPException(status_code=422, detail="No checkable claims found in this text.")

        research_results = research_all(claims)
        synthesized = synthesize_all(research_results)
        verdict = final_verdict(synthesized)

        per_claim_evidence = [
            {
                "claim": s["claim"],
                "summary": s["summary"],
                "trusted_source_count": s["trusted_source_count"],
                "total_sources_found": s["total_sources_found"],
                "sources": [
                    {
                        "title": r["title"],
                        "url": r["url"],
                        "domain": r["domain"],
                        "trust": r["credibility"]["trust"],
                    }
                    for r in s["search_results"]
                ],
            }
            for s in synthesized
        ]

        return {
            "input_text": text,
            "per_claim_evidence": per_claim_evidence,
            "verdict": verdict,
        }
    except HTTPException:
        raise
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(e)) from e
