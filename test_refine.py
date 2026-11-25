import json
from pipeline.outline import generate_outline
from pipeline.draft import generate_draft
from pipeline.refine import refine_draft, get_metrics

source = open("sources/vector_databases.txt", encoding="utf-8").read()

outline = generate_outline(
    topic="How vector databases power modern AI search",
    tone="beginner",
    audience="college students new to AI",
    length="medium",
)
draft = generate_draft(outline)
refined, report = refine_draft(draft, source_text=source)

open("outputs/test_draft.md", "w", encoding="utf-8").write(draft)
open("outputs/test_refined.md", "w", encoding="utf-8").write(refined)

before, after = get_metrics(draft), get_metrics(refined)
print("=== METRICS (before -> after) ===")
for k in before:
    print(f"{k}: {before[k]} -> {after[k]}")
print("\n=== REPORT ===")
print(json.dumps(report, indent=2))
print("\n=== REFINED PREVIEW (first 1200 chars) ===\n")
print(refined[:1200])
