"""Self-consistency gate for the authored task corpus.

Every task's *reference* implementation, fed in as the candidate, must pass each suite it
declares: test -> pass, parity -> 100% agreement, perf -> produces a ratio (~1.0). This catches
broken references, mismatched entrypoints, non-JSON-serializable run_case outputs, and
misconfigured manifests before any model is ever run.
"""

from __future__ import annotations

import pytest

from slm_coding_bench.executors.subprocess_exec import SubprocessExecutor
from slm_coding_bench.models import Candidate, SuiteStatus
from slm_coding_bench.suites.base import read_reference
from slm_coding_bench.suites.parity_suite import ParitySuite
from slm_coding_bench.suites.perf_suite import PerfSuite
from slm_coding_bench.suites.test_suite import TestSuite
from slm_coding_bench.tasks.loader import load_tasks
from slm_coding_bench.tasks.manifest import SuiteName

EX = SubprocessExecutor()
TASKS = load_tasks("tasks")


def _ids(tasks):
    return [t.id for t in tasks]


@pytest.mark.skipif(not TASKS, reason="no tasks authored yet")
@pytest.mark.parametrize("task", TASKS, ids=_ids(TASKS))
def test_reference_is_self_consistent(task):
    # The reference, used as the candidate, must satisfy every declared suite.
    if task.applies(SuiteName.test):
        # reference defines the entrypoint; tests import it from `solution`.
        cand = Candidate(code=read_reference(task), raw_output="", extraction_ok=True)
        res = TestSuite().evaluate(task, cand, EX)
        assert res.status == SuiteStatus.pass_, f"{task.id} test: {res.detail}"

    if task.applies(SuiteName.parity):
        cand = Candidate(code=read_reference(task), raw_output="", extraction_ok=True)
        res = ParitySuite().evaluate(task, cand, EX)
        assert res.status == SuiteStatus.pass_ and res.score == 1.0, \
            f"{task.id} parity: {res.detail}"

    if task.applies(SuiteName.perf):
        cand = Candidate(code=read_reference(task), raw_output="", extraction_ok=True)
        res = PerfSuite().evaluate(task, cand, EX)
        assert res.status == SuiteStatus.pass_, f"{task.id} perf: {res.detail}"
        assert res.score is not None and 0.3 < res.score < 3.0, \
            f"{task.id} perf ratio unexpectedly far from 1.0: {res.score}"
