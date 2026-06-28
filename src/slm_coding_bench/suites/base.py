"""Suite interface and shared helpers for reading task artifacts into the sandbox.

Sandbox module-name convention (what the value-channel driver imports):
``solution`` (candidate), ``reference``, ``generators`` (make_inputs + run_case), ``perf``
(run_once), ``tests``. Manifest file contents are mapped onto these standard names.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from slm_coding_bench.executors.base import Executor
from slm_coding_bench.models import Candidate, SuiteResult, Task


class Suite(ABC):
    name: str = "base"

    @abstractmethod
    def evaluate(
        self, task: Task, candidate: Candidate, executor: Executor
    ) -> SuiteResult:  # pragma: no cover - interface
        ...


def read_tests(task: Task) -> str:
    return (task.dir / task.manifest.tests_file).read_text()


def read_reference(task: Task) -> str:
    return (task.dir / task.manifest.reference_file).read_text()


def read_generators(task: Task) -> str:
    return (task.dir / task.manifest.generators_file).read_text()


def read_perf_module(task: Task) -> str:
    module = task.manifest.perf.runner.split(":", 1)[0]
    return (task.dir / f"{module}.py").read_text()


def compare_values(a, b, abs_tol: float = 0.0, rel_tol: float = 0.0) -> bool:
    """Structural comparison with optional numeric tolerance (recurses dicts/lists/tuples)."""
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if abs_tol == 0.0 and rel_tol == 0.0:
            return a == b
        diff = abs(a - b)
        return diff <= max(abs_tol, rel_tol * max(abs(a), abs(b)))
    if isinstance(a, dict) and isinstance(b, dict):
        if a.keys() != b.keys():
            return False
        return all(compare_values(a[k], b[k], abs_tol, rel_tol) for k in a)
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        if len(a) != len(b):
            return False
        return all(compare_values(x, y, abs_tol, rel_tol) for x, y in zip(a, b))
    return a == b
