from pipeline import config
from pipeline.llm import call_llm

SYSTEM = (
    "You are an experienced blog writer. You write clear, engaging, well-structured prose in "
    "well-formed paragraphs of 3 to 5 sentences. You never use filler, never repeat earlier points, "
    "and never add headings unless told to. Output plain markdown text only."
)


def _style(outline: dict) -> str:
    return (
        f"Audience: {outline['audience']}\n"
        f"Tone: {config.TONES[outline['tone']]}\n"
        f"Blog title: {outline['title']}"
    )


def _write_intro(outline: dict) -> str:
    headings = ", ".join(s["heading"] for s in outline["sections"])
    prompt = f"""{_style(outline)}

Write the INTRODUCTION of this blog post in about {outline['intro_words']} words.
Hook idea: {outline['hook']}
The post will cover: {headings}

Rules:
- 1 to 2 paragraphs.
- Open with the hook, state what the reader will learn, do NOT summarize every section.
- Do NOT include any heading or the title."""
    return call_llm(prompt, system=SYSTEM, temperature=0.7)


def _write_section(outline: dict, section: dict, previous_text: str) -> str:
    points = "\n".join(f"- {p}" for p in section["key_points"])
    prev = previous_text[-700:] if previous_text else "(this is the first section after the intro)"
    tw = section["target_words"]
    if tw < 150:
        para_rule = "Exactly 2 short paragraphs of 2 to 3 sentences each."
    else:
        para_rule = "2 to 3 paragraphs of 3 to 5 sentences each."
    prompt = f"""{_style(outline)}

Write the body of ONE section in about {tw} words. HARD LIMIT: do not exceed {int(tw * 1.1)} words.
Section heading (do NOT print it): {section['heading']}
Cover these key points, in order:
{points}

For flow, here is the end of the text written so far. Continue naturally from it without repeating it:
\"\"\"{prev}\"\"\"

Rules:
- {para_rule}
- Cover every key point briefly with a concrete example or explanation.
- Do NOT repeat ideas already used earlier in the post.
- Do NOT include the heading, bullet lists, or a conclusion."""
    return call_llm(prompt, system=SYSTEM, temperature=0.7)


def _write_conclusion(outline: dict, previous_text: str) -> str:
    prompt = f"""{_style(outline)}

Write the CONCLUSION in about {outline['conclusion_words']} words.
Core takeaway: {outline['conclusion_point']}

End of the post so far, for context:
\"\"\"{previous_text[-600:]}\"\"\"

Rules:
- 1 paragraph, end with a clear takeaway or next step for the reader.
- Do NOT introduce new ideas, do NOT include a heading, do NOT copy sentences from above."""
    return call_llm(prompt, system=SYSTEM, temperature=0.7)


def generate_draft(outline: dict) -> str:
    parts = [f"# {outline['title']}", "", _write_intro(outline), ""]
    running = parts[2]
    for section in outline["sections"]:
        body = _write_section(outline, section, running)
        parts += [f"## {section['heading']}", "", body, ""]
        running += "\n\n" + body
    conclusion = _write_conclusion(outline, running)
    parts += ["## Conclusion", "", conclusion, ""]
    return "\n".join(parts)
