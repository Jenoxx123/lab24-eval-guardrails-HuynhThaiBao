from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def run(cmd: list[str]) -> None:
    print(f"\n>>> {' '.join(cmd)}")
    subprocess.run(cmd, cwd=ROOT, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--docs-dir", default="docs", help="Corpus directory used by Phase A.")
    parser.add_argument("--sources", default="day18,wikipedia,synthetic", help="Corpus sources for build_corpus.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run(
        [
            sys.executable,
            "scripts/build_corpus.py",
            "--output-dir",
            args.docs_dir,
            "--sources",
            args.sources,
        ]
    )
    run([sys.executable, "scripts/run_phase_a.py", "--docs-dir", args.docs_dir])
    run([sys.executable, "scripts/run_phase_b.py"])
    run([sys.executable, "scripts/run_phase_c.py"])
    run([sys.executable, "scripts/run_phase_d.py"])
    run([sys.executable, "scripts/pre_submit_check.py"])
    print("\nAll phases completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
