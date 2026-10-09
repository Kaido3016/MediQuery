"""Evaluate the synthetic extraction regression corpus, not clinical accuracy."""

import json
from pathlib import Path

from src.services.report_analysis import _parse_page_findings

DATASET = Path(__file__).with_name("golden.json")
FIELDS = ("name", "value", "unit", "reference_range", "flag", "page")


def _identity(item: dict[str, object] | object) -> tuple[str, str, str | None]:
    if isinstance(item, dict):
        return (str(item["name"]).casefold(), str(item["value"]), item["unit"])
    return (item.name.casefold(), item.value, item.unit)


def _full_finding(item: dict[str, object] | object) -> tuple[object, ...]:
    if isinstance(item, dict):
        return tuple(item[field] for field in FIELDS)
    return tuple(getattr(item, field) for field in FIELDS)


def _metrics(tp: int, fp: int, fn: int) -> dict[str, float]:
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-12)
    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def evaluate() -> dict[str, object]:
    dataset = json.loads(DATASET.read_text(encoding="utf-8"))
    detection_tp = detection_fp = detection_fn = 0
    exact_tp = exact_fp = exact_fn = 0
    field_correct = field_total = 0
    per_case = []

    for case in dataset["cases"]:
        predicted, _ = _parse_page_findings(case["text"], 1)
        expected = case["expected"]
        expected_by_id = {_identity(item): item for item in expected}
        predicted_by_id = {_identity(item): item for item in predicted}
        matched_ids = expected_by_id.keys() & predicted_by_id.keys()

        detection_tp += len(matched_ids)
        detection_fp += len(predicted_by_id.keys() - expected_by_id.keys())
        detection_fn += len(expected_by_id.keys() - predicted_by_id.keys())

        expected_full = {_full_finding(item) for item in expected}
        predicted_full = {_full_finding(item) for item in predicted}
        case_exact_tp = len(expected_full & predicted_full)
        case_exact_fp = len(predicted_full - expected_full)
        case_exact_fn = len(expected_full - predicted_full)
        exact_tp += case_exact_tp
        exact_fp += case_exact_fp
        exact_fn += case_exact_fn

        for identity in matched_ids:
            expected_item = expected_by_id[identity]
            predicted_item = predicted_by_id[identity]
            for field in FIELDS:
                field_total += 1
                if getattr(predicted_item, field) == expected_item[field]:
                    field_correct += 1

        per_case.append(
            {
                "id": case["id"],
                "detection_tp": len(matched_ids),
                "detection_fp": len(predicted_by_id.keys() - expected_by_id.keys()),
                "detection_fn": len(expected_by_id.keys() - predicted_by_id.keys()),
                "exact_tp": case_exact_tp,
                "exact_fp": case_exact_fp,
                "exact_fn": case_exact_fn,
            }
        )

    return {
        "dataset_version": dataset["dataset_version"],
        "scope": "synthetic parser regression only; not clinical validation",
        "case_count": len(dataset["cases"]),
        "labeled_finding_count": sum(
            len(case["expected"]) for case in dataset["cases"]
        ),
        "exact_finding": {
            "true_positive": exact_tp,
            "false_positive": exact_fp,
            "false_negative": exact_fn,
            **_metrics(exact_tp, exact_fp, exact_fn),
        },
        "candidate_detection": {
            "true_positive": detection_tp,
            "false_positive": detection_fp,
            "false_negative": detection_fn,
            **_metrics(detection_tp, detection_fp, detection_fn),
        },
        "matched_finding_field_accuracy": round(field_correct / max(field_total, 1), 4),
        "per_case": per_case,
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2))
