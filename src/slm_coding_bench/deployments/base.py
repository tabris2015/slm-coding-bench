"""Deployment adapter interface and per-call metric accumulation.

A deployment adapter is the harness's view of a way to serve models: it points at an
OpenAI-compatible endpoint, optionally manages the server process, makes chat calls, and
aggregates serving metrics per model.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict

from slm_coding_bench.models import GenMetrics, ServingMetrics
from slm_coding_bench.util.stats import percentile


class MetricsAccumulator:
    """Collects per-call :class:`GenMetrics` and produces aggregate :class:`ServingMetrics`."""

    def __init__(self) -> None:
        self._by_model: dict[str, list[GenMetrics]] = defaultdict(list)
        self._peak_ram_mb: dict[str, float] = {}

    def record(self, model: str, m: GenMetrics) -> None:
        self._by_model[model].append(m)

    def set_peak_ram(self, model: str, mb: float | None) -> None:
        if mb is not None:
            self._peak_ram_mb[model] = max(self._peak_ram_mb.get(model, 0.0), mb)

    def aggregate(self, model: str, deployment: str) -> ServingMetrics:
        return self._aggregate(self._by_model.get(model, []), model, deployment)

    def aggregate_combined(self, models: list[str], label: str, deployment: str) -> ServingMetrics:
        """Merge the calls of several models into one row (for roster/multi-agent solvers)."""
        calls: list[GenMetrics] = []
        for m in models:
            calls.extend(self._by_model.get(m, []))
        sm = self._aggregate(calls, label, deployment)
        sm.peak_ram_mb = max((self._peak_ram_mb[m] for m in models if m in self._peak_ram_mb),
                             default=None)
        return sm

    def _aggregate(self, calls: list[GenMetrics], model: str, deployment: str) -> ServingMetrics:
        latencies = [m.total_ms for m in calls if m.total_ms is not None]
        ttfts = [m.ttft_ms for m in calls if m.ttft_ms is not None]
        tps = [m.tok_per_s for m in calls if m.tok_per_s is not None]
        return ServingMetrics(
            model=model,
            deployment=deployment,
            n_calls=len(calls),
            latency_ms_p50=percentile(latencies, 50),
            latency_ms_p95=percentile(latencies, 95),
            ttft_ms_p50=percentile(ttfts, 50),
            throughput_tok_s_mean=(sum(tps) / len(tps)) if tps else None,
            prompt_tokens_total=sum(m.prompt_tokens or 0 for m in calls),
            completion_tokens_total=sum(m.completion_tokens or 0 for m in calls),
            peak_ram_mb=self._peak_ram_mb.get(model),
        )


class DeploymentAdapter(ABC):
    """Base class for deployment adapters. Use as a context manager."""

    name: str = "base"

    def __init__(self) -> None:
        self.metrics = MetricsAccumulator()

    def __enter__(self) -> DeploymentAdapter:
        return self

    def __exit__(self, *exc) -> None:
        return None

    @abstractmethod
    def chat(
        self,
        *,
        model: str,
        messages: list[dict],
        temperature: float,
        max_tokens: int,
        seed: int | None = None,
        stream: bool = True,
    ) -> tuple[str, GenMetrics]:  # pragma: no cover - interface
        ...

    @abstractmethod
    def health(self) -> bool:  # pragma: no cover - interface
        ...

    def serving_metrics(self, model: str) -> ServingMetrics:
        return self.metrics.aggregate(model, self.name)

    def combined_serving_metrics(self, models: list[str], label: str) -> ServingMetrics:
        return self.metrics.aggregate_combined(models, label, self.name)
