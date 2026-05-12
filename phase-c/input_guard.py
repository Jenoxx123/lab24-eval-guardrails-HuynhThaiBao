from __future__ import annotations

import asyncio
import re
import time
from dataclasses import dataclass
from typing import Tuple

import numpy as np

try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_anonymizer import AnonymizerEngine
except Exception:
    AnalyzerEngine = None
    AnonymizerEngine = None

try:
    from langchain_openai import OpenAIEmbeddings
except Exception:
    OpenAIEmbeddings = None


VN_PII = {
    "cccd": r"\b\d{12}\b",
    "phone_vn": r"(?:\+84|0)\d{9,10}\b",
    "tax_code": r"\b\d{10}(?:-\d{3})?\b",
    "email": r"\b[\w.\-]+@[\w.\-]+\.\w+\b",
}


@dataclass
class TopicCheckResult:
    ok: bool
    reason: str
    score: float


class InputGuard:
    def __init__(self) -> None:
        self.analyzer = AnalyzerEngine() if AnalyzerEngine else None
        self.anonymizer = AnonymizerEngine() if AnonymizerEngine else None

    def scrub_vn(self, text: str) -> Tuple[str, bool]:
        out = text
        found = False
        for name, pattern in VN_PII.items():
            updated, count = re.subn(pattern, f"[{name.upper()}]", out)
            out = updated
            found = found or count > 0
        return out, found

    def scrub_ner(self, text: str) -> str:
        if not self.analyzer or not self.anonymizer:
            return text
        results = self.analyzer.analyze(text=text, language="en")
        return self.anonymizer.anonymize(text=text, analyzer_results=results).text

    def sanitize(self, text: str) -> tuple[str, bool, float]:
        start = time.perf_counter()
        text = text or ""
        step1, found = self.scrub_vn(text)
        step2 = self.scrub_ner(step1)
        latency_ms = (time.perf_counter() - start) * 1000
        return step2, found, latency_ms

    async def sanitize_async(self, text: str) -> tuple[str, bool, float]:
        return await asyncio.to_thread(self.sanitize, text)


class TopicGuard:
    def __init__(self, allowed_topics: list[str], threshold: float = 0.60) -> None:
        self.allowed_topics = allowed_topics
        self.threshold = threshold
        self.emb = None
        self.topic_vectors: list[list[float]] = []
        if OpenAIEmbeddings:
            try:
                self.emb = OpenAIEmbeddings()
                self.topic_vectors = [self.emb.embed_query(t) for t in allowed_topics]
            except Exception:
                self.emb = None
                self.topic_vectors = []

    def check(self, text: str) -> TopicCheckResult:
        text = (text or "").strip()
        if not text:
            return TopicCheckResult(False, "Empty input.", 0.0)
        if self.emb and self.topic_vectors:
            q = self.emb.embed_query(text)
            sims = []
            for tv in self.topic_vectors:
                denom = (np.linalg.norm(q) * np.linalg.norm(tv)) or 1.0
                sims.append(float(np.dot(q, tv) / denom))
            score = max(sims)
            best = self.allowed_topics[sims.index(score)]
            if score >= self.threshold:
                return TopicCheckResult(True, f"On-topic: {best}", score)
            return TopicCheckResult(False, f"Off-topic. Closest topic: {best} ({score:.2f})", score)

        # fallback keyword check when embeddings are unavailable
        hits = sum(1 for t in self.allowed_topics if any(k in text.lower() for k in t.lower().split()))
        score = min(1.0, hits / max(1, len(self.allowed_topics)))
        if score > 0:
            return TopicCheckResult(True, "On-topic (keyword fallback).", score)
        return TopicCheckResult(False, "Off-topic. Please ask about AI/RAG topics.", score)

    async def check_async(self, text: str) -> TopicCheckResult:
        return await asyncio.to_thread(self.check, text)


def graceful_off_topic_message() -> str:
    return (
        "Mình chỉ hỗ trợ các chủ đề AI/RAG trong phạm vi hệ thống này. "
        "Bạn có thể hỏi về retrieval, evaluation, guardrails, hoặc latency optimization."
    )
