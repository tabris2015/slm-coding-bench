"""Tests for the test/parity/perf suites against a synthetic task on disk."""

from __future__ import annotations

import textwrap

import yaml

from slm_coding_bench.executors.subprocess_exec import SubprocessExecutor
from slm_coding_bench.models import Candidate, SuiteStatus
from slm_coding_bench.suites.parity_suite import ParitySuite
from slm_coding_bench.suites.perf_suite import PerfSuite
from slm_coding_bench.suites.test_suite import TestSuite
from slm_coding_bench.tasks.loader import load_task

EX = SubprocessExecutor()

GENERATORS = textwrap.dedent("""
    import random

    def make_inputs(seed, n):
        r = random.Random(seed)
        return [[r.randint(0, 20) for _ in range(r.randint(0, 10))] for _ in range(n)]

    def run_case(impl, case):
        return impl(list(case))
""")

REFERENCE = "def unique_sorted(xs):\n    return sorted(set(xs))\n"

PERF = textwrap.dedent("""
    import random

    def run_once(impl, size):
        r = random.Random(size)
        data = [r.randint(0, size) for _ in range(size)]
        return impl(data)
""")

TESTS = textwrap.dedent("""
    from solution import unique_sorted

    def test_basic():
        assert unique_sorted([3, 1, 2, 1, 3]) == [1, 2, 3]

    def test_empty():
        assert unique_sorted([]) == []
""")

MANIFEST = {
    "id": "custom/unique_sorted",
    "origin": "custom",
    "title": "Unique sorted",
    "entrypoint": "unique_sorted",
    "signature": "unique_sorted(xs: list[int]) -> list[int]",
    "suites": ["test", "parity", "perf"],
    "reference_file": "reference.py",
    "generators_file": "generators.py",
    "parity": {"num_cases": 40, "seed": 5},
    "perf": {"points": [{"name": "n=2000", "size": 2000, "repeats": 5}]},
}

GOOD = "def unique_sorted(xs):\n    return sorted(set(xs))\n"
BAD_PARITY = "def unique_sorted(xs):\n    return sorted(xs)\n"  # passes basic-ish, fails parity


def _make_task(tmp_path):
    d = tmp_path / "unique_sorted"
    d.mkdir()
    (d / "manifest.yaml").write_text(yaml.safe_dump(MANIFEST))
    (d / "prompt.md").write_text("Return the sorted unique elements of a list.")
    (d / "tests.py").write_text(TESTS)
    (d / "reference.py").write_text(REFERENCE)
    (d / "generators.py").write_text(GENERATORS)
    (d / "perf.py").write_text(PERF)
    return load_task(d / "manifest.yaml")


def _cand(code: str) -> Candidate:
    return Candidate(code=code, raw_output=code, extraction_ok=True)


def test_test_suite_pass_and_fail(tmp_path):
    task = _make_task(tmp_path)
    assert TestSuite().evaluate(task, _cand(GOOD), EX).status == SuiteStatus.pass_
    bad = TestSuite().evaluate(task, _cand("def unique_sorted(xs):\n    return xs\n"), EX)
    assert bad.status == SuiteStatus.fail


def test_parity_agrees_and_detects_divergence(tmp_path):
    task = _make_task(tmp_path)
    good = ParitySuite().evaluate(task, _cand(GOOD), EX)
    assert good.status == SuiteStatus.pass_ and good.score == 1.0
    bad = ParitySuite().evaluate(task, _cand(BAD_PARITY), EX)
    assert bad.status == SuiteStatus.fail and bad.score < 1.0
    assert bad.detail["failures"]  # captured at least one divergent case


def test_perf_reports_ratio(tmp_path):
    task = _make_task(tmp_path)
    res = PerfSuite().evaluate(task, _cand(GOOD), EX)
    assert res.status == SuiteStatus.pass_
    assert res.score is not None and res.score > 0
    assert res.detail["points"][0]["name"] == "n=2000"


def test_extraction_failure_is_graceful(tmp_path):
    task = _make_task(tmp_path)
    cand = Candidate(code="not code", raw_output="...", extraction_ok=False)
    assert TestSuite().evaluate(task, cand, EX).status == SuiteStatus.fail
