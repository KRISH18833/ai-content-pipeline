import re
import json
from collections import Counter
from pipeline.llm import call_llm

FILLER = [
    "game-changing", "in today's", "it's important to note", "it is important to note",
    "delve", "in conclusion", "at the end of the day", "superpower", "unlock the power",
    "ever-evolving", "in the realm of", "mind-reading",
]

EDITOR_SYSTEM = (
    "You are a meticulous senior editor. You improve writing without changing its meaning, "
    "structure, or facts. Output only what is asked, nothing else."
)


def _body(text: str) -> str:
    return "\n".join(l for l in text.splitlines() if not l.startswith("#"))


def get_metrics(text: str) -> dict:
    body = _body(text)
    words = re.findall(r"[a-z0-9']+", body.lower())
    grams = list(zip(*[words[i:] for i in range(4)]))
    counts = Counter(grams)
    repeated_grams = sum(c - 1 for c in counts.values() if c > 1)
    rep_pct = round(repeated_grams / max(len(grams), 1) * 100, 2)

    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", body) if len(s.split()) > 2]
    openers = Counter(" ".join(s.lower().split()[:2]) for s in sentences)
    repeated_openers = sum(c - 1 for c in openers.values() if c > 1)
    opener_pct = round(repeated_openers / max(len(sentences), 1) * 100, 2)

    low = body.lower()
    filler = sum(low.count(f) for f in FILLER)

    return {
        "words": len(text.split()),
        "repeated_4gram_pct": rep_pct,
        "repeated_sentence_openers_pct": opener_pct,
        "filler_phrases": filler,
    }


def _headings(text: str) -> list:
    return re.findall(r"^#{1,3} .+$", text, flags=re.M)


def _safe(original: str, candidate: str, tol: float = 0.2) -> bool:
    if _headings(original) != _headings(candidate):
        return False
    o, c = len(original.split()), len(candidate.split())
    return (1 - tol) * o <= c <= (1 + tol) * o


def improve_flow(draft: str) -> str:
    n = len(draft.split())
    prompt = f"""Edit the blog post below.

Do:
- Remove repeated ideas, repeated phrases, and sentences that say the same thing twice.
- Vary sentence openings so consecutive sentences do not start the same way.
- Add smooth transitions between paragraphs and between sections.
- Replace clichés and filler (for example: game-changing, superpower, in today's world) with specific wording.

Do NOT:
- Change, add, remove, or reorder any heading. Keep every "#" and "##" line exactly as written.
- Add new facts or new sections.
- Change the tone or audience level.
- Change the length by more than 10 percent (currently about {n} words).

Return the full edited post in markdown, nothing else.

POST:
{draft}"""
    return call_llm(prompt, system=EDITOR_SYSTEM, temperature=0.4)


def find_factual_issues(draft: str, source: str) -> list:
    prompt = f"""Fact-check the blog post against the SOURCE.

Flag only statements in the post that are CONTRADICTED by the source or are specific technical claims (names, numbers, algorithms, how something works) that the source does not support and that are likely wrong.
Do NOT flag analogies, metaphors, examples used to explain, or opinions.
If everything is consistent, return an empty list.

Return ONLY JSON in this shape:
{{"issues": [{{"claim": "exact text from the post", "problem": "why it is wrong or unsupported", "correction": "corrected wording based on the source"}}]}}

SOURCE:
{source}

POST:
{draft}"""
    raw = call_llm(prompt, system="You are a strict fact-checker. Return only valid JSON.", temperature=0.0, json_mode=True)
    try:
        return json.loads(raw).get("issues", [])
    except json.JSONDecodeError:
        return []


def apply_corrections(draft: str, issues: list) -> str:
    listing = "\n".join(f"- CLAIM: {i['claim']}\n  FIX: {i['correction']}" for i in issues)
    n = len(draft.split())
    prompt = f"""Apply ONLY the listed corrections to the blog post. Change as little text as possible.
Keep every heading exactly as written, keep the tone, and keep the length near {n} words.
Return the full corrected post in markdown, nothing else.

CORRECTIONS:
{listing}

POST:
{draft}"""
    return call_llm(prompt, system=EDITOR_SYSTEM, temperature=0.2)


def refine_draft(draft: str, source_text: str = "") -> tuple:
    report = {"flow_applied": False, "factcheck_applied": False, "issues": [], "warnings": []}
    current = draft

    edited = improve_flow(current)
    if _safe(current, edited):
        current = edited
        report["flow_applied"] = True
    else:
        report["warnings"].append("Flow edit rejected (headings or length changed); kept original draft.")

    if source_text.strip():
        issues = find_factual_issues(current, source_text)
        report["issues"] = issues
        if issues:
            fixed = apply_corrections(current, issues)
            if _safe(current, fixed):
                current = fixed
                report["factcheck_applied"] = True
            else:
                report["warnings"].append("Fact-check corrections rejected (headings or length changed).")

    return current, report
