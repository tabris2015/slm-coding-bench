"""Run configuration: a YAML run spec (source of truth) with CLI overlay support."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class DeploymentConfig(BaseModel):
    kind: str = "openai_compat"  # "openai_compat" | "mlx_server"
    name: str
    base_url: str | None = None
    api_key_env: str | None = None
    models: list[str] = Field(default_factory=list)
    # mlx_server-only (launch a local process); unused for openai_compat.
    launch: bool = False
    host: str | None = None
    port: int | None = None


class ExecutorConfig(BaseModel):
    kind: str = "subprocess"
    test_timeout_s: float = 15.0
    parity_timeout_s: float = 30.0
    perf_timeout_s: float = 60.0
    mem_limit_mb: int | None = 1024
    perf_mem_limit_mb: int | None = 2048


class RunConfig(BaseModel):
    run_id: str | None = None
    samples: int = 1
    temp: float = 0.0
    max_tokens: int = 1024
    seed: int | None = None

    tasks_root: str = "tasks"
    task_glob: list[str] | None = None

    solvers: list[str] = Field(default_factory=lambda: ["single_agent"])
    deployments: list[DeploymentConfig] = Field(default_factory=list)
    executor: ExecutorConfig = Field(default_factory=ExecutorConfig)

    # Parity/perf only run on the first sample by default (pass@k is a test-suite concept).
    parity_perf_on_all_samples: bool = False
    results_root: str = "results"

    @classmethod
    def from_yaml(cls, path: str | Path) -> RunConfig:
        data = yaml.safe_load(Path(path).read_text()) or {}
        return cls.model_validate(data)

    def apply_overrides(self, **overrides) -> RunConfig:
        """Return a copy with non-None overrides applied (used for CLI overlay)."""
        patch = {k: v for k, v in overrides.items() if v is not None}
        return self.model_copy(update=patch)
