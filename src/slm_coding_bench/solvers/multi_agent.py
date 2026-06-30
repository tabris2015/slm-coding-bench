"""Multi-agent solver: a heterogeneous, verifier-checked planner -> coder -> verifier graph.

Design (from the project research): a heterogeneous, *moderately-sparse* graph rather than a flat
swarm, to suppress the small-model error-compounding/tool-reliability cliff.

    Planner   (e.g. Qwen2.5-Coder-7B)  -> a short algorithm plan (no code)
    Coder     (e.g. Qwen2.5-Coder-3B)  -> implement the plan as code
    Verifier  (e.g. Qwen3-1.7B)        -> check the candidate, then either APPROVE or send
                                          concrete feedback back to the coder (bounded retries)

**Honesty of the verifier's ground truth.** The verifier must never see the task's graded
``tests.py`` (that *is* the pass@1 metric). Instead it checks the candidate against the worked
``## Examples`` already present in the prompt — information every solver is given — executed in a
fresh sandbox, plus an LLM code review. So the verify->retry loop earns its keep without
contaminating the benchmark. Tasks that ship no extractable examples fall back to LLM review only.

Each node calls ``deployment.chat()`` with its own model id, so one deployment that serves all
three models by per-request selection is sufficient. This solver pins its own roster, so it is a
``per_model=False`` solver: the runner evaluates it once and labels the row via
:meth:`roster_label`.
"""

from __future__ import annotations

import ast
import json
import re

from slm_coding_bench.deployments.base import DeploymentAdapter
from slm_coding_bench.executors.base import ExecRequest
from slm_coding_bench.executors.subprocess_exec import SubprocessExecutor
from slm_coding_bench.extract import extract_code
from slm_coding_bench.models import Candidate, GenMetrics, Task
from slm_coding_bench.solvers.base import Solver, SolverContext

_FENCE_RE = re.compile(r"```[a-zA-Z0-9_+-]*\n(?P<body>.*?)```", re.DOTALL)
_APPROVE_RE = re.compile(r"\bAPPROVE\b", re.IGNORECASE)
_REVISE_RE = re.compile(r"\b(REVISE|REJECT|BUG|INCORRECT|WRONG)\b", re.IGNORECASE)

PLANNER_SYSTEM = (
    "You are a senior algorithm designer. Given a coding task, write a SHORT plan (3-6 bullet "
    "points) the implementer will follow: the core approach/data structure, the target time "
    "complexity, and the edge cases that must be handled. Do NOT write code — plan only."
)

CODER_SYSTEM = (
    "You are an expert Python programmer. Implement the task following the given plan.\n"
    "Rules:\n"
    "- Define exactly the requested entrypoint with the exact name and signature.\n"
    "- Return ONLY the solution code inside one ```python code block. No explanation, no tests, "
    "no example usage.\n"
    "- Do not read from stdin or print; the entrypoint is imported and called directly.\n"
    "- Use only the Python standard library."
)

VERIFIER_SYSTEM = (
    "You are a meticulous code reviewer. You are given a task, a candidate Python solution, and "
    "the result of running the candidate against the task's worked examples. Decide whether the "
    "solution is correct and robust (including the stated edge cases).\n"
    "- If it is correct, reply with exactly the word APPROVE on its own line.\n"
    "- Otherwise reply REVISE and then, in 1-3 sentences, the specific bug or missing case the "
    "implementer must fix. Do not write the corrected code yourself."
)


def extract_examples(prompt: str, entrypoint: str) -> list[str]:
    """Pull worked ``entrypoint(...) == expected`` assertions out of a task prompt.

    Looks inside fenced code blocks for boolean expressions that call ``entrypoint`` and contain a
    top-level comparison. Each returned string is a Python expression that should evaluate truthy
    against a correct solution. Doctest-style ``>>>`` lines are not handled (none in the corpus).
    """
    out: list[str] = []
    seen: set[str] = set()
    call = entrypoint + "("
    for m in _FENCE_RE.finditer(prompt):
        for raw in m.group("body").splitlines():
            line = raw.strip()
            if line.startswith("assert "):
                line = line[len("assert "):].strip()
            if call not in line or "==" not in line:
                continue
            if not _is_bool_expr(line):
                continue
            if line not in seen:
                seen.add(line)
                out.append(line)
    return out


def _is_bool_expr(src: str) -> bool:
    try:
        node = ast.parse(src, mode="eval")
    except (SyntaxError, ValueError):
        return False
    return isinstance(node.body, ast.Compare)


_CHECK_DRIVER = '''
import json, sys
ns = {}
try:
    with open("solution.py") as fh:
        exec(compile(fh.read(), "solution.py", "exec"), ns)
except Exception as e:
    json.dump({"loaded": False, "error": repr(e)}, open("result.json", "w"))
    sys.exit(0)
spec = json.load(open(sys.argv[1]))
results = []
for expr in spec["asserts"]:
    try:
        ok = bool(eval(expr, dict(ns)))
        results.append({"expr": expr, "ok": ok})
    except Exception as e:
        results.append({"expr": expr, "ok": False, "error": repr(e)})
json.dump({"loaded": True, "results": results}, open("result.json", "w"))
'''


class MultiAgentSolver(Solver):
    name = "multi_agent"
    per_model = False

    def __init__(
        self,
        *,
        planner_model: str | None = None,
        coder_model: str | None = None,
        verifier_model: str | None = None,
        max_retries: int = 2,
        example_timeout_s: float = 10.0,
        example_mem_limit_mb: int | None = 1024,
    ) -> None:
        self.planner_model = planner_model
        self.coder_model = coder_model
        self.verifier_model = verifier_model
        self.max_retries = max_retries
        self._executor = SubprocessExecutor()
        self._example_timeout_s = example_timeout_s
        self._example_mem_limit_mb = example_mem_limit_mb

    def roster_label(self, deployment_models: list[str]) -> str:
        def _short(m: str | None) -> str:
            if not m:
                return "?"
            return m.rsplit("/", 1)[-1].replace("-Instruct", "").replace("-4bit", "")
        return (f"multi[{_short(self.planner_model)}>"
                f"{_short(self.coder_model)}>{_short(self.verifier_model)}]")

    def solve(
        self,
        task: Task,
        *,
        model: str,
        deployment: DeploymentAdapter,
        ctx: SolverContext,
    ) -> Candidate:
        planner_model = self.planner_model or model
        coder_model = self.coder_model or model
        verifier_model = self.verifier_model or coder_model

        calls: list[GenMetrics] = []

        def chat(model_id, messages, max_tokens=None):
            text, m = deployment.chat(
                model=model_id, messages=messages, temperature=ctx.temperature,
                max_tokens=max_tokens or ctx.max_tokens, seed=ctx.seed,
            )
            calls.append(m)
            return text

        examples = extract_examples(task.prompt, task.manifest.entrypoint)

        # 1. Plan.
        plan = chat(planner_model, [
            {"role": "system", "content": PLANNER_SYSTEM},
            {"role": "user", "content": _planner_user(task)},
        ])

        # 2-3. Code, check against examples, optionally LLM-review, retry on failure.
        feedback: str | None = None
        code, raw, ok = "", "", False
        for attempt in range(self.max_retries + 1):
            raw = chat(coder_model, [
                {"role": "system", "content": CODER_SYSTEM},
                {"role": "user", "content": _coder_user(task, plan, feedback)},
            ])
            code, ok = extract_code(raw, entrypoint=task.manifest.entrypoint)

            if not ok:
                feedback = ("Your previous reply did not contain a parseable Python solution "
                            "inside a ```python code block. Return only the code.")
                continue

            example_report = self._run_examples(code, examples) if examples else None
            if example_report and example_report["failures"]:
                if attempt < self.max_retries:
                    feedback = _example_feedback(example_report["failures"])
                    continue
                break  # out of retries; return the last candidate for honest grading

            # Examples pass (or none): an LLM review is the remaining gate.
            verdict = chat(verifier_model, [
                {"role": "system", "content": VERIFIER_SYSTEM},
                {"role": "user", "content": _verifier_user(task, code, example_report)},
            ])
            if _approved(verdict) or attempt == self.max_retries:
                break
            feedback = _verifier_feedback(verdict)

        return Candidate(
            code=code,
            raw_output=raw,
            extraction_ok=ok,
            sample_index=ctx.sample_index,
            finish_reason=None,
            gen_metrics=_combine(calls),
        )

    def _run_examples(self, code: str, examples: list[str]) -> dict:
        """Run the candidate against the prompt examples in a sandbox. Returns failure detail."""
        req = ExecRequest(
            files={"solution.py": code, "check.py": _CHECK_DRIVER,
                   "spec.json": json.dumps({"asserts": examples})},
            entry="check.py",
            argv=["spec.json"],
            timeout_s=self._example_timeout_s,
            mem_limit_mb=self._example_mem_limit_mb,
        )
        res = self._executor.run(req)
        rj = res.result_json or {}
        if res.timed_out:
            return {"n": len(examples), "failures": [{"expr": "<all>", "error": "timeout"}]}
        if not rj.get("loaded", False):
            return {"n": len(examples),
                    "failures": [{"expr": "<import>", "error": rj.get("error", "load failed")}]}
        failures = [r for r in rj.get("results", []) if not r.get("ok")]
        return {"n": len(examples), "failures": failures}


def _planner_user(task: Task) -> str:
    parts = [task.prompt.strip(), "",
             f"Plan the implementation of `{task.manifest.entrypoint}`."]
    if task.manifest.signature:
        parts.append(f"Signature: {task.manifest.signature}")
    return "\n".join(parts)


def _coder_user(task: Task, plan: str, feedback: str | None) -> str:
    parts = [task.prompt.strip(), "",
             f"Define a top-level Python entrypoint named `{task.manifest.entrypoint}`."]
    if task.manifest.signature:
        parts.append(f"Expected signature/usage: {task.manifest.signature}")
    parts += ["", "Implementation plan:", plan.strip()]
    if feedback:
        parts += ["", "A previous attempt was rejected. Fix this and return the full corrected "
                  "solution:", feedback.strip()]
    return "\n".join(parts)


def _verifier_user(task: Task, code: str, example_report: dict | None) -> str:
    parts = [task.prompt.strip(), "", "Candidate solution:", "```python", code.strip(), "```"]
    if example_report is None:
        parts += ["", "No worked examples were available to run; review by reasoning about the "
                  "code against the task and its edge cases."]
    else:
        parts += ["", f"The candidate passed all {example_report['n']} worked example(s) from the "
                  "task. Review for any remaining bug or unhandled edge case."]
    return "\n".join(parts)


def _example_feedback(failures: list[dict]) -> str:
    lines = ["The solution failed these worked examples from the task:"]
    for f in failures[:5]:
        if "error" in f:
            lines.append(f"- `{f['expr']}` raised {f['error']}")
        else:
            lines.append(f"- `{f['expr']}` was not satisfied")
    return "\n".join(lines)


def _verifier_feedback(verdict: str) -> str:
    cleaned = _REVISE_RE.sub("", verdict).strip() or verdict.strip()
    return f"A reviewer flagged a problem: {cleaned}"


def _approved(verdict: str) -> bool:
    return bool(_APPROVE_RE.search(verdict)) and not _REVISE_RE.search(verdict)


def _combine(calls: list[GenMetrics]) -> GenMetrics | None:
    """Sum a pipeline's per-call metrics into one honest per-task cost record."""
    if not calls:
        return None
    prompt = sum(c.prompt_tokens or 0 for c in calls)
    completion = sum(c.completion_tokens or 0 for c in calls)
    total_ms = sum(c.total_ms or 0.0 for c in calls)
    ttft = next((c.ttft_ms for c in calls if c.ttft_ms is not None), None)
    tps = completion / (total_ms / 1000.0) if completion and total_ms > 0 else None
    return GenMetrics(prompt_tokens=prompt or None, completion_tokens=completion or None,
                      ttft_ms=ttft, total_ms=total_ms or None, tok_per_s=tps)
