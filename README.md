# News Verifier — Multi-Agent Fact-Checking Pipeline

Checks whether a piece of news appears genuine by extracting its factual
claims and cross-referencing them against live web search, trusted-outlet
lists, and (optionally) the Google Fact Check Tools database.

Built as an extension of the Planner / Researcher / Synthesizer / Critic
pattern.

## ⚠️ Important limitation, read first
No automated system can certify a news item as "100% genuine." This pipeline
gives a **calibrated confidence score with reasoning**, the same way
professional fact-checkers (Reuters, AFP) operate — never an absolute
guarantee. Treat the output as strong supporting evidence for your own
judgment, not a final ruling.

## Architecture

```
News text
   │
   ▼
[Planner]  → extracts 2-6 discrete, checkable claims
   │
   ▼
[Researcher] → per claim: web search + domain credibility check
              + Google Fact Check DB lookup
   │
   ▼
[Synthesizer] → neutral written summary of evidence per claim
   │
   ▼
[Critic] → weighs everything → confidence score + verdict + reasoning
```

## Setup

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in at least one LLM provider key
(tried in this order: Groq → Gemini → OpenRouter). `config.py` loads `.env`
automatically via `python-dotenv` — no manual `export` needed.

```bash
cp .env.example .env
# then edit .env and paste in your key(s)
```

If you'd rather not use a `.env` file, plain shell exports also work:

```bash
export GROQ_API_KEY="..."
```

## Usage

### Text verification (news article/claim)

```bash
python main.py "Some news claim or article text to check..."

# or from a file:
python main.py --file article.txt

# save full structured output:
python main.py --file article.txt --json-out result.json
```

### Image verification

```bash
# Check if an image has been recycled or used out-of-context
python main.py "news text here" --image path/to/image.jpg

# With both text and image:
python main.py "news text" --image photo.png --json-out result.json
```

Image verification checks:
- Reverse image search (finds where the image was originally published)
- Vision analysis (describes content, detects edited/synthetic elements)
- Context mismatch (image used with unrelated news)

## Extending it (matches what you were already doing in the research pipeline)

- **Search backend**: `utils/search.py` uses free DuckDuckGo search (`ddgs`).
  Swap in SearXNG or Brave the same way you did before if you hit rate limits.
- **Trusted domains**: edit `config.py` → `TRUSTED_BD` / `TRUSTED_INTL` /
  `KNOWN_UNRELIABLE` — worth adding more Bangladeshi outlets and known
  fake-news domains as you encounter them.
- **Image/video verification**: not included yet. A natural next module:
  reverse image search (e.g. via a SerpAPI Google Lens endpoint) to catch
  recycled/out-of-context photos — a very common tactic in BD misinformation.
- **Bengali input**: the LLM prompts work fine with Bengali news text as-is;
  no translation step needed since Groq/Gemini/OpenRouter models handle
  Bengali natively. If search recall on Bengali queries is weak, try adding
  an English-translated `search_query` alongside the Bengali claim in
  `planner.py`.
- **Full image verification**: Currently the `--image` flag accepts image paths
  but needs:
  - **TinEye API key**: For reverse image search (detects recycled images)
  - **Gemini Vision multimodal API**: For detailed image content analysis
  - Both are optional add-ons; text verification works without them.
- **Deploy**: same Gradio + Hugging Face Spaces route you used for the
  research pipeline would work well here for sharing with classmates.

### Implementing Full Image Support

**TinEye reverse image search:**
```bash
pip install tineyeapi
```
Then get a free API key from https://tineye.com/api and add to .env:
```env
TINEYE_API_KEY=your_key_here
```

**Gemini Vision (for image content analysis):**
Gemini models with vision already work — just pass images directly to the LLM.
