"""Deterministic evaluation for the labeled synthetic extraction regression corpus.

This score measures parser behavior on constructed fixtures only. It must never be
reported as clinical accuracy or performance on real-world patient reports.
"""
import json
from pathlib import Path

from src.services.report_analysis import _parse_page_findings

DATASET = Path(__file__).with_name("golden.json")


def evaluate() -> dict[str, object]:
    dataset = json.loads(DATASET.read_text(encoding="utf-8"))
    true_positive = false_positive = false_negative = 0
    field_correct = field_total = 0
    per_case = []
    for case in dataset["cases"]:
        predicted, _ = _parse_page_findings(case["text"], 1)
        expected = case["expected"]
        expected_by_key = {
            (item["name"].casefold(), item["value"], item["unit"]): item
            for item in expected
        }
        predicted_by_key = {
            (item.name.casefold(), item.value, item.unit): item
            for item in predicted
        }
        matched = set(expected_by_key) & set(predicted_by_key)
        tp = len(matched)
        fp = len(predicted_by_key.keys() - expected_by_key.keys())
        fn = len(expected_by_key.keys() - predicted_by_key.keys())
        true_positive += tp
        false_positive += fp
        false_negative += fn
        fields = ("name", "value", "unit", "reference_range", "flag", "page")
        for key in matched:
            expected_item = expected_by_key[key]
            predicted_item = predicted_by_key[key]
            for field in fields:
                field_total += 1
                if getattr(predicted_item, field) == expected_item[field]:
                    field_correct += 1
        per_case.append({"id": case["id"], "tp": tp, "fp": fp, "fn": fn})
    precision = true_positive / max(true_positive + false_positive, 1)
    recall = true_positive / max(true_positive + false_negative, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-12)
    return {
        "dataset_version": dataset["dataset_version"],
        "scope": "synthetic parser regression only; not clinical validation",
        "case_count": len(dataset["cases"]),
        "labeled_finding_count": sum(len(case["expected"]) for case in dataset["cases"]),
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "matched_finding_field_accuracy": round(field_correct / max(field_total, 1), 4),
        "per_case": per_case,
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2))
