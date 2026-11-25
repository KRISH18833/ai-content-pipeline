import re
from pipeline import config
from pipeline.llm import call_llm
from pipeline.refine import get_metrics, _headings

ADJUST_SYSTEM = (
    "You are a meticulous senior editor. Output only the full edited post in markdown, nothing else."
)


def _body(text: str) -> str:
    return "\n".join(l for l in text.splitlines() if not l.startswith("#"))


def _outline_text(outline: dict) -> str:
    parts = [outline["title"], outline["hook"], outline["conclusion_point"]]
    for s in outline["sections"]:
        parts.append(s["heading"])
        parts += s["key_points"]
    return " ".join(parts)


def _range(target: int) -> tuple:
    return int(target * config.MIN_WORD_RATIO), int(target * config.MAX_WORD_RATIO)


def check_length(text: str, target: int) -> dict:
    n = len(text.split())
    lo, hi = _range(target)
    return {"name": "length_in_range", "passed": lo <= n <= hi, "detail": f"{n} words (allowed {lo}-{hi})"}


def check_not_outline_copy(text: str, outline: dict) -> dict:
    body = _body(text).lower()
    expansion = round(len(body.split()) / max(len(_outline_text(outline).split()), 1), 2)
    points = [p.lower().strip(" .") for s in outline["sections"] for p in s["key_points"]]
    verbatim = sum(1 for p in points if p and p in body)
    passed = expansion >= 1.5 and verbatim <= 0.3 * len(points)
    return {"name": "draft_not_outline_copy", "passed": passed,
            "detail": f"expansion {expansion}x outline, {verbatim}/{len(points)} key points copied verbatim"}


def check_structure(text: str, outline: dict) -> dict:
    lines = text.splitlines()
    h1 = [l for l in lines if l.startswith("# ")]
    h2_names = re.findall(r"^## (.+)$", text, flags=re.M)
    expected_h2 = len(outline["sections"]) + 1
    chunks = re.split(r"^## .+$", text, flags=re.M)[1:]
    paras = [[p for p in c.strip().split("\n\n") if p.strip()] for c in chunks]
    # the final section (Conclusion) is intentionally one paragraph, so only body sections need 2+
    thin = [h2_names[i] for i, p in enumerate(paras[:-1]) if len(p) < 2]
    wall = sum(1 for p in paras for x in p if len(x.split()) > 200)
    passed = len(h1) == 1 and len(h2_names) == expected_h2 and not thin and wall == 0
    return {"name": "structure_ok", "passed": passed,
            "detail": f"{len(h1)} title, {len(h2_names)}/{expected_h2} sections, thin body sections: {thin or 'none'}, {wall} wall-of-text paragraphs"}


def check_repetition(text: str) -> dict:
    pct = get_metrics(text)["repeated_4gram_pct"]
    return {"name": "low_repetition", "passed": pct < 2.0, "detail": f"{pct}% repeated 4-grams (limit 2.0)"}


def run_guardrails(text: str, outline: dict) -> dict:
    checks = [
        check_length(text, outline["total_words"]),
        check_not_outline_copy(text, outline),
        check_structure(text, outline),
        check_repetition(text),
    ]
    return {"passed": all(c["passed"] for c in checks), "checks": checks}


def trim_by_section(text: str, target: int) -> str:
    parts = re.split(r"(?m)^(?=## )", text)
    head, sections = parts[0], parts[1:]
    head_words = len(head.split())
    total = len(text.split())
    ratio = max(target - head_words, 50) / max(total - head_words, 1)
    out = [head.rstrip() + "\n\n"]
    for sec in sections:
        first, _, body = sec.partition("\n")
        body = body.strip()
        goal = max(40, int(len(body.split()) * ratio))
        prompt = f"""Rewrite this section body to about {goal} words (it is currently {len(body.split())}).
Keep the key ideas and the tone. Use 2 paragraphs if {goal} is 100 or more, otherwise 1 to 2 short paragraphs.
Do NOT include a heading. Return only the rewritten body.

BODY:
{body}"""
        new_body = call_llm(prompt, system=ADJUST_SYSTEM, temperature=0.3)
        out.append(f"{first}\n\n{new_body.strip()}\n\n")
    return "".join(out)


def enforce_length(text: str, target: int, max_attempts: int = 3) -> tuple:
    log = []
    current = text
    for attempt in range(1, max_attempts + 1):
        n = len(current.split())
        if abs(n - target) <= 0.15 * target:
            break
        delta = abs(n - target)
        if n > target:
            action = f"Cut about {delta} words by removing the least important sentences and tightening wording."
        else:
            action = f"Add about {delta} words by adding concrete examples and explanation to the thinnest body sections."
        prompt = f"""Edit the blog post below. {action}
Current length: {n} words. The result must be about {target} words (between {int(target*0.9)} and {int(target*1.1)}).
Keep every heading ("#" and "##" lines) exactly as written, keep every section, keep body sections at 2 or more paragraphs, keep the tone and audience level, add no new sections.

POST:
{current}"""
        candidate = call_llm(prompt, system=ADJUST_SYSTEM, temperature=0.3)
        ok_headings = _headings(candidate) == _headings(current)
        closer = abs(len(candidate.split()) - target) < abs(n - target)
        log.append(f"attempt {attempt}: {n} -> {len(candidate.split())} words, headings_ok={ok_headings}, closer={closer}")
        if ok_headings and closer:
            current = candidate

    n = len(current.split())
    if n > int(target * config.MAX_WORD_RATIO):
        trimmed = trim_by_section(current, target)
        ok_headings = _headings(trimmed) == _headings(current)
        closer = abs(len(trimmed.split()) - target) < abs(n - target)
        log.append(f"section-trim fallback: {n} -> {len(trimmed.split())} words, headings_ok={ok_headings}, closer={closer}")
        if ok_headings and closer:
            current = trimmed
    return current, log
