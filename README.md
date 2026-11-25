# AI Content Pipeline

Multi-step LLM pipeline that turns a topic into a publishable blog post: outline → draft → refine, with configurable length and tone, quality guardrails, and 3 full sample outputs.

## Pipeline

```
topic + tone + audience + length
        │
        ▼
[1] OUTLINE   JSON outline (title, hook, sections, key points, word budget), validated + retried
        │
        ▼
[2] DRAFT     intro, then each section written from its key points (with the previous text for flow), then conclusion
        │
        ▼
[3] REFINE    edit pass (repetition, sentence openers, filler, transitions) + optional fact-check against a source file
        │
        ▼
[4] GUARDRAILS  length enforcement (whole-post edit, then per-section trim fallback) + 4 quality checks
        │
        ▼
    outputs/<topic-slug>.md
```

## Setup

```
python -m venv venv
venv\Scripts\activate          # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env         # macOS/Linux: cp .env.example .env
```

Put your Gemini API key in `.env`. Model: `gemini-3.5-flash-lite` (set in `pipeline/config.py`).

## Usage

```
python main.py --topic "How UPI changed digital payments in India" --tone casual --audience "general readers in India" --length long --source sources/upi.txt
```

| Option | Values | Default |
|---|---|---|
| `--topic` | any text (required) | |
| `--tone` | beginner, technical, casual, professional | casual |
| `--audience` | any text | general readers |
| `--length` | short (600), medium (1000), long (1500) words | medium |
| `--words` | custom word target, overrides `--length` | |
| `--source` | .txt file used to fact-check the draft | |

Run all 3 sample topics: `python run_all.py` (writes `outputs/RESULTS.md`).

## Guardrails

| Check | Rule |
|---|---|
| length_in_range | 80% to 125% of the target word count |
| draft_not_outline_copy | at least 1.5x the outline's length and at most 30% of key points copied verbatim |
| structure_ok | one title, expected number of sections, 2+ paragraphs per body section, no 200+ word paragraphs |
| low_repetition | under 2% repeated 4-grams |

`test_guardrails.py` proves they work: a pasted outline fails the copy check (12/12 key points copied, 0.7x expansion), and short or oversized text fails the length check.

## Sample outputs (all 3 posts included)

| Topic | Tone / audience | Length | Result | Post |
|---|---|---|---|---|
| How vector databases power modern AI search | beginner / college students new to AI | medium, 1084 words (target 1000) | guardrails passed | [read](outputs/how-vector-databases-power-modern-ai-search.md) |
| Why the Transformer architecture changed NLP | technical / ML engineers | custom 700, 736 words | guardrails passed | [read](outputs/why-the-transformer-architecture-changed-nlp.md) |
| How UPI changed digital payments in India | casual / general readers in India | long, 1600 words (target 1500) | guardrails passed | [read](outputs/how-upi-changed-digital-payments-in-india.md) |

Per-run metrics (before/after refinement) are in [outputs/RESULTS.md](outputs/RESULTS.md). Intermediate outputs (`*_outline.json`, `*_draft.md`) are saved next to each final post.

## Does refinement measurably help?

- Repeated sentence openers: 13.95% to 6.0% (vector post), 20.37% to 6.38% in an earlier test run
- Repeated 4-grams: 0.61% to 0% in the earlier test run
- Fact-check test (`test_factcheck.py`): 3 of 3 deliberately planted errors were found and corrected from the source (keyword-matching claim, "HNSW is perfectly exact", "PostgreSQL cannot store vectors")

## Honest evaluation

Where it works:
- Structure is consistent: all 3 posts follow their outlines, with clear headings and short paragraphs.
- Tone and audience visibly change the output: analogies for beginners, math and hardware detail for engineers, humor for the casual UPI post.
- The fact-checker reliably catches blatant contradictions against a source.

Where it falls short:
- The fact-checker missed a subtle error. The Transformer post said scores are divided by the "inverse square root" of d_k (correct: divided by sqrt(d_k)). The checker found 0 issues; I caught it in manual review and fixed it by hand (see `fix_transformer_post.py` and RESULTS.md). It only checks claims against the source I provide, so anything outside the source goes unverified (e.g. the UPI post's claims about offline payments and countries).
- Length enforcement can pad. Expanding the vector post from 717 to 1084 words added generic filler in the final sections.
- The refinement safety check rejected the UPI post's flow edit (heading or length changed), so that post shipped unrefined.
- The repetition metric measures phrases, not ideas. The UPI post reuses the same chai/squinting jokes many times.
- Output depends on the model, and the pipeline needed a model change midway because of availability and quota.

Human review is still required before publishing.

## Project structure

```
ai-content-pipeline/
├── pipeline/ (config.py, llm.py, outline.py, draft.py, refine.py, guardrails.py, run.py)
├── sources/  (fact-check source files)
├── outputs/  (3 final posts, outlines, drafts, RESULTS.md)
├── main.py, run_all.py
└── test_*.py, factcheck_post.py, fix_transformer_post.py
```
