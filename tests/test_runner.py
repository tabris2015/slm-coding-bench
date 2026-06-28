"""End-to-end runner test with a mocked deployment (no real LLM)."""

from __future__ import annotations

import textwrap

import yaml

from slm_coding_bench import registry
from slm_coding_bench.config import RunConfig
from slm_coding_bench.deployments.base import DeploymentAdapter
from slm_coding_bench.models import GenMetrics, SuiteStatus
from slm_coding_bench.results.leaderboard import render_markdown, summarize
from slm_coding_bench.runner import Runner
from slm_coding_bench.tasks.manifest import SuiteName

MANIFEST = {
    "id": "custom/unique_sorted",
    "title": "Unique sorted",
    "entrypoint": "unique_sorted",
    "suites": ["test", "parity", "perf"],
    "reference_file": "reference.py",
    "generators_file": "generators.py",
    "parity": {"num_cases": 20, "seed": 5},
    "perf": {"points": [{"name": "n=1000", "size": 1000, "repeats": 3}]},
}
GENERATORS = textwrap.dedent("""
    import random
    def make_inputs(seed, n):
        r = random.Random(seed)
        return [[r.randint(0, 20) for _ in range(5)] for _ in range(n)]
    def run_case(impl, case):
        return impl(list(case))
""")
PERF = textwrap.dedent("""
    import random
    def run_once(impl, size):
        r = random.Random(size)
        return impl([r.randint(0, size) for _ in range(size)])
""")
TESTS = "from solution import unique_sorted\n\ndef test_basic():\n    assert unique_sorted([2,1,2]) == [1,2]\n"
REFERENCE = "def unique_sorted(xs):\n    return sorted(set(xs))\n"
SOLUTION = "```python\ndef unique_sorted(xs):\n    return sorted(set(xs))\n```"


class MockDeployment(DeploymentAdapter):
    name = "mock"

    def health(self) -> bool:
        return True

    def chat(self, *, model, messages, temperature, max_tokens, seed=None, stream=True):
        m = GenMetrics(prompt_tokens=10, completion_tokens=20, ttft_ms=5.0,
                       total_ms=25.0, tok_per_s=800.0)
        self.metrics.record(model, m)
        return SOLUTION, m


def _make_tasks_dir(tmp_path):
    root = tmp_path / "tasks"
    d = root / "custom" / "unique_sorted"
    d.mkdir(parents=True)
    (d / "manifest.yaml").write_text(yaml.safe_dump(MANIFEST))
    (d / "prompt.md").write_text("Return sorted unique elements.")
    (d / "tests.py").write_text(TESTS)
    (d / "reference.py").write_text(REFERENCE)
    (d / "generators.py").write_text(GENERATORS)
    (d / "perf.py").write_text(PERF)
    return root


def test_end_to_end(tmp_path, monkeypatch):
    monkeypatch.setattr(registry, "build_deployment", lambda cfg: MockDeployment())
    # Runner imports build_deployment by name into its namespace:
    import slm_coding_bench.runner as runner_mod
    monkeypatch.setattr(runner_mod, "build_deployment", lambda cfg: MockDeployment())

    root = _make_tasks_dir(tmp_path)
    cfg = RunConfig.model_validate({
        "tasks_root": str(root),
        "results_root": str(tmp_path / "results"),
        "deployments": [{"kind": "openai_compat", "name": "mock",
                         "base_url": "http://x", "models": ["fake-model"]}],
    })
    store = Runner(cfg).run()

    records = store.read_records()
    suites_seen = {r.suite for r in records}
    assert suites_seen == {SuiteName.test, SuiteName.parity, SuiteName.perf}
    for suite in (SuiteName.test, SuiteName.parity):
        rec = next(r for r in records if r.suite == suite)
        assert rec.status == SuiteStatus.pass_
    perf_rec = next(r for r in records if r.suite == SuiteName.perf)
    assert perf_rec.status == SuiteStatus.pass_ and perf_rec.score is not None

    serving = store.read_serving()
    assert serving and serving[0].n_calls == 1

    summary = summarize(records, serving, cfg.samples)
    md = render_markdown(summary, store.run_id)
    assert "pass@1" in md and "Serving" in md
    assert summary["rows"][0]["pass1_custom"] == 1.0
