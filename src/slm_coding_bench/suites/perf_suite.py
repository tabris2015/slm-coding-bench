"""Runtime-performance suite.

For each perf point, times the candidate and the reference with the same warmup/repeats and takes
the *minimum* wall time (min-of-N rejects scheduler/GC noise). Reports the ratio
``candidate_min / reference_min`` per point and a geometric-mean aggregate. Results are advisory:
they compare against the reference, never absolute time. Reference timings are cached per task.

Note: the runner only schedules this suite for candidates that already passed `test`, so a
fast-but-wrong solution cannot score here.
"""

from __future__ import annotations

import json

from slm_coding_bench.executors.base import ExecRequest, Executor
from slm_coding_bench.models import Candidate, SuiteResult, SuiteStatus, Task
from slm_coding_bench.suites.base import Suite, read_perf_module, read_reference
from slm_coding_bench.util.stats import geomean


class PerfSuite(Suite):
    name = "perf"

    def __init__(self, timeout_s: float = 60.0, mem_limit_mb: int | None = 2048) -> None:
        self.timeout_s = timeout_s
        self.mem_limit_mb = mem_limit_mb
        self._ref_cache: dict[tuple[str, str], float | None] = {}

    def _run_point(self, task: Task, target: str, code_files: dict[str, str], point):
        spec = {
            "op": "perf",
            "target": target,
            "entrypoint": task.manifest.entrypoint,
            "size": point.size,
            "warmup": task.manifest.perf.warmup,
            "repeats": point.repeats,
        }
        req = ExecRequest(
            files={
                "perf.py": read_perf_module(task),
                "spec.json": json.dumps(spec),
                **code_files,
            },
            entry="_child_runner.py",
            argv=["spec.json"],
            timeout_s=self.timeout_s,
            mem_limit_mb=self.mem_limit_mb,
        )
        res = self.executor.run(req)
        rj = res.result_json
        if res.timed_out or rj is None or "min" not in rj:
            return None
        return rj["min"]

    def _reference_min(self, task: Task, point) -> float | None:
        key = (task.id, point.name)
        if key not in self._ref_cache:
            self._ref_cache[key] = self._run_point(
                task, "reference", {"reference.py": read_reference(task)}, point
            )
        return self._ref_cache[key]

    def evaluate(self, task: Task, candidate: Candidate, executor: Executor) -> SuiteResult:
        self.executor = executor
        if not candidate.extraction_ok:
            return SuiteResult(suite="perf", status=SuiteStatus.fail, score=None,
                               detail={"reason": "no parseable code extracted"})

        points = []
        ratios = []
        all_budgets_ok = True
        for point in task.manifest.perf.points:
            ref_min = self._reference_min(task, point)
            cand_min = self._run_point(task, "solution", {"solution.py": candidate.code}, point)
            if ref_min is None:
                return SuiteResult(suite="perf", status=SuiteStatus.error, score=None,
                                   detail={"reason": f"reference perf failed at {point.name}"})
            if cand_min is None:
                return SuiteResult(suite="perf", status=SuiteStatus.error, score=None,
                                   detail={"reason": f"candidate perf failed at {point.name}",
                                           "point": point.name})
            ratio = cand_min / ref_min if ref_min > 0 else None
            budget_ok = True if point.max_ratio is None else (ratio is not None
                                                              and ratio <= point.max_ratio)
            all_budgets_ok = all_budgets_ok and budget_ok
            ratios.append(ratio)
            points.append({
                "name": point.name, "cand_min_s": cand_min, "ref_min_s": ref_min,
                "ratio": ratio, "max_ratio": point.max_ratio, "budget_ok": budget_ok,
            })

        agg = geomean([r for r in ratios if r is not None])
        status = SuiteStatus.pass_ if all_budgets_ok else SuiteStatus.fail
        return SuiteResult(suite="perf", status=status, score=agg,
                           detail={"points": points, "geomean_ratio": agg})
