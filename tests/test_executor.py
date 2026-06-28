"""Tests for the subprocess executor + value-channel driver."""

from __future__ import annotations

import json

from slm_coding_bench.executors.base import ExecRequest
from slm_coding_bench.executors.subprocess_exec import SubprocessExecutor

EX = SubprocessExecutor()


def _spec(d: dict) -> str:
    return json.dumps(d)


def test_op_test_pass():
    req = ExecRequest(
        files={
            "solution.py": "def add(a, b):\n    return a + b\n",
            "tests.py": "from solution import add\n\ndef test_add():\n    assert add(2, 3) == 5\n",
            "spec.json": _spec({"op": "test", "entrypoint": "add"}),
        },
        entry="_child_runner.py",
        argv=["spec.json"],
    )
    res = EX.run(req)
    assert res.ok and not res.timed_out
    assert res.result_json == {"passed": True, "error": None, "n_tests": 1}


def test_op_test_fail():
    req = ExecRequest(
        files={
            "solution.py": "def add(a, b):\n    return a - b\n",
            "tests.py": "from solution import add\n\ndef test_add():\n    assert add(2, 3) == 5\n",
            "spec.json": _spec({"op": "test", "entrypoint": "add"}),
        },
        entry="_child_runner.py",
        argv=["spec.json"],
    )
    res = EX.run(req)
    assert res.result_json is not None and res.result_json["passed"] is False
    assert "test_add" in res.result_json["error"]


def test_op_test_humaneval_check():
    req = ExecRequest(
        files={
            "solution.py": "def add(a, b):\n    return a + b\n",
            "tests.py": "def check(candidate):\n    assert candidate(1, 1) == 2\n",
            "spec.json": _spec({"op": "test", "entrypoint": "add"}),
        },
        entry="_child_runner.py",
        argv=["spec.json"],
    )
    res = EX.run(req)
    assert res.result_json["passed"] is True


def test_timeout():
    req = ExecRequest(
        files={
            "solution.py": "def f():\n    return 1\n",
            "tests.py": "import time\n\ndef test_slow():\n    time.sleep(30)\n",
            "spec.json": _spec({"op": "test", "entrypoint": "f"}),
        },
        entry="_child_runner.py",
        argv=["spec.json"],
        timeout_s=1.5,
    )
    res = EX.run(req)
    assert res.timed_out and not res.ok


def test_op_parity_agreement():
    gen = (
        "import random\n"
        "def make_inputs(seed, n):\n"
        "    r = random.Random(seed)\n"
        "    return [[r.randint(0, 100), r.randint(0, 100)] for _ in range(n)]\n"
        "def run_case(impl, case):\n"
        "    return impl(case[0], case[1])\n"
    )
    files_common = {
        "generators.py": gen,
        "reference.py": "def add(a, b):\n    return a + b\n",
    }
    spec = {"op": "parity", "entrypoint": "add", "seed": 7, "n": 25}

    # Matching candidate -> all agree.
    good = EX.run(ExecRequest(
        files={**files_common, "solution.py": "def add(a, b):\n    return a + b\n",
               "spec.json": _spec({**spec, "target": "solution"})},
        entry="_child_runner.py", argv=["spec.json"],
    ))
    ref = EX.run(ExecRequest(
        files={**files_common, "spec.json": _spec({**spec, "target": "reference"})},
        entry="_child_runner.py", argv=["spec.json"],
    ))
    assert good.result_json["n"] == 25 and ref.result_json["n"] == 25
    cand_vals = [r["value"] for r in good.result_json["results"]]
    ref_vals = [r["value"] for r in ref.result_json["results"]]
    assert cand_vals == ref_vals


def test_op_perf_runs():
    perf = (
        "def run_once(impl, size):\n"
        "    data = list(range(size))\n"
        "    return impl(data)\n"
    )
    req = ExecRequest(
        files={
            "perf.py": perf,
            "solution.py": "def total(xs):\n    return sum(xs)\n",
            "spec.json": _spec({"op": "perf", "entrypoint": "total", "target": "solution",
                                "size": 1000, "warmup": 1, "repeats": 5}),
        },
        entry="_child_runner.py",
        argv=["spec.json"],
    )
    res = EX.run(req)
    assert res.result_json is not None and "min" in res.result_json
    assert len(res.result_json["times"]) == 5
