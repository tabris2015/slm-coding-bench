"""Single-agent solver: one model call produces the whole solution."""

from __future__ import annotations

from slm_coding_bench.deployments.base import DeploymentAdapter
from slm_coding_bench.extract import extract_code
from slm_coding_bench.models import Candidate, Task
from slm_coding_bench.solvers.base import Solver, SolverContext

SYSTEM_PROMPT = (
    "You are an expert Python programmer. Write a single, self-contained Python solution to the "
    "user's task.\n"
    "Rules:\n"
    "- Define exactly the requested entrypoint with the exact name and signature.\n"
    "- Return ONLY the solution code inside one ```python code block. No explanation, no tests, "
    "no example usage.\n"
    "- Do not read from stdin or print; the entrypoint is imported and called directly.\n"
    "- Use only the Python standard library."
)


def build_user_prompt(task: Task) -> str:
    parts = [task.prompt.strip(), ""]
    parts.append(f"Define a top-level Python entrypoint named `{task.manifest.entrypoint}`.")
    if task.manifest.signature:
        parts.append(f"Expected signature/usage: {task.manifest.signature}")
    return "\n".join(parts)


class SingleAgentSolver(Solver):
    name = "single_agent"

    def solve(
        self,
        task: Task,
        *,
        model: str,
        deployment: DeploymentAdapter,
        ctx: SolverContext,
    ) -> Candidate:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(task)},
        ]
        text, metrics = deployment.chat(
            model=model,
            messages=messages,
            temperature=ctx.temperature,
            max_tokens=ctx.max_tokens,
            seed=ctx.seed,
        )
        code, ok = extract_code(text, entrypoint=task.manifest.entrypoint)
        return Candidate(
            code=code,
            raw_output=text,
            extraction_ok=ok,
            sample_index=ctx.sample_index,
            finish_reason=None,
            gen_metrics=metrics,
        )
