"""Multi-agent solver — documented interface stub (planned next phase).

This conforms to the same :class:`Solver` interface as the single-agent solver so it drops into
the runner unchanged once implemented. The intended design (from the project research) is a
heterogeneous, moderately-sparse, verifier-checked graph rather than a flat swarm:

    Planner (e.g. Qwen2.5-Coder-7B)
        -> decompose the task into a short plan
    Coder (e.g. Qwen2.5-Coder-3B)
        -> implement the plan as code (one or few calls)
    Verifier (e.g. Qwen3-1.7B, run as cheap aspect-checkers, majority vote)
        -> run the test/parity suites via the Executor and review;
           on failure, loop back to the Coder with the failing detail (bounded retries).

Edges are deliberately limited (planner<->coder, coder<->verifier) to suppress error
compounding. Each node calls ``deployment.chat()`` with its own model id, so a single
deployment serving all three models (per-request model selection) is sufficient. Tool calls
(run_python/read/write) and constrained decoding are layered in to attack the small-model
tool-reliability cliff.

Implementation is deferred; v1 ships the single-agent baseline and the full benchmark.
"""

from __future__ import annotations

from slm_coding_bench.deployments.base import DeploymentAdapter
from slm_coding_bench.models import Candidate, Task
from slm_coding_bench.solvers.base import Solver, SolverContext


class MultiAgentSolver(Solver):
    name = "multi_agent"

    def __init__(
        self,
        *,
        planner_model: str | None = None,
        coder_model: str | None = None,
        verifier_model: str | None = None,
        max_retries: int = 2,
    ) -> None:
        self.planner_model = planner_model
        self.coder_model = coder_model
        self.verifier_model = verifier_model
        self.max_retries = max_retries

    def solve(
        self,
        task: Task,
        *,
        model: str,
        deployment: DeploymentAdapter,
        ctx: SolverContext,
    ) -> Candidate:
        raise NotImplementedError(
            "MultiAgentSolver is a planned next-phase feature; see module docstring for the "
            "intended planner->coder->verifier design."
        )
