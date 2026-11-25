import json
from pipeline.guardrails import check_length, check_not_outline_copy, run_guardrails, enforce_length

outline = json.load(open("outputs/why-the-transformer-architecture-changed-nlp_outline.json", encoding="utf-8"))
text = open("outputs/why-the-transformer-architecture-changed-nlp.md", encoding="utf-8").read()

print("TEST 1: outline pasted as the draft must FAIL the copy check")
fake = "# " + outline["title"] + "\n\n" + "\n\n".join(
    f"## {s['heading']}\n\n" + " ".join(s["key_points"]) for s in outline["sections"])
print(check_not_outline_copy(fake, outline))

print("\nTEST 2: too-short text must FAIL the length check")
print(check_length("# Title\n\n" + "word " * 100, 700))

print("\nTEST 3: a 1000-word text with target 700 must FAIL length")
print(check_length("# T\n\n" + "word " * 1000, 700))

print("\nTEST 4: enforce_length must bring it into range")
fixed, log = enforce_length(text, 700)
print(log)
print("New word count:", len(fixed.split()))
print(run_guardrails(fixed, outline))
