"""Multi-agent solver: example extraction, the verify->retry loop, and runner wiring."""

from __future__ import annotations

import textwrap

import yaml

from slm_coding_bench import registry
from slm_coding_bench.config import RunConfig, SolverConfig
from slm_coding_bench.deployments.base import DeploymentAdapter
from slm_coding_bench.models import GenMetrics, SuiteStatus
from slm_coding_bench.runner import Runner
from slm_coding_bench.solvers.base import SolverContext
from slm_coding_bench.solvers.multi_agent import MultiAgentSolver, extract_examples
from slm_coding_bench.tasks.manifest import SuiteName

PROMPT = textwrap.dedent("""
    # Add one

    Write `add_one(x)` that returns x + 1.

    ## Examples

    ```
    add_one(1) == 2
    add_one(-5) == -4
    ```
""")


def test_extract_examples_picks_only_comparisons():
    ex = extract_examples(PROMPT, "add_one")
    assert ex == ["add_one(1) == 2", "add_one(-5) == -4"]


def test_extract_examples_ignores_unrelated_lines():
    prompt = "```\nsome_prose add_one\nadd_one(3) == 4\nplain_call(1)\n```"
    assert extract_examples(prompt, "add_one") == ["add_one(3) == 4"]


def _ctx() -> SolverContext:
    return SolverContext(temperature=0.0, max_tokens=256, seed=1)


def _task(tmp_path, suites=("test",)):
    from slm_coding_bench.models import Task
    from slm_coding_bench.tasks.manifest import TaskManifest
    d = tmp_path / "custom" / "add_one"
    d.mkdir(parents=True)
    manifest = TaskManifest(id="custom/add_one", title="Add one", entrypoint="add_one",
                            suites=[SuiteName(s) for s in suites])
    return Task(manifest=manifest, dir=d, prompt=PROMPT)


GOOD = "```python\ndef add_one(x):\n    return x + 1\n```"
BAD = "```python\ndef add_one(x):\n    return x + 2\n```"


class ScriptedDeployment(DeploymentAdapter):
    """Returns queued replies per role model; records which models were called."""

    name = "scripted"

    def __init__(self, replies: dict[str, list[str]]):
        super().__init__()
        self.replies = {k: list(v) for k, v in replies.items()}
        self.calls: list[str] = []

    def health(self) -> bool:
        return True

    def chat(self, *, model, messages, temperature, max_tokens, seed=None, stream=True):
        self.calls.append(model)
        text = self.replies[model].pop(0)
        m = GenMetrics(prompt_tokens=5, completion_tokens=7, ttft_ms=1.0, total_ms=10.0,
                       tok_per_s=700.0)
        self.metrics.record(model, m)
        return text, m


def test_multi_agent_approves_when_examples_pass(tmp_path):
    dep = ScriptedDeployment({
        "planner": ["1. add one to x"],
        "coder": [GOOD],
        "verifier": ["APPROVE"],
    })
    solver = MultiAgentSolver(planner_model="planner", coder_model="coder",
                              verifier_model="verifier", max_retries=2)
    cand = solver.solve(_task(tmp_path), model="x", deployment=dep, ctx=_ctx())
    assert cand.extraction_ok and "x + 1" in cand.code
    # planner, coder, verifier — exactly one of each, no retry.
    assert dep.calls == ["planner", "coder", "verifier"]
    # Pipeline cost is the sum across the three calls.
    assert cand.gen_metrics.completion_tokens == 21
    assert cand.gen_metrics.total_ms == 30.0


def test_multi_agent_retries_on_failing_examples(tmp_path):
    # First coder answer is wrong (fails examples) -> retry -> second answer is correct.
    # A wrong answer is caught by the example sandbox, so the verifier is only called after a
    # candidate passes the examples.
    dep = ScriptedDeployment({
        "planner": ["plan"],
        "coder": [BAD, GOOD],
        "verifier": ["APPROVE"],
    })
    solver = MultiAgentSolver(planner_model="planner", coder_model="coder",
                              verifier_model="verifier", max_retries=2)
    cand = solver.solve(_task(tmp_path), model="x", deployment=dep, ctx=_ctx())
    assert "x + 1" in cand.code
    assert dep.calls == ["planner", "coder", "coder", "verifier"]


def test_runner_wires_multi_agent_as_single_roster_row(tmp_path, monkeypatch):
    dep = ScriptedDeployment({
        "P": ["plan"] * 10, "C": [GOOD] * 10, "V": ["APPROVE"] * 10,
    })
    import slm_coding_bench.runner as runner_mod
    monkeypatch.setattr(runner_mod, "build_deployment", lambda cfg: dep)

    root = tmp_path / "tasks"
    d = root / "custom" / "add_one"
    d.mkdir(parents=True)
    d.joinpath("manifest.yaml").write_text(yaml.safe_dump({
        "id": "custom/add_one", "title": "Add one", "entrypoint": "add_one", "suites": ["test"],
    }))
    d.joinpath("prompt.md").write_text(PROMPT)
    d.joinpath("tests.py").write_text(
        "from solution import add_one\n\ndef test_x():\n    assert add_one(1) == 2\n")

    cfg = RunConfig.model_validate({
        "tasks_root": str(root),
        "results_root": str(tmp_path / "results"),
        "solvers": [{"name": "multi_agent",
                     "params": {"planner_model": "P", "coder_model": "C", "verifier_model": "V"}}],
        "deployments": [{"kind": "openai_compat", "name": "m", "base_url": "http://x",
                         "models": ["P", "C", "V"]}],
    })
    store = Runner(cfg).run()
    records = store.read_records()
    # Exactly one roster row's worth of test records (one task), labelled by the roster, not per model.
    test_recs = [r for r in records if r.suite == SuiteName.test]
    assert len(test_recs) == 1
    assert test_recs[0].solver == "multi_agent"
    assert test_recs[0].model.startswith("multi[")
    assert test_recs[0].status == SuiteStatus.pass_
    # Combined serving row uses the roster label.
    serving = store.read_serving()
    assert len(serving) == 1 and serving[0].model.startswith("multi[")
    assert serving[0].n_calls == 3


def test_build_solver_accepts_params():
    solver = registry.build_solver(SolverConfig(name="multi_agent",
                                                params={"coder_model": "c", "max_retries": 1}))
    assert isinstance(solver, MultiAgentSolver)
    assert solver.coder_model == "c" and solver.max_retries == 1 and solver.per_model is False
