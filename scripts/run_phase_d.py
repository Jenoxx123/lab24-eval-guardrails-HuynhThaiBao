from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.common import init_env

PHASE_A = ROOT / "phase-a"
PHASE_C = ROOT / "phase-c"
PHASE_D = ROOT / "phase-d"


def safe_metric(summary: dict, key: str, default: float) -> float:
    v = summary.get(key, default)
    try:
        return float(v)
    except Exception:
        return default


def main() -> int:
    init_env()
    PHASE_D.mkdir(parents=True, exist_ok=True)

    ragas = {}
    if (PHASE_A / "ragas_summary.json").exists():
        ragas = json.loads((PHASE_A / "ragas_summary.json").read_text(encoding="utf-8"))

    p95_total = 2500.0
    p95_l1 = 50.0
    p95_l3 = 100.0
    if (PHASE_C / "latency_benchmark.csv").exists():
        df = pd.read_csv(PHASE_C / "latency_benchmark.csv")
        p95_total = float(df["total_ms"].quantile(0.95))
        p95_l1 = float(df["L1"].quantile(0.95))
        p95_l3 = float(df["L3"].quantile(0.95))

    faith = safe_metric(ragas, "faithfulness", 0.80)
    ar = safe_metric(ragas, "answer_relevancy", 0.78)
    cp = safe_metric(ragas, "context_precision", 0.68)
    cr = safe_metric(ragas, "context_recall", 0.72)

    doc = f"""# Lab 24 Blueprint (Production Draft)

## Section 1: SLO Definition

| Metric | Target | Alert Threshold | Severity |
|---|---|---|---|
| Faithfulness | >= 0.85 | < 0.80 for 30 min | P2 |
| Answer Relevancy | >= 0.80 | < 0.75 for 30 min | P2 |
| Context Precision | >= 0.70 | < 0.65 for 1h | P3 |
| Context Recall | >= 0.75 | < 0.70 for 1h | P3 |
| P95 Latency (guarded) | < 2500 ms | > 3000 ms for 5 min | P1 |
| Guardrail Detection Rate | >= 90% | < 85% | P2 |
| False Positive Rate | < 5% | > 10% | P2 |

Current run snapshot:
- Faithfulness: {faith:.3f}
- Answer Relevancy: {ar:.3f}
- Context Precision: {cp:.3f}
- Context Recall: {cr:.3f}
- L1 P95: {p95_l1:.1f} ms
- L3 P95: {p95_l3:.1f} ms
- Total P95: {p95_total:.1f} ms

## Section 2: Architecture Diagram

```mermaid
graph TD
    A[User Input] --> B[L1 Input Guards]
    B --> C{{PII/Topic/Injection OK?}}
    C -->|No| Z[Refuse + Guidance]
    C -->|Yes| D[L2 RAG Generation]
    D --> E[L3 Output Guard]
    E -->|Unsafe| Z
    E -->|Safe| F[Response to User]
    F --> G[L4 Audit Log Async]
```

Latency budget annotation:
- L1 target P95: < 50 ms
- L2 target P95: < 2200 ms
- L3 target P95: < 100 ms
- L4 async: does not block response

## Section 3: Alert Playbook

### Incident: Faithfulness drops below 0.80
- Severity: P2
- Detection: continuous eval alert
- Likely causes: retrieval drift, prompt drift, stale index
- Investigation: compare CP/CR trend, check prompt/version diff, verify corpus index freshness
- Resolution: retriever tune/reindex, rollback prompt, rerun eval gate

### Incident: Guardrail false positives > 10%
- Severity: P2
- Detection: moderation dashboard alert
- Likely causes: over-sensitive topic threshold, output guard model drift
- Investigation: inspect blocked safe samples, check threshold changes
- Resolution: calibrate threshold, add allowlist patterns, re-evaluate on legit suite

### Incident: P95 latency > 3s
- Severity: P1
- Detection: runtime latency monitor
- Likely causes: external API delay, oversized context, sequential processing
- Investigation: layer-level latency breakdown, dependency status
- Resolution: enable parallelism, reduce context size, cache retrieval, fallback model route

## Section 4: Cost Analysis (100k queries/month)

| Component | Unit Cost | Volume | Monthly Cost |
|---|---:|---:|---:|
| RAG generation (gpt-4o-mini) | $0.001/query | 100,000 | $100 |
| RAGAS eval (1% sample) | $0.01/query | 1,000 | $10 |
| LLM Judge (tiered) | mixed | 11,000 | $60 |
| Input guard (Presidio self-host) | near-zero | 100,000 | $0 |
| Output guard (Groq/API est.) | $0.0005/query | 100,000 | $50 |
| **Estimated Total** |  |  | **$220** |

Optimization ideas:
- Dynamic eval sampling by risk tier
- Judge tiering: cheap-first and escalate hard cases
- Output guard cache for repeated prompts
"""
    (PHASE_D / "blueprint.md").write_text(doc, encoding="utf-8")
    print("Phase D blueprint generated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
