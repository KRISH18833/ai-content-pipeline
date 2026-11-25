import json
from pipeline import config
from pipeline.llm import call_llm

SYSTEM = (
    "You are an expert content strategist. You design clear, logical blog post outlines. "
    "You return ONLY valid JSON, nothing else."
)


def _build_prompt(topic: str, tone: str, audience: str, total_words: int, n_sections: int) -> str:
    return f"""Create a blog post outline.

Topic: {topic}
Audience: {audience}
Tone: {config.TONES[tone]}
Target length: about {total_words} words
Number of body sections: {n_sections}

Return JSON in exactly this shape:
{{
  "title": "compelling, specific blog title",
  "hook": "one sentence describing how the intro grabs the reader",
  "sections": [
    {{
      "heading": "clear section heading",
      "key_points": ["specific point 1", "specific point 2", "specific point 3"]
    }}
  ],
  "conclusion_point": "the single takeaway the reader leaves with"
}}

Rules:
- Exactly {n_sections} sections, in a logical order that builds understanding.
- Each section has 3 to 4 concrete, specific key points (no vague filler like "overview").
- Headings must be distinct and not repeat each other.
- No markdown, no commentary, JSON only."""


def _validate(data: dict, n_sections: int) -> None:
    for key in ("title", "hook", "sections", "conclusion_point"):
        if key not in data:
            raise ValueError(f"missing key: {key}")
    secs = data["sections"]
    if not isinstance(secs, list) or len(secs) != n_sections:
        raise ValueError(f"expected {n_sections} sections, got {len(secs) if isinstance(secs, list) else 'invalid'}")
    for s in secs:
        if not s.get("heading") or not isinstance(s.get("key_points"), list) or len(s["key_points"]) < 2:
            raise ValueError("section missing heading or key_points")


def generate_outline(topic: str, tone: str = "casual", audience: str = "general readers", length: str = "medium", words: int = None) -> dict:
    total_words = words or config.LENGTHS[length]
    n_sections = max(3, min(8, round(total_words / 200)))
    prompt = _build_prompt(topic, tone, audience, total_words, n_sections)

    last_err = None
    for _ in range(config.MAX_RETRIES):
        raw = call_llm(prompt, system=SYSTEM, temperature=0.6, json_mode=True)
        try:
            data = json.loads(raw)
            _validate(data, n_sections)
            break
        except (json.JSONDecodeError, ValueError) as e:
            last_err = e
    else:
        raise RuntimeError(f"Outline generation failed validation: {last_err}")

    # word budget: ~12% intro, ~8% conclusion, rest split across sections
    body_words = int(total_words * 0.80)
    per_section = body_words // n_sections
    for s in data["sections"]:
        s["target_words"] = per_section
    data["intro_words"] = int(total_words * 0.12)
    data["conclusion_words"] = int(total_words * 0.08)
    data["topic"] = topic
    data["tone"] = tone
    data["audience"] = audience
    data["length"] = "custom" if words else length
    data["total_words"] = total_words
    return data
