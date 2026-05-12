from __future__ import annotations

import json
import os
import random
import re
import sys
from pathlib import Path

import pandas as pd
from sklearn.metrics import cohen_kappa_score

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.common import ensure_dirs, init_env, write_csv  # noqa: E402


PHASE_A = ROOT / "phase-a"
PHASE_B = ROOT / "phase-b"


def parse_json_or_tie(text: str) -> dict:
    try:
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception:
        return {"winner": "tie", "reason": "parse_error"}


def _tokens(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-zA-Z0-9_]+", str(s).lower()) if len(w) > 2}


def lexical_score(question: str, answer: str, ground_truth: str) -> float:
    q = _tokens(question)
    a = _tokens(answer)
    g = _tokens(ground_truth)
    qa = len(q & a) / (len(q | a) or 1)
    ga = len(g & a) / (len(g | a) or 1)
    conc = 1.0 if len(answer) < 800 else 0.6
    return (qa + ga + conc) / 3


def judge_pair(question: str, answer_a: str, answer_b: str, ground_truth: str) -> tuple[str, str]:
    sa = lexical_score(question, answer_a, ground_truth)
    sb = lexical_score(question, answer_b, ground_truth)
    if abs(sa - sb) < 0.03:
        return "tie", f"close scores ({sa:.2f} vs {sb:.2f})"
    return ("A", f"A better ({sa:.2f}>{sb:.2f})") if sa > sb else ("B", f"B better ({sb:.2f}>{sa:.2f})")


def pairwise_with_swap(question: str, ans1: str, ans2: str, ground_truth: str):
    run1_winner, run1_reason = judge_pair(question, ans1, ans2, ground_truth)
    run2_winner_raw, run2_reason = judge_pair(question, ans2, ans1, ground_truth)
    # flip result due to swap
    if run2_winner_raw == "A":
        run2_winner = "B"
    elif run2_winner_raw == "B":
        run2_winner = "A"
    else:
        run2_winner = "tie"

    final = run1_winner if run1_winner == run2_winner else "tie"
    reason = f"run1={run1_reason}; run2={run2_reason}"
    return final, run1_winner, run2_winner, reason


def absolute_score(question: str, answer: str, ground_truth: str) -> dict:
    rel = lexical_score(question, answer, question)
    acc = lexical_score(question, answer, ground_truth)
    conc = 5 if len(answer) < 500 else (4 if len(answer) < 1000 else 3)
    helpf = 4 if len(answer) > 80 else 3
    acc_i = max(1, min(5, round(acc * 5)))
    rel_i = max(1, min(5, round(rel * 5)))
    overall = round((acc_i + rel_i + conc + helpf) / 4, 2)
    return {
        "accuracy": acc_i,
        "relevance": rel_i,
        "conciseness": conc,
        "helpfulness": helpf,
        "overall": overall,
    }


def build_answer_b(base_answer: str, ground_truth: str, idx: int) -> str:
    # second version to compare against baseline answer A
    if idx % 3 == 0:
        return f"{ground_truth[:220]} [version B improved grounding]"
    if len(base_answer) < 120:
        return f"{base_answer} Câu trả lời nhấn mạnh căn cứ từ context."
    return base_answer[: max(80, int(len(base_answer) * 0.75))]


def main() -> int:
    init_env()
    ensure_dirs([str(PHASE_B)])
    src = PHASE_A / "ragas_results.csv"
    if not src.exists():
        print("Missing phase-a/ragas_results.csv. Run Phase A first.")
        return 1

    df = pd.read_csv(src)
    df = df.head(30).copy()
    if len(df) < 30:
        print("Need at least 30 rows from Phase A.")
        return 1

    pairwise_rows = []
    abs_rows = []
    for i, row in df.iterrows():
        q = str(row["question"])
        gt = str(row["ground_truth"])
        ans_a = str(row["answer"])
        ans_b = build_answer_b(ans_a, gt, i + 1)
        winner, run1, run2, reason = pairwise_with_swap(q, ans_a, ans_b, gt)
        pairwise_rows.append(
            {
                "question_id": i + 1,
                "question": q,
                "answer_a": ans_a,
                "answer_b": ans_b,
                "run1_winner": run1,
                "run2_winner": run2,
                "winner_after_swap": winner,
                "reason": reason,
            }
        )
        abs_s = absolute_score(q, ans_a, gt)
        abs_rows.append({"question_id": i + 1, "question": q, "answer": ans_a, **abs_s})

    write_csv(
        str(PHASE_B / "pairwise_results.csv"),
        pairwise_rows,
        [
            "question_id",
            "question",
            "answer_a",
            "answer_b",
            "run1_winner",
            "run2_winner",
            "winner_after_swap",
            "reason",
        ],
    )
    write_csv(
        str(PHASE_B / "absolute_scores.csv"),
        abs_rows,
        ["question_id", "question", "answer", "accuracy", "relevance", "conciseness", "helpfulness", "overall"],
    )

    # Create human labels starter file (10 rows)
    sample = pd.DataFrame(pairwise_rows).sample(10, random_state=42).sort_values("question_id")
    human_rows = []
    for j, (_, r) in enumerate(sample.iterrows()):
        # initialize with judge prediction and perturb lightly to avoid single-label edge case
        winner = r["winner_after_swap"]
        if j % 5 == 0:
            winner = "tie" if winner != "tie" else "A"
        human_rows.append(
            {
                "question_id": int(r["question_id"]),
                "human_winner": winner,
                "confidence": "medium",
                "notes": "Auto-init; please manually validate.",
            }
        )
    write_csv(str(PHASE_B / "human_labels.csv"), human_rows, ["question_id", "human_winner", "confidence", "notes"])

    # quick kappa preview from initialized labels
    pairwise_df = pd.read_csv(PHASE_B / "pairwise_results.csv").set_index("question_id")
    human_df = pd.read_csv(PHASE_B / "human_labels.csv").set_index("question_id")
    common = human_df.index.intersection(pairwise_df.index)
    human = human_df.loc[common, "human_winner"].tolist()
    judge = pairwise_df.loc[common, "winner_after_swap"].tolist()
    kappa = cohen_kappa_score(human, judge)

    # Bias report
    pw = pd.read_csv(PHASE_B / "pairwise_results.csv")
    run1_a_win_rate = float((pw["run1_winner"] == "A").mean())
    pw["len_a"] = pw["answer_a"].astype(str).str.len()
    pw["len_b"] = pw["answer_b"].astype(str).str.len()
    longer_b = pw["len_b"] > pw["len_a"]
    b_win_when_longer = int(((pw["winner_after_swap"] == "B") & longer_b).sum())
    b_longer_total = int(longer_b.sum()) or 1
    length_bias_rate = b_win_when_longer / b_longer_total

    report = [
        "# Judge Bias Report",
        "",
        "## Bias 1: Position bias",
        f"- A wins when listed first (run1): {run1_a_win_rate:.1%}",
        "- Rule of thumb: >55% may indicate position bias.",
        "",
        "## Bias 2: Length bias",
        f"- B wins when B is longer: {b_win_when_longer}/{b_longer_total} ({length_bias_rate:.1%})",
        "",
        "## Quick table",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| run1 A-win rate | {run1_a_win_rate:.3f} |",
        f"| B-win when longer | {length_bias_rate:.3f} |",
        f"| initialized kappa | {kappa:.3f} |",
        "",
        "## Mitigation",
        "- Keep swap-and-average.",
        "- Add style normalization prompt and max token budget.",
        "- Recalibrate with 20-50 human labels.",
    ]
    (PHASE_B / "judge_bias_report.md").write_text("\n".join(report), encoding="utf-8")

    print("Phase B artifacts generated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
