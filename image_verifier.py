"""
Image verification: reverse image search + vision analysis.
Can verify if an image is recycled, out-of-context, or misused in news.
"""
import base64
from pathlib import Path


def encode_image_to_base64(image_path: str) -> str:
    """Encode a local image file to base64."""
    with open(image_path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


def analyze_image_with_vision(image_path_or_url: str, prompt: str = None) -> dict:
    """
    Use Gemini Vision to analyze an image.
    Can describe what's in the image, detect text, estimate location, etc.
    """
    from llm import call_llm
    
    if prompt is None:
        prompt = (
            "Analyze this news image. Describe: (1) what's visible (people, places, objects), "
            "(2) any visible text or captions, (3) any metadata (dates, locations, watermarks), "
            "(4) whether it looks authentic or edited. Return as JSON with keys: "
            "description, visible_text, metadata, authenticity_notes"
        )
    
    # If it's a local file, encode to base64
    if Path(image_path_or_url).exists():
        b64_image = encode_image_to_base64(image_path_or_url)
        # Note: full vision integration would need specialized image handling in llm.py
        # For now, return a placeholder — this needs Gemini's multimodal API
        return {
            "source": "local_file",
            "path": image_path_or_url,
            "encoded": b64_image[:50] + "...",  # truncate for display
            "note": "Full vision analysis requires Gemini multimodal API setup",
        }
    else:
        # If it's a URL, pass directly
        return {
            "source": "url",
            "url": image_path_or_url,
            "note": "Vision analysis for URLs requires Gemini multimodal API setup",
        }


def search_image_reverse(image_path: str, max_results: int = 5) -> list[dict]:
    """
    Reverse image search to find where an image has been used before.
    Uses free alternatives (TinEye API, Google Lens via Selenium, etc.).
    For now, returns a placeholder — requires additional library setup.
    """
    return [
        {
            "note": "Reverse image search requires TinEye API key or Selenium setup",
            "suggestion": "Consider these services: TinEye, Google Lens, Bing Image Search",
            "image_path": image_path,
        }
    ]


def check_image_reuse(image_path: str, news_context: str) -> dict:
    """
    Check if an image appears to be recycled/reused from an older news story.
    Combines reverse search + vision analysis.
    """
    vision_result = analyze_image_with_vision(image_path)
    reverse_results = search_image_reverse(image_path)
    
    return {
        "image_path": image_path,
        "context": news_context,
        "vision_analysis": vision_result,
        "reverse_search": reverse_results,
        "verdict": "Requires full API setup (TinEye + Gemini Vision)",
    }
