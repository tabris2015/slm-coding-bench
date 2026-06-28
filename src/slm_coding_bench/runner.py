"""Orchestration: for each (deployment x model x solver x task x sample), generate a candidate
and evaluate the applicable suites, recording results and serving metrics."""

from __future__ import annotations

import platform
from datetime import datetime, timezone

from slm_coding_bench.config import RunConfig
from slm_coding_bench.models import ResultRecord, SuiteStatus, Task
from slm_coding_bench.registry import build_deployment, build_executor, build_solver, build_suites
from slm_coding_bench.results.store import ResultStore, make_run_id
from slm_coding_bench.solvers.base import SolverContext
from slm_coding_bench.tasks.loader import load_tasks
from slm_coding_bench.tasks.manifest import SuiteName

# Suites are evaluated in this order; perf is skipped when test does not pass.
_SUITE_ORDER = [SuiteName.test, SuiteName.parity, SuiteName.perf]


class Runner:
    def __init__(self, config: RunConfig, progress=None) -> None:
        self.config = config
        self.progress = progress or (lambda msg: None)

    def run(self) -> ResultStore:
        cfg = self.config
        run_id = cfg.run_id or make_run_id()
        store = ResultStore(cfg.results_root, run_id)
        store.write_run_manifest(
            config=cfg.model_dump(),
            extra={"host": platform.platform(), "python": platform.python_version()},
        )

        tasks = load_tasks(cfg.tasks_root, cfg.task_glob)
        self.progress(f"loaded {len(tasks)} tasks; run_id={run_id}")

        executor = build_executor(cfg.executor)
        suites = build_suites(cfg.executor)
        solvers = [build_solver(name) for name in cfg.solvers]

        for dep_cfg in cfg.deployments:
            deployment = build_deployment(dep_cfg)
            with deployment:
                if not deployment.health():
                    self.progress(f"[skip] deployment {dep_cfg.name!r} is unhealthy")
                    continue
                for model in dep_cfg.models:
                    self.progress(f"== {dep_cfg.name} :: {model} ==")
                    for solver in solvers:
                        for task in tasks:
                            self._run_task(store, run_id, deployment, dep_cfg.name, model,
                                           solver, task, executor, suites)
                    store.write_serving(deployment.serving_metrics(model))
        self.progress(f"done; results in {store.run_dir}")
        return store

    def _run_task(self, store, run_id, deployment, dep_name, model, solver, task: Task,
                  executor, suites) -> None:
        cfg = self.config
        for sample_index in range(cfg.samples):
            ctx = SolverContext(
                temperature=cfg.temp, max_tokens=cfg.max_tokens,
                seed=cfg.seed, sample_index=sample_index,
            )
            try:
                candidate = solver.solve(task, model=model, deployment=deployment, ctx=ctx)
            except Exception as e:  # generation failure -> record as error, keep going
                self._record(store, run_id, task, model, dep_name, solver.name,
                             SuiteName.test, sample_index, SuiteStatus.error,
                             None, True, None, {"solve_error": str(e)[:500]})
                continue

            run_parity_perf = sample_index == 0 or cfg.parity_perf_on_all_samples
            test_passed = True
            for suite_name in _SUITE_ORDER:
                if not task.applies(suite_name):
                    self._record(store, run_id, task, model, dep_name, solver.name, suite_name,
                                 sample_index, SuiteStatus.not_applicable, None,
                                 candidate.extraction_ok, candidate.gen_metrics, {})
                    continue
                if suite_name in (SuiteName.parity, SuiteName.perf) and not run_parity_perf:
                    continue
                if suite_name == SuiteName.perf and not test_passed:
                    self._record(store, run_id, task, model, dep_name, solver.name, suite_name,
                                 sample_index, SuiteStatus.not_applicable, None,
                                 candidate.extraction_ok, candidate.gen_metrics,
                                 {"reason": "skipped: test did not pass"})
                    continue

                result = suites[suite_name].evaluate(task, candidate, executor)
                if suite_name == SuiteName.test:
                    test_passed = result.status == SuiteStatus.pass_
                self._record(store, run_id, task, model, dep_name, solver.name, suite_name,
                             sample_index, result.status, result.score,
                             candidate.extraction_ok, candidate.gen_metrics, result.detail)

            mark = "[green]✓[/green]" if test_passed else "[red]✗[/red]"
            self.progress(f"  {mark} {task.id} (sample {sample_index})")

    def _record(self, store, run_id, task, model, dep_name, solver_name, suite, sample_index,
                status, score, extraction_ok, gen_metrics, detail) -> None:
        store.write_record(ResultRecord(
            run_id=run_id, task_id=task.id, origin=task.origin, model=model,
            deployment=dep_name, solver=solver_name, suite=suite, sample_index=sample_index,
            status=status, score=score, extraction_ok=extraction_ok,
            gen_metrics=gen_metrics, detail=detail, ts=datetime.now(timezone.utc),
        ))
