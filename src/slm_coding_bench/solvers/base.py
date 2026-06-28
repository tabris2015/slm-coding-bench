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
