"""Functional-correctness suite: run the task's tests against the candidate."""

from __future__ import annotations

import json

from slm_coding_bench.executors.base import ExecRequest, Executor
from slm_coding_bench.models import Candidate, SuiteResult, SuiteStatus, Task
from slm_coding_bench.suites.base import Suite, read_tests


class TestSuite(Suite):
    name = "test"
    __test__ = False  # not a pytest test class


    def __init__(self, timeout_s: float = 15.0, mem_limit_mb: int | None = 1024) -> None:
        self.timeout_s = timeout_s
        self.mem_limit_mb = mem_limit_mb

    def evaluate(self, task: Task, candidate: Candidate, executor: Executor) -> SuiteResult:
        if not candidate.extraction_ok:
            return SuiteResult(
                suite="test", status=SuiteStatus.fail, score=0.0,
                detail={"reason": "no parseable code extracted from model output"},
            )

        spec = {"op": "test", "entrypoint": task.manifest.entrypoint}
        req = ExecRequest(
            files={
                "solution.py": candidate.code,
                "tests.py": read_tests(task),
                "spec.json": json.dumps(spec),
            },
            entry="_child_runner.py",
            argv=["spec.json"],
            timeout_s=self.timeout_s,
            mem_limit_mb=self.mem_limit_mb,
        )
        res = executor.run(req)

        if res.timed_out:
            return SuiteResult(suite="test", status=SuiteStatus.timeout, score=0.0,
                               detail={"wall_ms": res.wall_ms})
        rj = res.result_json
        if rj is None or "fatal" in rj:
            return SuiteResult(
                suite="test", status=SuiteStatus.error, score=0.0,
                detail={"stderr": res.stderr[-1000:], "fatal": (rj or {}).get("fatal")},
            )
        if rj.get("passed"):
            return SuiteResult(suite="test", status=SuiteStatus.pass_, score=1.0,
                               detail={"n_tests": rj.get("n_tests")})
        return SuiteResult(
            suite="test", status=SuiteStatus.fail, score=0.0,
            detail={"error": (rj.get("error") or "")[-1200:], "n_tests": rj.get("n_tests")},
        )
