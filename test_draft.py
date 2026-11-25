import re
from pipeline.outline import generate_outline
from pipeline.draft import generate_draft

outline = generate_outline(
    topic="How vector databases power modern AI search",
    tone="beginner",
    audience="college students new to AI",
    length="medium",
)
draft = generate_draft(outline)

with open("outputs/test_draft.md", "w", encoding="utf-8") as f:
    f.write(draft)

headings = re.findall(r"^## (.+)$", draft, flags=re.M)
expected = [s["heading"] for s in outline["sections"]] + ["Conclusion"]
print("Word count:", len(draft.split()), "| target:", outline["total_words"])
print("Headings match outline:", headings == expected)
print("Headings found:", headings)
print("\n--- DRAFT PREVIEW (first 1500 chars) ---\n")
print(draft[:1500])
