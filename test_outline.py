import json
from pipeline.outline import generate_outline

outline = generate_outline(
    topic="How vector databases power modern AI search",
    tone="beginner",
    audience="college students new to AI",
    length="medium",
)
print(json.dumps(outline, indent=2))
