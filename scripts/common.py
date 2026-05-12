from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
from dotenv import load_dotenv


def init_env() -> None:
    """
    Load environment variables from .env in project root.
    Safe to call multiple times.
    """
    load_dotenv(dotenv_path=Path(".env"), override=False)


def ensure_dirs(paths: Sequence[str]) -> None:
    for p in paths:
        Path(p).mkdir(parents=True, exist_ok=True)


def write_json(path: str, payload: dict) -> None:
    Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def write_csv(path: str, rows: list[dict], fieldnames: Sequence[str]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def percentile(values: Iterable[float], p: float) -> float:
    arr = np.array(list(values), dtype=float)
    if arr.size == 0:
        return 0.0
    return float(np.percentile(arr, p))
