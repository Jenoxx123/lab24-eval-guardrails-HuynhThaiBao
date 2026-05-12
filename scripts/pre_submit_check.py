from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent.parent


REQUIRED = [
    "README.md",
    "requirements.txt",
    "prompts.md",
    "phase-a/testset_v1.csv",
    "phase-a/testset_review_notes.md",
    "phase-a/ragas_results.csv",
    "phase-a/ragas_summary.json",
    "phase-a/failure_analysis.md",
    "phase-b/pairwise_results.csv",
    "phase-b/absolute_scores.csv",
    "phase-b/human_labels.csv",
    "phase-b/kappa_analysis.py",
    "phase-b/judge_bias_report.md",
    "phase-c/input_guard.py",
    "phase-c/output_guard.py",
    "phase-c/full_pipeline.py",
    "phase-c/pii_test_results.csv",
    "phase-c/adversarial_test_results.csv",
    "phase-c/latency_benchmark.csv",
    "phase-d/blueprint.md",
    ".github/workflows/eval-gate.yml",
]


def main() -> int:
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    if missing:
        print("Missing required files:")
        for m in missing:
            print(f"- {m}")
        return 1

    # Quick quality checks
    testset = pd.read_csv(ROOT / "phase-a/testset_v1.csv")
    if len(testset) < 50:
        print("testset_v1.csv has < 50 rows.")
        return 1
    required_cols = {"question", "ground_truth", "contexts", "evolution_type"}
    if not required_cols.issubset(set(testset.columns)):
        print("testset_v1.csv missing required columns.")
        return 1

    pairwise = pd.read_csv(ROOT / "phase-b/pairwise_results.csv")
    if len(pairwise) < 30:
        print("pairwise_results.csv has < 30 rows.")
        return 1

    print("Pre-submit check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

