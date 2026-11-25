import json
import re
from pathlib import Path
from pipeline.outline import generate_outline
from pipeline.draft import generate_draft
from pipeline.refine import refine_draft, get_metrics


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


def run_pipeline(topic, tone="casual", audience="general readers", length="medium",
                 words=None, source_path=None, out_dir="outputs") -> dict:
    out = Path(out_dir)
    out.mkdir(exist_ok=True)
    slug = slugify(topic)

    source_text = ""
    if source_path:
        source_text = Path(source_path).read_text(encoding="utf-8")

    print("[1/3] Generating outline...")
    outline = generate_outline(topic, tone, audience, length, words)
    (out / f"{slug}_outline.json").write_text(json.dumps(outline, indent=2), encoding="utf-8")

    print("[2/3] Writing draft...")
    draft = generate_draft(outline)
    (out / f"{slug}_draft.md").write_text(draft, encoding="utf-8")

    print("[3/3] Refining...")
    final, report = refine_draft(draft, source_text=source_text)
    final_path = out / f"{slug}.md"
    final_path.write_text(final, encoding="utf-8")

    result = {
        "slug": slug,
        "outline": outline,
        "draft": draft,
        "final": final,
        "report": report,
        "metrics_before": get_metrics(draft),
        "metrics_after": get_metrics(final),
        "final_path": str(final_path),
    }
    return result
