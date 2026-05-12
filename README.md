# Lab 24 - Full Evaluation & Guardrail System

## Overview
This project implements a full evaluation and guardrail stack for a Day 18 style RAG system. It includes automated RAGAS evaluation, LLM-as-Judge with calibration, defense-in-depth guardrails, and a production blueprint. The repo is organized by phase so each milestone can be run and validated independently. Outputs are saved as CSV/JSON/Markdown artifacts for grading and auditability.

## Setup
```powershell
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
```

Create `.env` and paste your keys (template already created):
```env
OPENAI_API_KEY=your_openai_api_key_here
GROQ_API_KEY=your_groq_api_key_here
USE_OPENAI_CALLS=1
OPENAI_CHAT_MODEL=gpt-4o-mini
```

Or set environment variables manually:
```powershell
$env:OPENAI_API_KEY="..."
# Optional for C.4 Llama Guard API
$env:GROQ_API_KEY="..."
```

## Run Order
1. Build corpus: `python scripts/build_corpus.py`
   - Mix Day18 + Wikipedia + synthetic:
     `python scripts/build_corpus.py --sources day18,wikipedia,synthetic`
   - If you only want Day18 data:
     `python scripts/build_corpus.py --sources day18`
2. Phase A: `python scripts/run_phase_a.py`
3. Phase B: `python scripts/run_phase_b.py`
4. Phase C: `python scripts/run_phase_c.py`
5. Phase D: `python scripts/run_phase_d.py`
6. Pre-submit check: `python scripts/pre_submit_check.py`

To force real API calls (instead of local fallback):
```powershell
$env:USE_OPENAI_CALLS="1"
python scripts/run_phase_a.py
python scripts/run_phase_c.py
```

To use Groq for Llama Guard path in C.4:
```powershell
$env:GROQ_API_KEY="..."
python scripts/run_phase_c.py
```

## Results Summary
### Phase A (RAGAS)
- Test set: generated in `phase-a/testset_v1.csv`
- Summary metrics: `phase-a/ragas_summary.json`
- Failure clusters: `phase-a/failure_analysis.md`

### Phase B (LLM-Judge)
- Pairwise results: `phase-b/pairwise_results.csv`
- Absolute scoring: `phase-b/absolute_scores.csv`
- Human calibration: `phase-b/human_labels.csv` + `phase-b/kappa_analysis.py`
- Bias report: `phase-b/judge_bias_report.md`

### Phase C (Guardrails)
- Input guard code/results: `phase-c/input_guard.py`, `phase-c/pii_test_results.csv`
- Adversarial testing: `phase-c/adversarial_test_results.csv`
- Output guard: `phase-c/output_guard.py`
- End-to-end benchmark: `phase-c/full_pipeline.py`, `phase-c/latency_benchmark.csv`

### Phase D (Blueprint)
- Final blueprint: `phase-d/blueprint.md`

## Cost Tracking
- Add run-level cost numbers after executions:
  - Phase A eval cost: `$TBD`
  - Phase B judge cost: `$TBD`
  - Phase C guardrail cost: `$TBD`
  - Total: `$TBD`

## Lessons Learned
Update this section after implementation and testing.

## Demo Video
Add your unlisted YouTube link here.
