# Failure Cluster Analysis

## Bottom 10 Questions

| # | Question | Type | F | AR | CP | CR | Avg | Cluster |
|---|---|---|---:|---:|---:|---:|---:|---|
| 1 | Tóm tắt ý chính của đoạn sau: Artificial Intelligence

Source: https:/... | simple | 0.03 | 0.03 | 0.05 | 0.05 | 0.04 | C1 |
| 2 | Tóm tắt ý chính của đoạn sau: Artificial Intelligence

Source: https:/... | simple | 0.03 | 0.03 | 0.05 | 0.05 | 0.04 | C1 |
| 3 | Tóm tắt ý chính của đoạn sau: Artificial Intelligence

Source: https:/... | simple | 0.03 | 0.03 | 0.05 | 0.05 | 0.04 | C1 |
| 4 | Tóm tắt ý chính của đoạn sau: Artificial Intelligence

Source: https:/... | simple | 0.03 | 0.03 | 0.05 | 0.05 | 0.04 | C1 |
| 5 | Tóm tắt ý chính của đoạn sau: Artificial Intelligence

Source: https:/... | simple | 0.03 | 0.03 | 0.05 | 0.05 | 0.04 | C1 |
| 6 | Tóm tắt ý chính của đoạn sau: Artificial Intelligence

Source: https:/... | simple | 0.04 | 0.03 | 0.05 | 0.05 | 0.04 | C1 |
| 7 | Tóm tắt ý chính của đoạn sau: Artificial Intelligence

Source: https:/... | simple | 0.04 | 0.03 | 0.05 | 0.05 | 0.04 | C1 |
| 8 | Tóm tắt ý chính của đoạn sau: Artificial Intelligence

Source: https:/... | simple | 0.04 | 0.03 | 0.05 | 0.05 | 0.04 | C1 |
| 9 | Tóm tắt ý chính của đoạn sau: Artificial Intelligence

Source: https:/... | simple | 0.04 | 0.03 | 0.05 | 0.05 | 0.04 | C1 |
| 10 | Tóm tắt ý chính của đoạn sau: Artificial Intelligence

Source: https:/... | simple | 0.04 | 0.03 | 0.05 | 0.05 | 0.04 | C1 |

## Clusters Identified

### Cluster C1: Multi-hop/context recall failures
- Pattern: thiếu bằng chứng đầy đủ cho câu hỏi cần tổng hợp nhiều phần.
- Root cause: `top_k` retrieval còn thấp hoặc chunking chưa tối ưu.
- Proposed fix: tăng `top_k` (3 -> 5), thêm re-ranker, hybrid retrieval.

### Cluster C2: Off-topic retrieval/context precision failures
- Pattern: context trả về chưa sát câu hỏi.
- Root cause: embedding mismatch hoặc query rewriting yếu.
- Proposed fix: query rewrite + metadata filtering + rerank threshold.

### Cluster C3: Answer style/relevancy failures
- Pattern: answer dài hoặc lan man.
- Root cause: prompt generation chưa ép concise + grounded.
- Proposed fix: strict response format + citation-required prompt.