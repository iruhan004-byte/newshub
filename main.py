"""
News Verifier — Planner -> Researcher -> Synthesizer -> Critic pipeline.

Usage:
    python main.py "paste the news text here"
    python main.py --file article.txt
"""
import argparse
import json
import sys

from planner import extract_claims
from researcher import research_all
from synthesizer import synthesize_all
from critic import final_verdict


def run_pipeline(news_text: str) -> dict:
    print("[1/4] Planner: extracting claims...")
    claims = extract_claims(news_text)
    if not claims:
        raise RuntimeError("Planner found no checkable claims in the input.")
    print(f"      -> {len(claims)} claim(s) found")

    print("[2/4] Researcher: searching + cross-referencing...")
    research_results = research_all(claims)

    print("[3/4] Synthesizer: summarizing evidence per claim...")
    synthesized = synthesize_all(research_results)

    print("[4/4] Critic: producing final verdict...")
    verdict = final_verdict(synthesized)

    return {
        "input_text": news_text,
        "claims": claims,
        "per_claim_evidence": [
            {
                "claim": s["claim"],
                "summary": s["summary"],
                "trusted_source_count": s["trusted_source_count"],
                "total_sources_found": s["total_sources_found"],
                "sources": [
                    {"title": r["title"], "url": r["url"], "domain": r["domain"], "trust": r["credibility"]["trust"]}
                    for r in s["search_results"]
                ],
            }
            for s in synthesized
        ],
        "verdict": verdict,
    }


def main():
    parser = argparse.ArgumentParser(description="Verify whether a news item appears genuine.")
    parser.add_argument("text", nargs="?", help="News text to verify (or use --file)")
    parser.add_argument("--file", help="Path to a .txt file containing the news text")
    parser.add_argument("--image", help="Path to an image file to verify (checks for recycled/out-of-context images)")
    parser.add_argument("--json-out", help="Optional path to save the full result as JSON")
    args = parser.parse_args()

    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            news_text = f.read()
    elif args.text:
        news_text = args.text
    else:
        print("Provide news text as an argument or via --file.", file=sys.stderr)
        sys.exit(1)
    
    # Optional: image verification
    image_result = None
    if args.image:
        from image_verifier import check_image_reuse
        print("[Image] Verifying image...")
        image_result = check_image_reuse(args.image, news_text)

    result = run_pipeline(news_text)
    
    # Attach image result if provided
    if image_result:
        result["image_verification"] = image_result

    print("\n" + "=" * 60)
    v = result["verdict"]
    print(f"VERDICT: {v['overall_verdict']}  (confidence: {v['confidence_score']}%)")
    print(f"Reasoning: {v['reasoning']}")
    print(f"To increase confidence: {v['what_would_increase_confidence']}")
    print("=" * 60)

    for pc in v.get("per_claim_verdicts", []):
        print(f"  - [{pc['verdict']} ({pc['confidence']}%)] {pc['claim']}")
    
    if image_result:
        print("\n" + "=" * 60)
        print(f"IMAGE VERIFICATION: {image_result.get('verdict', 'See details below')}")
        print(f"Path: {image_result.get('image_path')}")
        if image_result.get("reverse_search"):
            print(f"Reverse search: {image_result['reverse_search']}")
        print("=" * 60)

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\nFull result saved to {args.json_out}")


if __name__ == "__main__":
    main()
