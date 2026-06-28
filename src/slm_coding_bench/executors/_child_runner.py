"""Value-channel driver, copied into each sandbox and run by :class:`SubprocessExecutor`.

Stdlib only (no package imports): it is executed inside the isolated working directory with the
candidate/reference/test/generator files alongside it. It reads a JSON spec (argv[1], default
``spec.json``), performs one operation, and writes ``result.json``. Suites interpret that file.

Operations
----------
- ``test``   run a task's tests against the candidate -> {passed, error, n_tests}
- ``parity`` call ``run_case(impl, case)`` for each generated case -> {results: [...]}
- ``perf``   time ``run_once(impl, size)`` (warmup + repeats) -> {times, min}
"""

from __future__ import annotations

import importlib
import json
import os
import sys
import time
import traceback

# Ensure the sandbox working directory is importable regardless of interpreter flags.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _write(result: dict) -> None:
    with open("result.json", "w") as fh:
        json.dump(result, fh)


def _load_attr(module_name: str, attr: str):
    mod = importlib.import_module(module_name)
    return getattr(mod, attr)


def _short_tb(limit: int = 2000) -> str:
    return traceback.format_exc()[-limit:]


def op_test(spec: dict) -> dict:
    entrypoint = spec["entrypoint"]
    solution_module = spec.get("solution_module", "solution")
    tests_module = spec.get("tests_module", "tests")
    try:
        tests = importlib.import_module(tests_module)
    except Exception:
        return {"passed": False, "error": "tests import failed: " + _short_tb(), "n_tests": 0}

    # HumanEval-style: a `check(candidate)` function.
    if hasattr(tests, "check"):
        try:
            fn = _load_attr(solution_module, entrypoint)
        except Exception:
            return {"passed": False, "error": "solution import failed: " + _short_tb(),
                    "n_tests": 1}
        try:
            tests.check(fn)
            return {"passed": True, "error": None, "n_tests": 1}
        except Exception:
            return {"passed": False, "error": _short_tb(), "n_tests": 1}

    # Otherwise: run every top-level `test_*` callable (they import `solution` themselves).
    test_fns = [getattr(tests, n) for n in dir(tests)
                if n.startswith("test_") and callable(getattr(tests, n))]
    if not test_fns:
        return {"passed": False, "error": "no check() or test_* functions found", "n_tests": 0}
    for fn in test_fns:
        try:
            fn()
        except Exception:
            return {"passed": False, "error": f"{fn.__name__}: " + _short_tb(),
                    "n_tests": len(test_fns)}
    return {"passed": True, "error": None, "n_tests": len(test_fns)}


def op_parity(spec: dict) -> dict:
    target = spec["target"]  # "solution" | "reference"
    entrypoint = spec["entrypoint"]
    gen_module = spec.get("gen_module", "generators")
    make_inputs = spec.get("make_inputs", "make_inputs")
    run_case = spec.get("run_case", "run_case")
    seed = int(spec.get("seed", 1234))
    n = int(spec.get("n", 200))

    try:
        gen = importlib.import_module(gen_module)
        make_fn = getattr(gen, make_inputs)
        run_fn = getattr(gen, run_case)
    except Exception:
        return {"fatal": "generators import failed: " + _short_tb()}

    try:
        impl = _load_attr(target, entrypoint)
    except Exception:
        return {"fatal": f"{target} import failed: " + _short_tb()}

    try:
        cases = make_fn(seed=seed, n=n)
    except Exception:
        return {"fatal": "make_inputs failed: " + _short_tb()}

    results = []
    for case in cases:
        try:
            value = run_fn(impl, case)
            results.append({"ok": True, "value": value})
        except Exception as e:
            results.append({"ok": False, "exc": type(e).__name__})
    return {"results": results, "n": len(results)}


def op_perf(spec: dict) -> dict:
    target = spec["target"]
    entrypoint = spec["entrypoint"]
    perf_module = spec.get("perf_module", "perf")
    run_once = spec.get("run_once", "run_once")
    size = int(spec["size"])
    warmup = int(spec.get("warmup", 1))
    repeats = int(spec.get("repeats", 7))

    try:
        perf = importlib.import_module(perf_module)
        run_fn = getattr(perf, run_once)
        impl = _load_attr(target, entrypoint)
    except Exception:
        return {"fatal": "perf import failed: " + _short_tb()}

    try:
        for _ in range(warmup):
            run_fn(impl, size=size)
        times = []
        for _ in range(repeats):
            t0 = time.perf_counter()
            run_fn(impl, size=size)
            times.append(time.perf_counter() - t0)
    except Exception:
        return {"fatal": "perf run failed: " + _short_tb()}

    return {"times": times, "min": min(times)}


_OPS = {"test": op_test, "parity": op_parity, "perf": op_perf}


def main() -> int:
    spec_path = sys.argv[1] if len(sys.argv) > 1 else "spec.json"
    try:
        with open(spec_path) as fh:
            spec = json.load(fh)
    except Exception:
        _write({"fatal": "spec load failed: " + _short_tb()})
        return 0
    op = _OPS.get(spec.get("op", ""))
    if op is None:
        _write({"fatal": f"unknown op: {spec.get('op')!r}"})
        return 0
    _write(op(spec))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
