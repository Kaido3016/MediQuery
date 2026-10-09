# Extraction evaluation

Run from the repository root:

```bash
python -m evaluation.extraction.run_eval
python -m pytest -q tests/test_extraction_evaluation.py
```

The checked-in golden set has 50 synthetic cases: supported structured values and
negative/non-lab lines. Metrics include exact finding precision/recall/F1 and
field-level accuracy for name, value, unit, reference range, flag, and page.

**Interpretation limit:** this is a deterministic regression fixture, not a clinical
benchmark and not an estimate of performance on real patient PDFs. It cannot
validate OCR, layout diversity, language diversity, unit conversion, reference-range
association across vendor templates, or clinical correctness. Before making any
real-world accuracy claim, obtain a legally reviewed, de-identified, representative
and independently double-labeled corpus, pre-register inclusion/exclusion criteria,
split by source/template to avoid leakage, report confidence intervals and
per-field error categories, and have a qualified clinical reviewer adjudicate
high-risk errors. Do not put PHI into this repository or CI artifacts.
