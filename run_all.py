import json
import traceback
from pathlib import Path
from pipeline.run import run_pipeline

JOBS = [
    {"topic": "How vector databases power modern AI search", "tone": "beginner",
     "audience": "college students new to AI", "length": "medium", "words": None,
     "source": "sources/vector_databases.txt"},
    {"topic": "Why the Transformer architecture changed NLP", "tone": "technical",
     "audience": "ML engineers", "length": "medium", "words": 700, "source": None},
    {"topic": "How UPI changed digital payments in India", "tone": "casual",
     "audience": "general readers in India", "length": "long", "words": None,
     "source": "sources/upi.txt"},
]

rows = []
for i, j in enumerate(JOBS, 1):
    print(f"\n===== JOB {i}/{len(JOBS)}: {j['topic']} =====")
    try:
        r = run_pipeline(j["topic"], j["tone"], j["audience"], j["length"], j["words"], j["source"])
        rows.append((j, r, None))
        print("Guardrails:", "PASSED" if r["guardrails"]["passed"] else "FAILED")
    except Exception as e:
        traceback.print_exc()
        rows.append((j, None, str(e)))

lines = ["# Pipeline Run Results", ""]
for j, r, err in rows:
    lines.append(f"## {j['topic']}")
    lines.append(f"- Tone: {j['tone']} | Audience: {j['audience']} | Length setting: {'custom ' + str(j['words']) if j['words'] else j['length']}")
    if err:
        lines += [f"- ERROR: {err}", ""]
        continue
    lines.append(f"- Output file: {r['final_path']}")
    lines.append(f"- Words: {r['metrics_after']['words']} (target {r['outline']['total_words']})")
    lines.append(f"- Metrics before: {r['metrics_before']}")
    lines.append(f"- Metrics after: {r['metrics_after']}")
    lines.append(f"- Refinement report: {r['report']}")
    lines.append(f"- Length enforcement: {r['length_log'] or 'not needed'}")
    lines.append(f"- Guardrails: {'PASSED' if r['guardrails']['passed'] else 'FAILED'}")
    for c in r["guardrails"]["checks"]:
        lines.append(f"  - [{'PASS' if c['passed'] else 'FAIL'}] {c['name']}: {c['detail']}")
    lines.append("")
Path("outputs/RESULTS.md").write_text("\n".join(lines), encoding="utf-8")
print("\nSaved outputs/RESULTS.md")
