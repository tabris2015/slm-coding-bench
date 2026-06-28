"""Adapter for any OpenAI-compatible chat-completions endpoint.

Covers a running ``mlx_lm.server``, ``llama-swap``, vLLM, or a cloud API. Uses streaming to
measure time-to-first-token; trusts server-reported ``usage`` when present and estimates token
counts otherwise.
"""

from __future__ import annotations

import json
import time

import httpx

from slm_coding_bench.deployments.base import DeploymentAdapter
from slm_coding_bench.models import GenMetrics


def _estimate_tokens(text: str) -> int:
    """Rough token estimate (~4 chars/token) when the server reports no usage."""
    return max(1, len(text) // 4)


class OpenAIDeployment(DeploymentAdapter):
    name = "openai_compat"

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        *,
        name: str | None = None,
        timeout_s: float = 300.0,
    ) -> None:
        super().__init__()
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        if name:
            self.name = name
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self._client = httpx.Client(timeout=timeout_s, headers=headers)

    def __exit__(self, *exc) -> None:
        self._client.close()

    def health(self) -> bool:
        try:
            r = self._client.get(f"{self.base_url}/models")
            return r.status_code == 200
        except httpx.HTTPError:
            return False

    def chat(
        self,
        *,
        model: str,
        messages: list[dict],
        temperature: float,
        max_tokens: int,
        seed: int | None = None,
        stream: bool = True,
    ) -> tuple[str, GenMetrics]:
        if stream:
            text, metrics = self._chat_stream(model, messages, temperature, max_tokens, seed)
        else:
            text, metrics = self._chat_once(model, messages, temperature, max_tokens, seed)
        self.metrics.record(model, metrics)
        return text, metrics

    def _payload(self, model, messages, temperature, max_tokens, seed, stream) -> dict:
        p = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }
        if seed is not None:
            p["seed"] = seed
        if stream:
            p["stream_options"] = {"include_usage": True}
        return p

    def _chat_stream(self, model, messages, temperature, max_tokens, seed):
        payload = self._payload(model, messages, temperature, max_tokens, seed, True)
        start = time.perf_counter()
        ttft_ms: float | None = None
        chunks: list[str] = []
        finish_reason: str | None = None
        usage: dict | None = None

        with self._client.stream("POST", f"{self.base_url}/chat/completions", json=payload) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line or not line.startswith("data:"):
                    continue
                data = line[len("data:"):].strip()
                if data == "[DONE]":
                    break
                try:
                    obj = json.loads(data)
                except json.JSONDecodeError:
                    continue
                if obj.get("usage"):
                    usage = obj["usage"]
                for choice in obj.get("choices", []):
                    delta = choice.get("delta", {})
                    piece = delta.get("content")
                    if piece:
                        if ttft_ms is None:
                            ttft_ms = (time.perf_counter() - start) * 1000.0
                        chunks.append(piece)
                    if choice.get("finish_reason"):
                        finish_reason = choice["finish_reason"]

        total_ms = (time.perf_counter() - start) * 1000.0
        text = "".join(chunks)
        return text, self._build_metrics(text, ttft_ms, total_ms, usage, finish_reason)

    def _chat_once(self, model, messages, temperature, max_tokens, seed):
        payload = self._payload(model, messages, temperature, max_tokens, seed, False)
        start = time.perf_counter()
        r = self._client.post(f"{self.base_url}/chat/completions", json=payload)
        r.raise_for_status()
        total_ms = (time.perf_counter() - start) * 1000.0
        obj = r.json()
        choice = obj.get("choices", [{}])[0]
        text = choice.get("message", {}).get("content", "") or ""
        finish_reason = choice.get("finish_reason")
        usage = obj.get("usage")
        # Non-streaming: no TTFT signal.
        return text, self._build_metrics(text, None, total_ms, usage, finish_reason)

    def _build_metrics(self, text, ttft_ms, total_ms, usage, finish_reason) -> GenMetrics:
        prompt_tokens = (usage or {}).get("prompt_tokens")
        completion_tokens = (usage or {}).get("completion_tokens")
        if completion_tokens is None:
            completion_tokens = _estimate_tokens(text)
        # End-to-end throughput (completion tokens over total wall time). Robust across both
        # plain and reasoning models; TTFT is reported separately for prefill latency. A
        # generation-phase formula (total - ttft) explodes when streamed content arrives late,
        # which is exactly the reasoning-model case.
        tok_per_s = None
        if completion_tokens and total_ms and total_ms > 0:
            tok_per_s = completion_tokens / (total_ms / 1000.0)
        return GenMetrics(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            ttft_ms=ttft_ms,
            total_ms=total_ms,
            tok_per_s=tok_per_s,
        )
