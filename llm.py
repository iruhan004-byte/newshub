"""
Unified LLM call wrapper.
Tries Groq -> Gemini -> OpenRouter, in that order, so the pipeline keeps
working even if one provider is rate-limited or its key is missing.
"""
import json
import config


def _call_groq(system, prompt):
    from groq import Groq
    client = Groq(api_key=config.GROQ_API_KEY)
    resp = client.chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content


def _call_gemini(system, prompt):
    import google.generativeai as genai
    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel(config.GEMINI_MODEL, system_instruction=system)
    resp = model.generate_content(prompt)
    return resp.text


def _call_openrouter(system, prompt):
    import requests
    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {config.OPENROUTER_API_KEY}"},
        json={
            "model": config.OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        },
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def call_llm(prompt: str, system: str = "You are a careful, neutral analyst.") -> str:
    """Try each configured provider in order; raise if all fail."""
    providers = []
    if config.GROQ_API_KEY:
        providers.append(("groq", _call_groq))
    if config.GEMINI_API_KEY:
        providers.append(("gemini", _call_gemini))
    if config.OPENROUTER_API_KEY:
        providers.append(("openrouter", _call_openrouter))

    if not providers:
        raise RuntimeError(
            "No LLM API key found. Set GROQ_API_KEY, GEMINI_API_KEY or "
            "OPENROUTER_API_KEY in your environment."
        )

    last_err = None
    for name, fn in providers:
        try:
            return fn(system, prompt)
        except Exception as e:  # noqa: BLE001
            last_err = e
            print(f"[llm] {name} failed: {e}. Trying next provider...")
    raise RuntimeError(f"All LLM providers failed. Last error: {last_err}")


def call_llm_json(prompt: str, system: str = "You are a careful, neutral analyst.") -> dict:
    """Call the LLM and force-parse JSON output (strips markdown fences if present)."""
    raw = call_llm(prompt + "\n\nRespond with ONLY valid JSON, no markdown fences, no commentary.", system)
    cleaned = raw.strip().strip("`")
    if cleaned.lower().startswith("json"):
        cleaned = cleaned[4:].strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # last-resort: find the first {...} block
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start != -1 and end != -1:
            return json.loads(cleaned[start:end + 1])
        raise
