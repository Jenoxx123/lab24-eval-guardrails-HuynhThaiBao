from __future__ import annotations

import os
import time
from dataclasses import dataclass

import requests

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


@dataclass
class SafetyDecision:
    is_safe: bool
    reason: str
    latency_ms: float


class OutputGuard:
    """
    Unified interface:
    check(user_input, answer) -> (is_safe, reason, latency_ms)
    """

    def __init__(self, use_groq: bool | None = None) -> None:
        groq_key = os.getenv("GROQ_API_KEY", "").strip()
        self.use_groq = bool(groq_key) if use_groq is None else use_groq
        self.groq_key = groq_key
        self.openai_client = OpenAI() if OpenAI else None

    def _groq_llama_guard(self, user_input: str, answer: str) -> SafetyDecision:
        url = "https://api.groq.com/openai/v1/chat/completions"
        payload = {
            "model": "llama-guard-3-8b",
            "messages": [
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": answer},
            ],
            "temperature": 0,
        }
        headers = {"Authorization": f"Bearer {self.groq_key}"}
        start = time.perf_counter()
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        latency_ms = (time.perf_counter() - start) * 1000
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"]
        lower = text.lower()
        is_safe = ("safe" in lower) and ("unsafe" not in lower)
        return SafetyDecision(is_safe, text, latency_ms)

    def _openai_fallback(self, user_input: str, answer: str) -> SafetyDecision:
        heur_block = any(
            k in answer.lower()
            for k in ["attack", "bomb", "malware", "self-harm", "phishing", "hate", "exploit", "ransomware"]
        )
        if not self.openai_client or os.getenv("USE_OPENAI_CALLS", "0") != "1":
            return SafetyDecision(not heur_block, "Heuristic fallback moderation.", 0.0)
        try:
            start = time.perf_counter()
            joined = f"User: {user_input}\nAssistant: {answer}"
            res = self.openai_client.moderations.create(model="omni-moderation-latest", input=joined)
            latency_ms = (time.perf_counter() - start) * 1000
            flagged = bool(res.results[0].flagged)
            reason = "Flagged by OpenAI moderation." if flagged else "Allowed by OpenAI moderation."
            return SafetyDecision(not flagged, reason, latency_ms)
        except Exception:
            return SafetyDecision(not heur_block, "Heuristic fallback after API failure.", 0.0)

    def check(self, user_input: str, answer: str) -> tuple[bool, str, float]:
        if self.use_groq and self.groq_key:
            try:
                decision = self._groq_llama_guard(user_input, answer)
                return decision.is_safe, decision.reason, decision.latency_ms
            except Exception as exc:
                # fallback automatically to OpenAI moderation
                fallback = self._openai_fallback(user_input, answer)
                return fallback.is_safe, f"Groq fallback: {exc}. {fallback.reason}", fallback.latency_ms
        try:
            decision = self._openai_fallback(user_input, answer)
            return decision.is_safe, decision.reason, decision.latency_ms
        except Exception as exc:
            return False, f"Safety check failed: {exc}", 0.0
