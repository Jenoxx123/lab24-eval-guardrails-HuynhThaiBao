from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.metrics import cohen_kappa_score


def interpret(kappa: float) -> str:
    if kappa < 0:
        return "Worse than chance - judge is unreliable."
    if kappa < 0.2:
        return "Slight agreement - not reliable."
    if kappa < 0.4:
        return "Fair agreement - still weak."
    if kappa < 0.6:
        return "Moderate agreement - usable for monitoring only."
    if kappa < 0.8:
        return "Substantial agreement - production-ready."
    return "Almost perfect agreement."


def main() -> int:
    root = Path(__file__).resolve().parent
    pairwise = pd.read_csv(root / "pairwise_results.csv").set_index("question_id")
    human = pd.read_csv(root / "human_labels.csv").set_index("question_id")

    common = pairwise.index.intersection(human.index)
    if len(common) == 0:
        print("No overlapping question_id.")
        return 1

    judge_labels = pairwise.loc[common, "winner_after_swap"].tolist()
    human_labels = human.loc[common, "human_winner"].tolist()
    kappa = cohen_kappa_score(human_labels, judge_labels)
    print(f"Cohen's kappa: {kappa:.3f}")
    print(interpret(kappa))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

