"""Differential-testing (parity) suite.

Runs the candidate and a reference implementation over the same seeded inputs (via each task's
``run_case(impl, case)``) and reports the agreement rate. Reference outputs are computed once per
task and cached. For tasks with multiple valid answers, ``run_case`` should canonicalize (e.g.
return a validity flag or a normalized form) so equality is meaningful.
"""

from __future__ import annotations

import json

from slm_coding_bench.executors.base import ExecRequest, Executor
from slm_coding_bench.models import Candidate, SuiteResult, SuiteStatus, Task
from slm_coding_bench.suites.base import Suite, compare_values, read_generators, read_reference


class ParitySuite(Suite):
    name = "parity"

    def __init__(self, timeout_s: float = 30.0, mem_limit_mb: int | None = 1024,
                 pass_threshold: float = 1.0) -> None:
        self.timeout_s = timeout_s
        self.mem_limit_mb = mem_limit_mb
        self.pass_threshold = pass_threshold
        self._ref_cache: dict[str, list[dict] | None] = {}

    def _run_target(self, task: Task, target: str, code_files: dict[str, str]):
        spec = {
            "op": "parity",
            "target": target,
            "entrypoint": task.manifest.entrypoint,
            "seed": task.manifest.parity.seed,
            "n": task.manifest.parity.num_cases,
        }
        req = ExecRequest(
            files={
                "generators.py": read_generators(task),
                "spec.json": json.dumps(spec),
                **code_files,
            },
            entry="_child_runner.py",
            argv=["spec.json"],
            timeout_s=self.timeout_s,
            mem_limit_mb=self.mem_limit_mb,
        )
        return self.executor.run(req)

    def _reference_results(self, task: Task) -> list[dict] | None:
        if task.id not in self._ref_cache:
            res = self._run_target(task, "reference", {"reference.py": read_reference(task)})
            rj = res.result_json
            self._ref_cache[task.id] = (
                rj["results"] if (rj and "results" in rj and not res.timed_out) else None
            )
        return self._ref_cache[task.id]

    def evaluate(self, task: Task, candidate: Candidate, executor: Executor) -> SuiteResult:
        self.executor = executor
        if not candidate.extraction_ok:
            return SuiteResult(suite="parity", status=SuiteStatus.fail, score=0.0,
                               detail={"reason": "no parseable code extracted"})

        ref_results = self._reference_results(task)
        if ref_results is None:
            return SuiteResult(suite="parity", status=SuiteStatus.error, score=0.0,
                               detail={"reason": "reference run failed (task is misconfigured)"})

        cand_res = self._run_target(task, "solution", {"solution.py": candidate.code})
        if cand_res.timed_out:
            return SuiteResult(suite="parity", status=SuiteStatus.timeout, score=0.0,
                               detail={"wall_ms": cand_res.wall_ms})
        rj = cand_res.result_json
        if rj is None or "fatal" in rj:
            return SuiteResult(suite="parity", status=SuiteStatus.error, score=0.0,
                               detail={"stderr": cand_res.stderr[-1000:],
                                       "fatal": (rj or {}).get("fatal")})

        cand_results = rj.get("results", [])
        n = min(len(ref_results), len(cand_results))
        spec = task.manifest.parity
        agree = 0
        failures = []
        for i in range(n):
            r, c = ref_results[i], cand_results[i]
            ok = self._cases_agree(r, c, spec.abs_tol, spec.rel_tol)
            if ok:
                agree += 1
            elif len(failures) < spec.max_failing_examples:
                failures.append({"index": i, "reference": _trunc(r), "candidate": _trunc(c)})

        score = agree / n if n else 0.0
        status = SuiteStatus.pass_ if score >= self.pass_threshold else SuiteStatus.fail
        return SuiteResult(
            suite="parity", status=status, score=score,
            detail={"n": n, "agree": agree, "seed": spec.seed, "failures": failures},
        )

    @staticmethod
    def _cases_agree(r: dict, c: dict, abs_tol: float, rel_tol: float) -> bool:
        if r.get("ok") and c.get("ok"):
            return compare_values(r.get("value"), c.get("value"), abs_tol, rel_tol)
        if not r.get("ok") and not c.get("ok"):
            # Both raised: agree iff the same exception type (models specified error behavior).
            return r.get("exc") == c.get("exc")
        return False  # exactly one raised


def _trunc(obj, limit: int = 200):
    s = repr(obj)
    return s if len(s) <= limit else s[:limit] + "…"
