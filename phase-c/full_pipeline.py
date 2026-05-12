from __future__ import annotations

import asyncio
import importlib.util
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_input_mod = _load_module("input_guard", Path(__file__).with_name("input_guard.py"))
_output_mod = _load_module("output_guard", Path(__file__).with_name("output_guard.py"))
InputGuard = _input_mod.InputGuard
TopicGuard = _input_mod.TopicGuard
graceful_off_topic_message = _input_mod.graceful_off_topic_message
OutputGuard = _output_mod.OutputGuard


def _refuse_response() -> str:
    return "Xin lỗi, mình không thể hỗ trợ yêu cầu này."


@dataclass
class PipelineResult:
    answer: str
    timings: dict[str, float]
    blocked: bool
    reason: str


class GuardedPipeline:
    def __init__(self, allowed_topics: list[str]) -> None:
        self.input_guard = InputGuard()
        self.topic_guard = TopicGuard(allowed_topics=allowed_topics, threshold=0.60)
        self.output_guard = OutputGuard()
        self.openai_client = OpenAI() if OpenAI else None

    async def rag_pipeline_async(self, query: str) -> str:
        if not self.openai_client or os.getenv("USE_OPENAI_CALLS", "0") != "1":
            # offline fallback
            return f"[Fallback answer] {query[:180]}"

        def _call() -> str:
            model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
            prompt = (
                "You are a concise AI/RAG assistant. Answer in Vietnamese, factual and short.\n"
                f"Question: {query}"
            )
            try:
                out = self.openai_client.responses.create(
                    model=model,
                    input=prompt,
                    temperature=0.2,
                )
                return out.output_text.strip()
            except Exception:
                return f"[Fallback answer] {query[:180]}"

        return await asyncio.to_thread(_call)

    async def audit_log(self, event: dict[str, Any]) -> None:
        # Replace with LangSmith/Langfuse integration if needed.
        _ = event
        await asyncio.sleep(0)

    async def guarded_pipeline(self, user_input: str) -> PipelineResult:
        timings: dict[str, float] = {}

        t0 = time.perf_counter()
        pii_task = asyncio.create_task(self.input_guard.sanitize_async(user_input))
        topic_task = asyncio.create_task(self.topic_guard.check_async(user_input))
        sanitized, _, _ = await pii_task
        topic = await topic_task
        timings["L1"] = (time.perf_counter() - t0) * 1000

        if not topic.ok:
            return PipelineResult(graceful_off_topic_message(), timings, True, topic.reason)

        t0 = time.perf_counter()
        answer = await self.rag_pipeline_async(sanitized)
        timings["L2"] = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        safe, reason, _ = await asyncio.to_thread(self.output_guard.check, sanitized, answer)
        timings["L3"] = (time.perf_counter() - t0) * 1000
        if not safe:
            return PipelineResult(_refuse_response(), timings, True, reason)

        t0 = time.perf_counter()
        asyncio.create_task(self.audit_log({"user_input": user_input, "answer": answer, "timings": timings}))
        timings["L4"] = (time.perf_counter() - t0) * 1000
        return PipelineResult(answer, timings, False, "OK")
