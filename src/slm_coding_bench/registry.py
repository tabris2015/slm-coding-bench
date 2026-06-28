"""Factories that turn config into concrete adapters/solvers/executors/suites."""

from __future__ import annotations

import os

from slm_coding_bench.config import DeploymentConfig, ExecutorConfig
from slm_coding_bench.deployments.base import DeploymentAdapter
from slm_coding_bench.deployments.openai_compat import OpenAIDeployment
from slm_coding_bench.executors.base import Executor
from slm_coding_bench.executors.subprocess_exec import SubprocessExecutor
from slm_coding_bench.solvers.base import Solver
from slm_coding_bench.solvers.multi_agent import MultiAgentSolver
from slm_coding_bench.solvers.single_agent import SingleAgentSolver
from slm_coding_bench.suites.parity_suite import ParitySuite
from slm_coding_bench.suites.perf_suite import PerfSuite
from slm_coding_bench.suites.test_suite import TestSuite
from slm_coding_bench.tasks.manifest import SuiteName


def build_deployment(cfg: DeploymentConfig) -> DeploymentAdapter:
    if cfg.kind in ("openai_compat", "mlx_server"):
        if not cfg.base_url:
            raise ValueError(f"deployment {cfg.name!r}: base_url is required")
        api_key = os.environ.get(cfg.api_key_env) if cfg.api_key_env else None
        # mlx_server process-launch is a planned extension; today it behaves as openai_compat
        # pointed at an already-running server.
        return OpenAIDeployment(cfg.base_url, api_key=api_key, name=cfg.name)
    raise ValueError(f"unknown deployment kind: {cfg.kind!r}")


def build_solver(name: str) -> Solver:
    solvers = {
        "single_agent": SingleAgentSolver,
        "multi_agent": MultiAgentSolver,
    }
    if name not in solvers:
        raise ValueError(f"unknown solver: {name!r}")
    return solvers[name]()


def build_executor(cfg: ExecutorConfig) -> Executor:
    if cfg.kind == "subprocess":
        return SubprocessExecutor()
    raise ValueError(f"unknown executor kind: {cfg.kind!r}")


def build_suites(cfg: ExecutorConfig) -> dict[SuiteName, object]:
    return {
        SuiteName.test: TestSuite(timeout_s=cfg.test_timeout_s, mem_limit_mb=cfg.mem_limit_mb),
        SuiteName.parity: ParitySuite(timeout_s=cfg.parity_timeout_s,
                                      mem_limit_mb=cfg.mem_limit_mb),
        SuiteName.perf: PerfSuite(timeout_s=cfg.perf_timeout_s,
                                  mem_limit_mb=cfg.perf_mem_limit_mb),
    }
