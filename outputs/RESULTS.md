# Pipeline Run Results

## How vector databases power modern AI search
- Tone: beginner | Audience: college students new to AI | Length setting: medium
- Output file: outputs\how-vector-databases-power-modern-ai-search.md
- Words: 1084 (target 1000)
- Metrics before: {'words': 790, 'repeated_4gram_pct': 0.14, 'repeated_sentence_openers_pct': 13.95, 'filler_phrases': 0}
- Metrics after: {'words': 1084, 'repeated_4gram_pct': 0.19, 'repeated_sentence_openers_pct': 6.0, 'filler_phrases': 0}
- Refinement report: {'flow_applied': True, 'factcheck_applied': True, 'issues': [{'claim': 'Spotify, for instance, uses this exact technology to recommend new songs that share a similar mood and vibe with your current favorites.', 'problem': 'The source text does not mention Spotify or music recommendations.', 'correction': 'Remove claims about specific companies not mentioned in the source.'}], 'warnings': []}
- Length enforcement: ['attempt 1: 717 -> 1084 words, headings_ok=True, closer=True']
- Guardrails: PASSED
  - [PASS] length_in_range: 1084 words (allowed 800-1250)
  - [PASS] draft_not_outline_copy: expansion 3.59x outline, 1/15 key points copied verbatim
  - [PASS] structure_ok: 1 title, 6/6 sections, thin body sections: none, 0 wall-of-text paragraphs
  - [PASS] low_repetition: 0.19% repeated 4-grams (limit 2.0)

## Why the Transformer architecture changed NLP
- Tone: technical | Audience: ML engineers | Length setting: custom 700
- Output file: outputs\why-the-transformer-architecture-changed-nlp.md
- Words: 736 (target 700)
- Metrics before: {'words': 557, 'repeated_4gram_pct': 0.0, 'repeated_sentence_openers_pct': 0.0, 'filler_phrases': 0}
- Metrics after: {'words': 736, 'repeated_4gram_pct': 0.0, 'repeated_sentence_openers_pct': 3.57, 'filler_phrases': 0}
- Refinement report: {'flow_applied': True, 'factcheck_applied': False, 'issues': [], 'warnings': []}
- Length enforcement: ['attempt 1: 540 -> 736 words, headings_ok=True, closer=True']
- Guardrails: PASSED
  - [PASS] length_in_range: 736 words (allowed 560-875)
  - [PASS] draft_not_outline_copy: expansion 2.93x outline, 0/12 key points copied verbatim
  - [PASS] structure_ok: 1 title, 5/5 sections, thin body sections: none, 0 wall-of-text paragraphs
  - [PASS] low_repetition: 0.0% repeated 4-grams (limit 2.0)

## How UPI changed digital payments in India
- Tone: casual | Audience: general readers in India | Length setting: long
- Output file: outputs\how-upi-changed-digital-payments-in-india.md
- Words: 1600 (target 1500)
- Metrics before: {'words': 1600, 'repeated_4gram_pct': 0.19, 'repeated_sentence_openers_pct': 5.26, 'filler_phrases': 0}
- Metrics after: {'words': 1600, 'repeated_4gram_pct': 0.19, 'repeated_sentence_openers_pct': 5.26, 'filler_phrases': 0}
- Refinement report: {'flow_applied': False, 'factcheck_applied': False, 'issues': [], 'warnings': ['Flow edit rejected (headings or length changed); kept original draft.']}
- Length enforcement: not needed
- Guardrails: PASSED
  - [PASS] length_in_range: 1600 words (allowed 1200-1875)
  - [PASS] draft_not_outline_copy: expansion 3.71x outline, 0/24 key points copied verbatim
  - [PASS] structure_ok: 1 title, 9/9 sections, thin body sections: none, 0 wall-of-text paragraphs
  - [PASS] low_repetition: 0.19% repeated 4-grams (limit 2.0)

## Post-run fact-check: Transformer post (source: sources/transformer_attention.txt)
- Issues found: 0
- Corrections applied: False
- Guardrails after fix: PASSED
