import json
from pathlib import Path
from pipeline.refine import find_factual_issues, apply_corrections, _safe
from pipeline.guardrails import run_guardrails

slug = "why-the-transformer-architecture-changed-nlp"
post_path = Path(f"outputs/{slug}.md")
outline = json.loads(Path(f"outputs/{slug}_outline.json").read_text(encoding="utf-8"))
source = Path("sources/transformer_attention.txt").read_text(encoding="utf-8")
post = post_path.read_text(encoding="utf-8")

Path(f"outputs/{slug}_before_factcheck.md").write_text(post, encoding="utf-8")

issues = find_factual_issues(post, source)
print("ISSUES FOUND:", len(issues))
for i in issues:
    print("- CLAIM:", i["claim"])
    print("  FIX:  ", i["correction"])

fixed, applied = post, False
if issues:
    candidate = apply_corrections(post, issues)
    if _safe(post, candidate):
        fixed, applied = candidate, True
    else:
        print("Corrections rejected by safety check; post unchanged.")

print("\nWrong phrase 'inverse square root' still present:", "inverse square root" in fixed.lower())
g = run_guardrails(fixed, outline)
print("Guardrails:", "PASSED" if g["passed"] else "FAILED")
for c in g["checks"]:
    print(f"  [{'PASS' if c['passed'] else 'FAIL'}] {c['name']}: {c['detail']}")

post_path.write_text(fixed, encoding="utf-8")

lines = ["", "## Post-run fact-check: Transformer post (source: sources/transformer_attention.txt)",
         f"- Issues found: {len(issues)}", f"- Corrections applied: {applied}"]
for i in issues:
    lines.append(f"  - CLAIM: {i['claim']} -> FIX: {i['correction']}")
lines.append(f"- Guardrails after fix: {'PASSED' if g['passed'] else 'FAILED'}")
with open("outputs/RESULTS.md", "a", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
