"""Command-line interface for slm-coding-bench."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from slm_coding_bench.config import RunConfig
from slm_coding_bench.results.leaderboard import render_markdown, summarize
from slm_coding_bench.results.store import ResultStore
from slm_coding_bench.runner import Runner
from slm_coding_bench.tasks.loader import load_tasks, validate_tasks

app = typer.Typer(
    add_completion=False,
    help="slm-coding-bench — a small, high-signal coding benchmark for (small) LLMs.",
)
console = Console()


@app.callback()
def _main() -> None:
    """slm-coding-bench."""


@app.command("list-tasks")
def list_tasks(tasks_root: str = typer.Option("tasks", "--tasks-root")) -> None:
    """List discovered tasks and which suites each declares."""
    tasks = load_tasks(tasks_root)
    for t in tasks:
        suites = ",".join(s.value for s in t.manifest.suites)
        console.print(f"[bold]{t.id}[/bold]  ({t.origin})  suites=[{suites}]  -> {t.manifest.title}")
    console.print(f"\n{len(tasks)} tasks")


@app.command("validate-tasks")
def validate(tasks_root: str = typer.Option("tasks", "--tasks-root")) -> None:
    """Validate every task directory; exit non-zero if any are malformed."""
    failures = validate_tasks(tasks_root)
    if not failures:
        console.print("[green]all tasks valid[/green]")
        raise typer.Exit(0)
    for path, err in failures:
        console.print(f"[red]FAIL[/red] {path}\n      {err}")
    console.print(f"\n[red]{len(failures)} task(s) failed validation[/red]")
    raise typer.Exit(1)


@app.command("run")
def run(
    config: Path = typer.Option(..., "-c", "--config", help="YAML run spec"),
    samples: int = typer.Option(None, "--samples", help="override samples per task"),
    temp: float = typer.Option(None, "--temp", help="override temperature"),
    tasks: str = typer.Option(None, "--tasks", help="comma-separated task-id globs"),
    run_id: str = typer.Option(None, "--run-id"),
) -> None:
    """Run the benchmark from a config; writes results and a markdown report."""
    cfg = RunConfig.from_yaml(config)
    cfg = cfg.apply_overrides(
        samples=samples,
        temp=temp,
        task_glob=[g.strip() for g in tasks.split(",")] if tasks else None,
        run_id=run_id,
    )
    store = Runner(cfg, progress=console.print).run()
    _write_report(store, cfg.samples)


@app.command("report")
def report(
    run_id: str = typer.Argument(..., help="run id under results/"),
    results_root: str = typer.Option("results", "--results-root"),
) -> None:
    """Regenerate the markdown report for an existing run."""
    store = ResultStore(results_root, run_id)
    records = store.read_records()
    if not records:
        console.print(f"[red]no records found for run {run_id}[/red]")
        raise typer.Exit(1)
    samples = max((r.sample_index for r in records), default=0) + 1
    path = _write_report(store, samples)
    console.print(path.read_text())


def _write_report(store: ResultStore, samples: int) -> Path:
    summary = summarize(store.read_records(), store.read_serving(), samples)
    md = render_markdown(summary, store.run_id)
    out = store.run_dir / "report.md"
    out.write_text(md)
    console.print(f"[green]report written:[/green] {out}")
    return out


if __name__ == "__main__":
    app()
