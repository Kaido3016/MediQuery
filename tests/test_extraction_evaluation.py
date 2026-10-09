"""Regression gates for the synthetic extraction evaluation dataset."""

from evaluation.extraction.run_eval import evaluate


def test_synthetic_extraction_corpus_is_large_enough_and_labeled():
    result = evaluate()
    assert result["case_count"] >= 50
    assert result["labeled_finding_count"] >= 30
    assert "not clinical validation" in result["scope"]


def test_parser_meets_regression_threshold_on_synthetic_fixture():
    result = evaluate()
    assert result["exact_finding"]["precision"] >= 0.95, result
    assert result["exact_finding"]["recall"] >= 0.95, result
    assert result["exact_finding"]["f1"] >= 0.95, result
