"""Core runtime schemas shared across the harness.

On-disk task schemas live in :mod:`slm_coding_bench.tasks.manifest`; this module holds the
runtime objects (resolved task, model output, suite results, serving metrics, result records).
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field

from slm_coding_bench.tasks.manifest import SuiteName, TaskManifest

SCHEMA_VERSION = 1


class SuiteStatus(str, Enum):
    pass_ = "pass"
    fail = "fail"
    error = "error"
    timeout = "timeout"
    not_applicable = "n/a"


class GenMetrics(BaseModel):
    """Per-generation metrics for a single model call."""

    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    ttft_ms: float | None = None
    total_ms: float | None = None
    tok_per_s: float | None = None


class ServingMetrics(BaseModel):
    """Aggregate serving metrics for a (model x deployment) over a run."""

    model: str
    deployment: str
    n_calls: int = 0
    latency_ms_p50: float | None = None
    latency_ms_p95: float | None = None
    ttft_ms_p50: float | None = None
    throughput_tok_s_mean: float | None = None
    prompt_tokens_total: int = 0
    completion_tokens_total: int = 0
    peak_ram_mb: float | None = None


class Task(BaseModel):
    """A resolved task: manifest + on-disk location + loaded prompt text."""

    manifest: TaskManifest
    dir: Path
    prompt: str

    model_config = {"arbitrary_types_allowed": True}

    @property
    def id(self) -> str:
        return self.manifest.id

    @property
    def origin(self) -> str:
        return self.manifest.origin

    def applies(self, suite: SuiteName) -> bool:
        return suite in self.manifest.suites


class Candidate(BaseModel):
    """A single candidate solution produced by a solver."""

    code: str
    raw_output: str
    extraction_ok: bool
    sample_index: int = 0
    finish_reason: str | None = None
    gen_metrics: GenMetrics | None = None


class SuiteResult(BaseModel):
    """Outcome of evaluating one suite on one candidate."""

    suite: SuiteName
    status: SuiteStatus
    score: float | None = None
    detail: dict = Field(default_factory=dict)


class ResultRecord(BaseModel):
    """One row of results: a (task x model x deployment x solver x suite x sample) outcome."""

    schema_version: int = SCHEMA_VERSION
    run_id: str
    task_id: str
    origin: str
    model: str
    deployment: str
    solver: str
    suite: SuiteName
    sample_index: int
    status: SuiteStatus
    score: float | None = None
    extraction_ok: bool = True
    gen_metrics: GenMetrics | None = None
    detail: dict = Field(default_factory=dict)
    ts: datetime
