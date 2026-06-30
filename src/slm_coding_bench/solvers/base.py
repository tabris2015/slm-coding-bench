"""Solver interface: turn a task into a candidate solution using a deployment."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel

from slm_coding_bench.deployments.base import DeploymentAdapter
from slm_coding_bench.models import Candidate, Task


class SolverContext(BaseModel):
    """Per-sample generation settings handed to a solver."""

    temperature: float = 0.0
    max_tokens: int = 1024
    seed: int | None = None
    sample_index: int = 0


class Solver(ABC):
    name: str = "base"

    per_model: bool = True
    """If True, the runner evaluates this solver once per benchmarked model in the deployment.
    Roster solvers (e.g. multi-agent, which pin their own per-role models) set this False so the
    runner evaluates them once and labels the rows with :attr:`roster_label`."""

    def roster_label(self, deployment_models: list[str]) -> str:
        """Row label for a ``per_model=False`` solver. Defaults to the solver name."""
        return self.name

    @abstractmethod
    def solve(
        self,
        task: Task,
        *,
        model: str,
        deployment: DeploymentAdapter,
        ctx: SolverContext,
    ) -> Candidate:  # pragma: no cover - interface
        ...
