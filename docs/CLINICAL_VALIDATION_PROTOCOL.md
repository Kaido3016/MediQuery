# Clinical validation protocol — extraction feature

**Status: protocol draft only; no independent clinical validation has been performed.** Current evaluation data are synthetic software-regression fixtures, not a clinical benchmark.

## Intended use to be approved before data collection

Proposed limited intended use: extract candidate laboratory names, values, units, reference ranges, flags, page numbers, and source evidence from supported text-based PDF reports so users can compare candidates with the original report. No diagnosis, triage, treatment, or clinical recommendation is intended.

A qualified clinical lead must approve this intended-use statement, target populations, supported laboratory/report formats, excluded cases, and acceptable error criteria before study execution.

## Dataset governance

- Use legally authorized, appropriately de-identified or synthetic documents; never commit PHI or raw clinical documents to this repository or CI.
- Include multiple laboratories, vendors, layout families, units, languages, page counts, reference-range styles, OCR/scanned cases if supported, malformed files, and ambiguous table structures.
- Split train/development/test sets by source institution/template and time where possible to reduce leakage.
- Have two independent qualified annotators label each target field and page/evidence span; adjudicate disagreements and document inter-rater agreement.
- Freeze parser version, dataset manifest, inclusion/exclusion rules, and analysis plan before the final test run.

## Metrics and error analysis

Report per-field exact-match precision, recall, F1, false-positive rate, missed-value rate, unit preservation, reference-range association, flag agreement, page/evidence correctness, and abstention/attention-note behavior. Include confidence intervals, subgroup/template breakdowns, and error examples that contain no identifying information.

Predefine risk-weighted acceptance thresholds with the clinical lead. Any systematic unit/range mismatch, unsupported value extraction, or false confident presentation should block release until corrected and independently retested.

## Human factors and release

- Test whether users understand that findings are candidates and must be verified against the original document.
- Verify evidence can be traced to the correct source page.
- Establish a correction/complaint pathway and monitor post-release extraction errors.
- Independently review safety, privacy, regulatory status, and whether the intended use changes as features are added.

The current 50-case synthetic corpus can catch regressions in deterministic parsing but cannot establish clinical validity or performance on real-world reports. OCR and clinical AI/RAG remain out of scope until separately implemented and evaluated.
