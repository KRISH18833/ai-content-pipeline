from pathlib import Path

p = Path("outputs/why-the-transformer-architecture-changed-nlp.md")
text = p.read_text(encoding="utf-8")

old = "Dividing this product by the inverse square root of the key dimensionality $\\sqrt{d_k}$ stabilizes variance"
new = "Dividing this product by $\\sqrt{d_k}$, the square root of the key dimensionality, stabilizes variance"

assert text.count(old) == 1, "expected exactly one occurrence"
p.write_text(text.replace(old, new), encoding="utf-8")

with open("outputs/RESULTS.md", "a", encoding="utf-8") as f:
    f.write(
        "\n## Known limitation: LLM fact-checker miss\n"
        "- The automated fact-check (source: sources/transformer_attention.txt) found 0 issues, "
        "but the Transformer post said scores are divided by the 'inverse square root' of d_k, "
        "which is wrong (the correct operation is dividing by sqrt(d_k)).\n"
        "- This was caught during manual review and fixed by hand. "
        "The fact-checker reliably catches blatant contradictions (3/3 planted errors in test_factcheck.py) "
        "but can miss subtle technical wording errors, so human review is still required before publishing.\n"
    )
